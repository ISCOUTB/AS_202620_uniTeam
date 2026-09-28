"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  api,
  ErrorApi,
  ETIQUETA_PRIORIDAD,
  obtenerFlujo,
  PESO_PRIORIDAD,
  PRIORIDADES,
  type EstadoTarea,
  type Prioridad,
  type Progreso,
  type Proyecto,
  type Tarea,
} from "@/lib/api";
import { useAvisos } from "@/lib/avisos";
import { Flujo } from "@/lib/flujo";
import { nombreCorto } from "@/lib/formato";
import { useLento } from "@/lib/lento";
import { useSesion } from "@/lib/sesion";
import { GrupoAvatares } from "../componentes/avatar";
import { DialogoTarea, type DatosTarea } from "./dialogo-tarea";
import { PanelMiembros } from "./panel-miembros";
import { TarjetaTarea } from "./tarjeta-tarea";

type Dialogo = { modo: "crear" } | { modo: "editar"; tarea: Tarea } | null;

function mensaje(e: unknown, porDefecto: string): string {
  return e instanceof ErrorApi ? e.message : porDefecto;
}

/** Dentro de cada columna: prioridad alta primero, luego la fecha más cercana. */
function comparar(a: Tarea, b: Tarea): number {
  return (
    PESO_PRIORIDAD[a.prioridad] - PESO_PRIORIDAD[b.prioridad] ||
    (a.fecha_limite ?? "9999").localeCompare(b.fecha_limite ?? "9999") ||
    a.creada_en.localeCompare(b.creada_en)
  );
}

export function Tablero() {
  // El identificador va en la consulta (?id=) y no en la ruta: el sitio se
  // exporta como ficheros estáticos y no puede generar una página por proyecto.
  const id = useSearchParams().get("id") ?? "";
  const { token, usuario, cargado } = useSesion();
  const { avisar } = useAvisos();

  const [proyecto, establecerProyecto] = useState<Proyecto | null>(null);
  const [tareas, establecerTareas] = useState<Tarea[] | null>(null);
  const [progreso, establecerProgreso] = useState<Progreso | null>(null);
  const [flujo, establecerFlujo] = useState<Flujo | null>(null);
  const [error, establecerError] = useState<string | null>(null);

  const [texto, establecerTexto] = useState("");
  const [filtroResponsable, establecerFiltroResponsable] = useState("");
  const [filtroPrioridad, establecerFiltroPrioridad] = useState<Prioridad | "">("");

  const [ocupadas, establecerOcupadas] = useState<Set<string>>(new Set());
  const [dialogo, establecerDialogo] = useState<Dialogo>(null);
  const [guardando, establecerGuardando] = useState(false);
  const [verMiembros, establecerVerMiembros] = useState(false);

  const lento = useLento(token !== null && tareas === null && !error);

  const recargarProgreso = useCallback(async () => {
    if (!token || !id) return;
    try {
      establecerProgreso(await api.progreso(token, id));
    } catch {
      /* el progreso es informativo: si falla, el tablero sigue sirviendo */
    }
  }, [token, id]);

  const recargar = useCallback(async () => {
    if (!token || !id) return;
    try {
      const [p, t, r, f] = await Promise.all([
        api.obtenerProyecto(token, id),
        api.listarTareas(token, id),
        api.progreso(token, id),
        obtenerFlujo(),
      ]);
      establecerFlujo(new Flujo(f));
      establecerProyecto(p);
      establecerTareas(t);
      establecerProgreso(r);
      establecerError(null);
    } catch (e) {
      establecerError(mensaje(e, "No se pudo contactar con la API."));
    }
  }, [token, id]);

  useEffect(() => {
    void recargar();
  }, [recargar]);

  useEffect(() => {
    document.title = proyecto ? `${proyecto.nombre} · UniTeam` : "Proyecto · UniTeam";
  }, [proyecto]);

  const esLider = !!proyecto?.miembros.some((m) => m.usuario === usuario && m.rol === "lider");

  /** Ejecuta una acción sobre una tarea sin permitir un segundo clic mientras dura. */
  async function sobreTarea(tareaId: string, accion: () => Promise<void>) {
    if (ocupadas.has(tareaId)) return;
    establecerOcupadas((s) => new Set(s).add(tareaId));
    try {
      await accion();
    } finally {
      establecerOcupadas((s) => {
        const copia = new Set(s);
        copia.delete(tareaId);
        return copia;
      });
    }
  }

  function reemplazar(tarea: Tarea) {
    establecerTareas((lista) => lista?.map((t) => (t.id === tarea.id ? tarea : t)) ?? lista);
  }

  const mover = (tarea: Tarea, destino: EstadoTarea) =>
    sobreTarea(tarea.id, async () => {
      if (!token) return;
      try {
        reemplazar(await api.cambiarEstado(token, id, tarea.id, destino));
        void recargarProgreso();
      } catch (e) {
        avisar(mensaje(e, "No se pudo cambiar el estado."), "error");
      }
    });

  const asignar = (tarea: Tarea, responsable: string) =>
    sobreTarea(tarea.id, async () => {
      if (!token || responsable === tarea.responsable) return;
      try {
        reemplazar(await api.asignarTarea(token, id, tarea.id, responsable));
        avisar(`Asignada a ${nombreCorto(responsable)}.`);
        void recargarProgreso();
      } catch (e) {
        avisar(mensaje(e, "No se pudo asignar la tarea."), "error");
      }
    });

  const eliminar = (tarea: Tarea) =>
    sobreTarea(tarea.id, async () => {
      if (!token) return;
      if (!window.confirm(`¿Eliminar la tarea «${tarea.titulo}»? No se puede deshacer.`)) return;
      try {
        await api.eliminarTarea(token, id, tarea.id);
        establecerTareas((lista) => lista?.filter((t) => t.id !== tarea.id) ?? lista);
        avisar("Tarea eliminada.");
        void recargarProgreso();
      } catch (e) {
        avisar(mensaje(e, "No se pudo eliminar la tarea."), "error");
      }
    });

  async function guardar(datos: DatosTarea) {
    if (!token || !dialogo) return;
    establecerGuardando(true);
    try {
      if (dialogo.modo === "crear") {
        const nueva = await api.crearTarea(token, id, datos);
        establecerTareas((lista) => [...(lista ?? []), nueva]);
        avisar("Tarea creada.");
      } else {
        const original = dialogo.tarea;
        let resultado = original;
        const cambios: Parameters<typeof api.editarTarea>[3] = {};
        if (datos.titulo !== original.titulo) cambios.titulo = datos.titulo;
        if (datos.prioridad !== original.prioridad) cambios.prioridad = datos.prioridad;
        if (datos.fecha_limite !== original.fecha_limite) cambios.fecha_limite = datos.fecha_limite;
        if (Object.keys(cambios).length > 0) {
          resultado = await api.editarTarea(token, id, original.id, cambios);
        }
        if (datos.responsable && datos.responsable !== original.responsable) {
          resultado = await api.asignarTarea(token, id, original.id, datos.responsable);
        }
        reemplazar(resultado);
        avisar("Cambios guardados.");
      }
      establecerDialogo(null);
      void recargarProgreso();
    } catch (e) {
      avisar(mensaje(e, "No se pudo guardar la tarea."), "error");
    } finally {
      establecerGuardando(false);
    }
  }

  async function agregarMiembro(correo: string): Promise<boolean> {
    if (!token) return false;
    try {
      establecerProyecto(await api.agregarMiembro(token, id, correo));
      avisar(`${correo} ya forma parte del proyecto.`);
      return true;
    } catch (e) {
      avisar(mensaje(e, "No se pudo añadir el integrante."), "error");
      return false;
    }
  }

  const visibles = useMemo(() => {
    const aguja = texto.trim().toLowerCase();
    return (tareas ?? [])
      .filter((t) => !aguja || t.titulo.toLowerCase().includes(aguja))
      .filter((t) => !filtroResponsable || (filtroResponsable === "-" ? !t.responsable : t.responsable === filtroResponsable))
      .filter((t) => !filtroPrioridad || t.prioridad === filtroPrioridad)
      .sort(comparar);
  }, [tareas, texto, filtroResponsable, filtroPrioridad]);

  const filtrando = !!(texto || filtroResponsable || filtroPrioridad);

  if (!cargado) return null;
  if (!token) return <p className="vacio">Inicia sesión para ver este proyecto.</p>;

  if (error && !proyecto) {
    return (
      <>
        <p className="migas">
          <Link href="/">← Mis proyectos</Link>
        </p>
        <div className="aviso error">{error}</div>
      </>
    );
  }

  if (!proyecto || !tareas || !flujo) {
    return (
      <>
        <p className="migas">
          <Link href="/">← Mis proyectos</Link>
        </p>
        <div className="tarjeta esqueleto" style={{ height: 120, marginBottom: 20 }} />
        <div className="kanban">
          {[0, 1, 2].map((i) => (
            <div key={i} className="columna esqueleto" style={{ height: 280 }} />
          ))}
        </div>
        {lento && (
          <p className="vacio">El servidor está despertando; la primera carga del día tarda un poco más.</p>
        )}
      </>
    );
  }

  return (
    <>
      <p className="migas">
        <Link href="/">← Mis proyectos</Link>
      </p>

      <div className="encabezado-pagina">
        <div>
          <h1>{proyecto.nombre}</h1>
          <div className="fila suave">
            <GrupoAvatares usuarios={proyecto.miembros.map((m) => m.usuario)} />
            <button className="enlace" onClick={() => establecerVerMiembros((v) => !v)}>
              {proyecto.miembros.length} integrante{proyecto.miembros.length === 1 ? "" : "s"}
              {verMiembros ? " ▴" : " ▾"}
            </button>
          </div>
        </div>
        <button onClick={() => establecerDialogo({ modo: "crear" })}>+ Nueva tarea</button>
      </div>

      {error && <div className="aviso error">{error}</div>}

      {verMiembros && <PanelMiembros proyecto={proyecto} esLider={esLider} alAgregar={agregarMiembro} />}

      {progreso && (
        <section className="tarjeta resumen">
          <div className="progreso-cabecera">
            <strong>{progreso.porcentaje_completado}% completado</strong>
            <span className="suave">
              {progreso.por_estado[flujo.final?.id ?? ""] ?? 0} de {progreso.total} tareas
            </span>
          </div>
          <div className="barra" role="progressbar" aria-valuenow={progreso.porcentaje_completado} aria-valuemin={0} aria-valuemax={100}>
            <div style={{ width: `${progreso.porcentaje_completado}%` }} />
          </div>
          <div className="metricas">
            <div className="metrica">
              <div className="valor">{progreso.total}</div>
              <div className="nombre">Tareas</div>
            </div>
            <div className="metrica">
              <div className="valor">
                {flujo.enCurso.reduce((suma, e) => suma + (progreso.por_estado[e.id] ?? 0), 0)}
              </div>
              <div className="nombre">En curso</div>
            </div>
            <div className={`metrica${progreso.sin_responsable > 0 ? " atencion" : ""}`}>
              <div className="valor">{progreso.sin_responsable}</div>
              <div className="nombre">Sin responsable</div>
            </div>
            <div className={`metrica${progreso.vencidas > 0 ? " alerta" : ""}`}>
              <div className="valor">{progreso.vencidas}</div>
              <div className="nombre">Vencidas</div>
            </div>
          </div>
        </section>
      )}

      {tareas.length < (progreso?.total ?? 0) && (
        <div className="aviso">
          Se muestran las primeras {tareas.length} de {progreso?.total} tareas: el tablero carga hasta 200 por proyecto.
        </div>
      )}

      <div className="filtros">
        <input
          type="search"
          value={texto}
          onChange={(e) => establecerTexto(e.target.value)}
          placeholder="Buscar tareas…"
          aria-label="Buscar tareas por título"
        />
        <select value={filtroResponsable} onChange={(e) => establecerFiltroResponsable(e.target.value)} aria-label="Filtrar por responsable">
          <option value="">Todos los responsables</option>
          <option value="-">Sin asignar</option>
          {usuario && proyecto.miembros.some((m) => m.usuario === usuario) && <option value={usuario}>Mis tareas</option>}
          {proyecto.miembros
            .filter((m) => m.usuario !== usuario)
            .map((m) => (
              <option key={m.usuario} value={m.usuario}>
                {nombreCorto(m.usuario)}
              </option>
            ))}
        </select>
        <select value={filtroPrioridad} onChange={(e) => establecerFiltroPrioridad(e.target.value as Prioridad | "")} aria-label="Filtrar por prioridad">
          <option value="">Todas las prioridades</option>
          {PRIORIDADES.map((p) => (
            <option key={p} value={p}>
              {ETIQUETA_PRIORIDAD[p]}
            </option>
          ))}
        </select>
        {filtrando && (
          <button
            className="enlace"
            onClick={() => {
              establecerTexto("");
              establecerFiltroResponsable("");
              establecerFiltroPrioridad("");
            }}
          >
            Quitar filtros
          </button>
        )}
      </div>

      {tareas.length === 0 ? (
        <div className="vacio-grande">
          <h2>El tablero está vacío</h2>
          <p>Crea la primera tarea y asígnasela a alguien del equipo.</p>
          <button onClick={() => establecerDialogo({ modo: "crear" })}>Crear la primera tarea</button>
        </div>
      ) : (
        <div className="kanban" style={{ "--columnas": flujo.estados.length } as React.CSSProperties}>
          {flujo.estados.map(({ id: estado, etiqueta }) => {
            const columna = visibles.filter((t) => t.estado === estado);
            return (
              <section key={estado} className={`columna columna-${flujo.tipo(estado)}`} aria-label={etiqueta}>
                <header>
                  <h2>{etiqueta}</h2>
                  <span className="contador">{columna.length}</span>
                </header>
                {columna.length === 0 ? (
                  <p className="vacio-columna">{filtrando ? "Nada coincide con los filtros." : "Sin tareas."}</p>
                ) : (
                  columna.map((t) => (
                    <TarjetaTarea
                      key={t.id}
                      tarea={t}
                      flujo={flujo}
                      miembros={proyecto.miembros}
                      ocupada={ocupadas.has(t.id)}
                      puedeEliminar={esLider || t.creada_por === usuario}
                      alMover={(destino) => void mover(t, destino)}
                      alAsignar={(r) => void asignar(t, r)}
                      alEditar={() => establecerDialogo({ modo: "editar", tarea: t })}
                      alEliminar={() => void eliminar(t)}
                    />
                  ))
                )}
              </section>
            );
          })}
        </div>
      )}

      {dialogo && (
        <DialogoTarea
          tarea={dialogo.modo === "editar" ? dialogo.tarea : undefined}
          miembros={proyecto.miembros}
          guardando={guardando}
          alGuardar={guardar}
          alCerrar={() => !guardando && establecerDialogo(null)}
        />
      )}
    </>
  );
}
