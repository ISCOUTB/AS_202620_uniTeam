"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  api,
  ErrorApi,
  ETIQUETA_ESTADO,
  TRANSICIONES,
  type EstadoTarea,
  type Prioridad,
  type Progreso,
  type Proyecto,
  type Tarea,
} from "@/lib/api";
import { useSesion } from "@/lib/sesion";

const ESTADOS: EstadoTarea[] = ["pendiente", "en_progreso", "completada"];
const PRIORIDADES: Prioridad[] = ["baja", "media", "alta"];

function estaVencida(t: Tarea): boolean {
  if (!t.fecha_limite || t.estado === "completada") return false;
  return t.fecha_limite < new Date().toISOString().slice(0, 10);
}

export default function PaginaTablero() {
  const { id } = useParams<{ id: string }>();
  const { token, cargado } = useSesion();

  const [proyecto, establecerProyecto] = useState<Proyecto | null>(null);
  const [tareas, establecerTareas] = useState<Tarea[]>([]);
  const [progreso, establecerProgreso] = useState<Progreso | null>(null);
  const [error, establecerError] = useState<string | null>(null);
  const [filtroEstado, establecerFiltroEstado] = useState<EstadoTarea | "">("");
  const [filtroResponsable, establecerFiltroResponsable] = useState("");

  const [titulo, establecerTitulo] = useState("");
  const [prioridad, establecerPrioridad] = useState<Prioridad>("media");
  const [responsable, establecerResponsable] = useState("");
  const [fechaLimite, establecerFechaLimite] = useState("");

  const recargar = useCallback(async () => {
    if (!token || !id) return;
    try {
      const [p, t, r] = await Promise.all([
        api.obtenerProyecto(token, id),
        api.listarTareas(token, id, {
          estado: filtroEstado || undefined,
          responsable: filtroResponsable || undefined,
        }),
        api.progreso(token, id),
      ]);
      establecerProyecto(p);
      establecerTareas(t);
      establecerProgreso(r);
      establecerError(null);
    } catch (e) {
      establecerError(
        e instanceof ErrorApi ? e.message : "No se pudo contactar con la API.",
      );
    }
  }, [token, id, filtroEstado, filtroResponsable]);

  useEffect(() => {
    void recargar();
  }, [recargar]);

  async function crearTarea(evento: React.FormEvent) {
    evento.preventDefault();
    if (!token || !titulo.trim()) return;
    try {
      await api.crearTarea(token, id, {
        titulo: titulo.trim(),
        prioridad,
        responsable: responsable || null,
        fecha_limite: fechaLimite || null,
      });
      establecerTitulo("");
      establecerResponsable("");
      establecerFechaLimite("");
      await recargar();
    } catch (e) {
      establecerError(
        e instanceof ErrorApi ? e.message : "No se pudo crear la tarea.",
      );
    }
  }

  async function mover(tarea: Tarea, estado: EstadoTarea) {
    if (!token) return;
    try {
      await api.cambiarEstado(token, id, tarea.id, estado);
      await recargar();
    } catch (e) {
      establecerError(
        e instanceof ErrorApi ? e.message : "No se pudo cambiar el estado.",
      );
    }
  }

  if (!cargado) return null;
  if (!token)
    return <p className="vacio">Inicia sesión para ver este proyecto.</p>;

  if (error && !proyecto) {
    return (
      <>
        <p style={{ marginBottom: 16 }}>
          <Link href="/">← Volver a mis proyectos</Link>
        </p>
        <div className="aviso error">{error}</div>
      </>
    );
  }

  return (
    <>
      <p style={{ marginBottom: 16 }}>
        <Link href="/">← Volver a mis proyectos</Link>
      </p>

      <h1>{proyecto?.nombre ?? "Proyecto"}</h1>
      <p className="subtitulo">
        {proyecto?.miembros.length ?? 0} integrante
        {(proyecto?.miembros.length ?? 0) === 1 ? "" : "s"}
      </p>

      {error && <div className="aviso error">{error}</div>}

      {progreso && (
        <section className="tarjeta" style={{ marginBottom: 24 }}>
          <div className="metricas">
            <div className="metrica">
              <div className="valor">{progreso.total}</div>
              <div className="nombre">Tareas</div>
            </div>
            <div className="metrica">
              <div className="valor">{progreso.porcentaje_completado}%</div>
              <div className="nombre">Completado</div>
            </div>
            <div className="metrica">
              <div className="valor">{progreso.sin_responsable}</div>
              <div className="nombre">Sin responsable</div>
            </div>
            <div className="metrica">
              <div className="valor">{progreso.vencidas}</div>
              <div className="nombre">Vencidas</div>
            </div>
          </div>
          <div className="barra" style={{ marginTop: 14 }}>
            <div style={{ width: `${progreso.porcentaje_completado}%` }} />
          </div>
        </section>
      )}

      <h2>Nueva tarea</h2>
      <section className="tarjeta">
        <form onSubmit={crearTarea}>
          <div className="fila">
            <div style={{ flex: "3 1 240px" }}>
              <label className="etiqueta" htmlFor="titulo">Título</label>
              <input
                id="titulo"
                value={titulo}
                onChange={(e) => establecerTitulo(e.target.value)}
                placeholder="Redactar la sección 5"
                style={{ width: "100%" }}
                required
              />
            </div>
            <div>
              <label className="etiqueta" htmlFor="prioridad">Prioridad</label>
              <select
                id="prioridad"
                value={prioridad}
                onChange={(e) => establecerPrioridad(e.target.value as Prioridad)}
              >
                {PRIORIDADES.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="etiqueta" htmlFor="responsable">Responsable</label>
              <select
                id="responsable"
                value={responsable}
                onChange={(e) => establecerResponsable(e.target.value)}
              >
                <option value="">Sin asignar</option>
                {proyecto?.miembros.map((m) => (
                  <option key={m.usuario} value={m.usuario}>{m.usuario}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="etiqueta" htmlFor="fecha">Fecha límite</label>
              <input
                id="fecha"
                type="date"
                value={fechaLimite}
                onChange={(e) => establecerFechaLimite(e.target.value)}
              />
            </div>
            <button type="submit" style={{ alignSelf: "flex-end" }}>Crear</button>
          </div>
        </form>
      </section>

      <h2>Tablero</h2>
      <div className="fila" style={{ marginBottom: 12 }}>
        <select
          value={filtroEstado}
          onChange={(e) => establecerFiltroEstado(e.target.value as EstadoTarea | "")}
          aria-label="Filtrar por estado"
        >
          <option value="">Todos los estados</option>
          {ESTADOS.map((e) => (
            <option key={e} value={e}>{ETIQUETA_ESTADO[e]}</option>
          ))}
        </select>
        <select
          value={filtroResponsable}
          onChange={(e) => establecerFiltroResponsable(e.target.value)}
          aria-label="Filtrar por responsable"
        >
          <option value="">Todos los responsables</option>
          {proyecto?.miembros.map((m) => (
            <option key={m.usuario} value={m.usuario}>{m.usuario}</option>
          ))}
        </select>
      </div>

      <section className="tarjeta">
        {tareas.length === 0 ? (
          <p className="vacio">No hay tareas que coincidan.</p>
        ) : (
          <table className="tabla">
            <thead>
              <tr>
                <th>Tarea</th>
                <th>Estado</th>
                <th>Prioridad</th>
                <th>Responsable</th>
                <th>Fecha límite</th>
                <th>Mover a</th>
              </tr>
            </thead>
            <tbody>
              {tareas.map((t) => (
                <tr key={t.id}>
                  <td>{t.titulo}</td>
                  <td>
                    <span className={`pastilla ${t.estado}`}>
                      {ETIQUETA_ESTADO[t.estado]}
                    </span>
                  </td>
                  <td><span className={`pastilla ${t.prioridad}`}>{t.prioridad}</span></td>
                  <td>{t.responsable ?? <span className="pastilla">sin asignar</span>}</td>
                  <td>
                    {t.fecha_limite ? (
                      estaVencida(t) ? (
                        <span className="pastilla vencida">{t.fecha_limite}</span>
                      ) : (
                        t.fecha_limite
                      )
                    ) : (
                      "—"
                    )}
                  </td>
                  <td>
                    <div className="fila">
                      {TRANSICIONES[t.estado].map((destino) => (
                        <button
                          key={destino}
                          className="secundario"
                          onClick={() => mover(t, destino)}
                        >
                          {ETIQUETA_ESTADO[destino]}
                        </button>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </>
  );
}
