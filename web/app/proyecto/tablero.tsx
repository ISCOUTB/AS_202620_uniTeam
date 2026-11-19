"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  API,
  api,
  ErrorApi,
  notificarSesionCaducada,
  obtenerFlujo,
  PESO_PRIORIDAD,
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
import { EstadoVacio } from "../componentes/estado-vacio";
import {
  IconoChevronAbajo,
  IconoChevronArriba,
  IconoFlechaIzquierda,
  IconoMas,
} from "../componentes/iconos";
import { DialogoTarea, type DatosTarea } from "./dialogo-tarea";
import { FiltrosTablero } from "./filtros-tablero";
import { PanelMiembros } from "./panel-miembros";
import { ResumenProyecto } from "./resumen-proyecto";
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
  const [errorDialogo, establecerErrorDialogo] = useState<string | null>(null);
  const [verMiembros, establecerVerMiembros] = useState(false);
  const [arrastrada, establecerArrastrada] = useState<Tarea | null>(null);
  const [rapida, establecerRapida] = useState("");
  const [creandoRapida, establecerCreandoRapida] = useState(false);
  const busqueda = useRef<HTMLInputElement>(null);
  /** Borrados en espera de «Deshacer»: el DELETE sale cuando vence el plazo. */
  const borrados = useRef(new Map<string, { temporizador: number; ejecutar: (alSalir?: boolean) => void }>());

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
    if (!token || !id) return;

    let detenido = false;
    let socket: WebSocket | null = null;
    let temporizador: number | undefined;
    let reintento = 0;

    const conectar = () => {
      if (detenido) return;
      const url = new URL(
        `${API}/proyectos/${encodeURIComponent(id)}/eventos`,
        window.location.href,
      );
      url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
      socket = new WebSocket(url);

      socket.onopen = () => {
        socket?.send(JSON.stringify({ tipo: "autenticar", token }));
      };
      socket.onmessage = (evento) => {
        let mensaje: { tipo?: string; proyecto_id?: string };
        try {
          mensaje = JSON.parse(evento.data) as { tipo?: string; proyecto_id?: string };
        } catch {
          return;
        }
        if (mensaje.tipo === "conectado") {
          reintento = 0;
          void recargar();
        } else if (
          mensaje.tipo === "tareas_actualizadas" &&
          mensaje.proyecto_id === id
        ) {
          void recargar();
        }
      };
      socket.onclose = (evento) => {
        if (detenido) return;
        if (evento.code === 4401) {
          notificarSesionCaducada();
          return;
        }
        if (evento.code === 4403) {
          void recargar();
          return;
        }
        const espera = Math.min(1000 * 2 ** reintento, 30_000);
        reintento += 1;
        temporizador = window.setTimeout(conectar, espera);
      };
    };

    conectar();
    return () => {
      detenido = true;
      if (temporizador !== undefined) window.clearTimeout(temporizador);
      socket?.close();
    };
  }, [token, id, recargar]);

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

  const mover = (tarea: Tarea, destino: string) =>
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

  /**
   * Eliminar con «Deshacer», como Gmail o Todoist: la tarjeta desaparece al
   * instante y el borrado real sale a los 6 s si nadie se arrepiente. Borrar
   * deja de ser un error irrecuperable (ESC-02) sin preguntar «¿seguro?».
   */
  function eliminar(tarea: Tarea) {
    if (!token) return;
    establecerTareas((lista) => lista?.filter((t) => t.id !== tarea.id) ?? lista);

    const restaurar = () =>
      establecerTareas((lista) => (lista && !lista.some((t) => t.id === tarea.id) ? [...lista, tarea] : lista));

    const ejecutar = (alSalir = false) => {
      borrados.current.delete(tarea.id);
      api
        .eliminarTarea(token, id, tarea.id, alSalir)
        .then(() => void recargarProgreso())
        .catch((e) => {
          restaurar();
          avisar(mensaje(e, "No se pudo eliminar la tarea."), "error");
        });
    };

    const temporizador = window.setTimeout(() => ejecutar(), 6000);
    borrados.current.set(tarea.id, { temporizador, ejecutar });
    avisar(
      `«${tarea.titulo}» eliminada.`,
      "info",
      {
        etiqueta: "Deshacer",
        alPulsar: () => {
          window.clearTimeout(temporizador);
          borrados.current.delete(tarea.id);
          restaurar();
        },
      },
      6000,
    );
  }

  // Si se sale de la página con borrados en espera, se ejecutan ya: salir no
  // equivale a deshacer. `keepalive` deja terminar la petición al cerrar.
  useEffect(() => {
    const pendientes = borrados.current;
    const vaciar = () => {
      for (const { temporizador, ejecutar } of pendientes.values()) {
        window.clearTimeout(temporizador);
        ejecutar(true);
      }
    };
    window.addEventListener("pagehide", vaciar);
    return () => {
      window.removeEventListener("pagehide", vaciar);
      vaciar();
    };
  }, []);

  async function crearRapida(evento: React.FormEvent) {
    evento.preventDefault();
    const titulo = rapida.trim();
    if (!token || !titulo || creandoRapida) return;
    establecerCreandoRapida(true);
    try {
      const nueva = await api.crearTarea(token, id, { titulo, prioridad: "media" });
      establecerTareas((lista) => [...(lista ?? []), nueva]);
      establecerRapida("");
      void recargarProgreso();
    } catch (e) {
      avisar(mensaje(e, "No se pudo crear la tarea."), "error");
    } finally {
      establecerCreandoRapida(false);
    }
  }

  // Atajos de teclado, como en Linear: «N» nueva tarea, «/» buscar.
  useEffect(() => {
    const tecla = (e: KeyboardEvent) => {
      const destino = e.target as HTMLElement;
      if (dialogo || e.metaKey || e.ctrlKey || e.altKey) return;
      if (destino.closest("input, textarea, select, [contenteditable]")) return;
      if (e.key === "n" || e.key === "N") {
        e.preventDefault();
        establecerDialogo({ modo: "crear" });
      } else if (e.key === "/") {
        e.preventDefault();
        busqueda.current?.focus();
      }
    };
    window.addEventListener("keydown", tecla);
    return () => window.removeEventListener("keydown", tecla);
  }, [dialogo]);

  async function guardar(datos: DatosTarea) {
    if (!token || !dialogo) return;
    establecerGuardando(true);
    establecerErrorDialogo(null);
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
      // El diálogo modal deja el resto del documento inerte, así que el aviso
      // flotante no llegaría al lector de pantalla: el error se muestra dentro.
      const texto = mensaje(e, "No se pudo guardar la tarea.");
      establecerErrorDialogo(texto);
      avisar(texto, "error");
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
          <Link href="/">
            <IconoFlechaIzquierda tamano={16} /> Mis proyectos
          </Link>
        </p>
        <h1>No se pudo cargar el proyecto</h1>
        <div className="aviso error" role="alert">
          {error}
        </div>
      </>
    );
  }

  if (!proyecto || !tareas || !flujo) {
    return (
      <>
        <p className="migas">
          <Link href="/">
            <IconoFlechaIzquierda tamano={16} /> Mis proyectos
          </Link>
        </p>
        <h1 className="solo-lectores">Cargando el proyecto</h1>
        <div className="tarjeta esqueleto" style={{ height: 120, marginBottom: 20 }} />
        <div className="kanban" aria-hidden="true">
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
        <Link href="/">
          <IconoFlechaIzquierda tamano={16} /> Mis proyectos
        </Link>
      </p>

      <div className="encabezado-pagina">
        <div>
          <p className="ceja">Proyecto</p>
          <h1>{proyecto.nombre}</h1>
          <div className="fila suave cabecera-miembros">
            <GrupoAvatares usuarios={proyecto.miembros.map((m) => m.usuario)} />
            <button
              className="enlace"
              onClick={() => establecerVerMiembros((v) => !v)}
              aria-expanded={verMiembros}
              aria-controls="panel-miembros"
            >
              {proyecto.miembros.length} integrante{proyecto.miembros.length === 1 ? "" : "s"}
              {verMiembros ? <IconoChevronArriba tamano={15} /> : <IconoChevronAbajo tamano={15} />}
            </button>
          </div>
        </div>
        <button onClick={() => establecerDialogo({ modo: "crear" })} title="Atajo: N">
          <IconoMas tamano={18} />
          Nueva tarea
          <kbd className="atajo" aria-hidden="true">
            N
          </kbd>
        </button>
      </div>

      {error && (
        <div className="aviso error" role="alert">
          {error}
        </div>
      )}

      {verMiembros && <PanelMiembros proyecto={proyecto} esLider={esLider} alAgregar={agregarMiembro} />}

      {progreso && <ResumenProyecto progreso={progreso} flujo={flujo} />}

      {tareas.length < (progreso?.total ?? 0) && (
        <div className="aviso">
          Se muestran las primeras {tareas.length} de {progreso?.total} tareas: el tablero carga hasta 200 por proyecto.
        </div>
      )}

      <FiltrosTablero
        texto={texto}
        alCambiarTexto={establecerTexto}
        responsable={filtroResponsable}
        alCambiarResponsable={establecerFiltroResponsable}
        prioridad={filtroPrioridad}
        alCambiarPrioridad={establecerFiltroPrioridad}
        miembros={proyecto.miembros}
        usuario={usuario}
        filtrando={filtrando}
        alLimpiar={() => {
          establecerTexto("");
          establecerFiltroResponsable("");
          establecerFiltroPrioridad("");
        }}
        refBusqueda={busqueda}
      />

      {tareas.length === 0 ? (
        <EstadoVacio
          titulo="El tablero está vacío"
          ilustracion="tablero"
          accion={
            <button onClick={() => establecerDialogo({ modo: "crear" })}>
              <IconoMas tamano={18} />
              Crear la primera tarea
            </button>
          }
        >
          Crea la primera tarea y asígnasela a alguien del equipo.
        </EstadoVacio>
      ) : (
        <div className="kanban" style={{ "--columnas": flujo.estados.length } as React.CSSProperties}>
          {flujo.estados.map(({ id: estado, etiqueta }) => {
            const columna = visibles.filter((t) => t.estado === estado);
            // Mientras se arrastra, cada columna dice si admite la tarea: solo
            // las transiciones que el flujo permite.
            const admite = !!arrastrada && flujo.siguientes(arrastrada.estado).includes(estado);
            let zona = "";
            if (arrastrada && admite) zona = " destino-valido";
            else if (arrastrada && arrastrada.estado !== estado) zona = " destino-invalido";
            return (
              <section
                key={estado}
                className={`columna columna-${flujo.tipo(estado)}${zona}`}
                aria-label={etiqueta}
                onDragOver={(e) => {
                  if (admite) {
                    e.preventDefault();
                    e.dataTransfer.dropEffect = "move";
                  }
                }}
                onDrop={(e) => {
                  e.preventDefault();
                  if (arrastrada && admite) void mover(arrastrada, estado);
                  establecerArrastrada(null);
                }}
              >
                <header>
                  <h2>
                    <span className="columna-punto" aria-hidden="true" />
                    {etiqueta}
                  </h2>
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
                      alEliminar={() => eliminar(t)}
                      alEmpezarArrastre={() => establecerArrastrada(t)}
                      alTerminarArrastre={() => establecerArrastrada(null)}
                    />
                  ))
                )}
                {flujo.tipo(estado) === "inicial" && (
                  <form onSubmit={crearRapida} className="alta-rapida">
                    <input
                      value={rapida}
                      onChange={(e) => establecerRapida(e.target.value)}
                      placeholder="+ Añadir una tarea"
                      aria-label="Título de la nueva tarea"
                      maxLength={300}
                      disabled={creandoRapida}
                    />
                    <button
                      type="submit"
                      className="icono"
                      aria-label="Añadir tarea"
                      disabled={!rapida.trim() || creandoRapida}
                    >
                      <IconoMas tamano={17} />
                    </button>
                  </form>
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
          error={errorDialogo}
          alGuardar={guardar}
          alCerrar={() => {
            if (guardando) return;
            establecerDialogo(null);
            establecerErrorDialogo(null);
          }}
        />
      )}
    </>
  );
}
