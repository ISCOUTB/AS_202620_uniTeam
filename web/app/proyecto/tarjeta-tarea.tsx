"use client";

import { ETIQUETA_PRIORIDAD, type EstadoTarea, type Miembro, type Tarea } from "@/lib/api";
import type { Flujo } from "@/lib/flujo";
import { ETIQUETA_VENCIMIENTO, formatearDia, nombreCorto, vencimiento } from "@/lib/formato";
import { Avatar } from "../componentes/avatar";

interface Props {
  tarea: Tarea;
  flujo: Flujo;
  miembros: Miembro[];
  ocupada: boolean;
  puedeEliminar: boolean;
  alMover: (destino: EstadoTarea) => void;
  alAsignar: (responsable: string) => void;
  alEditar: () => void;
  alEliminar: () => void;
}

/** Una tarea en su columna del tablero, con sus acciones a mano. */
export function TarjetaTarea({
  tarea,
  flujo,
  miembros,
  ocupada,
  puedeEliminar,
  alMover,
  alAsignar,
  alEditar,
  alEliminar,
}: Props) {
  const situacion = tarea.fecha_limite
    ? vencimiento(tarea.fecha_limite, flujo.esFinal(tarea.estado))
    : null;

  return (
    <article className={`tarjeta-tarea prioridad-${tarea.prioridad}${ocupada ? " ocupada" : ""}`}>
      <div className="fila separado">
        <span className={`pastilla ${tarea.prioridad}`}>{ETIQUETA_PRIORIDAD[tarea.prioridad]}</span>
        <div className="fila acciones-icono">
          <button className="icono" onClick={alEditar} disabled={ocupada} aria-label={`Editar «${tarea.titulo}»`} title="Editar">
            ✎
          </button>
          {puedeEliminar && (
            <button
              className="icono peligro"
              onClick={alEliminar}
              disabled={ocupada}
              aria-label={`Eliminar «${tarea.titulo}»`}
              title="Eliminar"
            >
              🗑
            </button>
          )}
        </div>
      </div>

      <h3 className={flujo.esFinal(tarea.estado) ? "hecha" : undefined}>{tarea.titulo}</h3>

      <div className="fila meta">
        {tarea.fecha_limite && (
          <span className={`fecha ${situacion ?? ""}`} title={situacion ? ETIQUETA_VENCIMIENTO[situacion] : undefined}>
            📅 {formatearDia(tarea.fecha_limite)}
            {situacion && situacion !== "a_tiempo" && <strong> · {ETIQUETA_VENCIMIENTO[situacion]}</strong>}
          </span>
        )}
      </div>

      <div className="fila separado pie-tarjeta">
        <label className="responsable">
          {tarea.responsable ? <Avatar usuario={tarea.responsable} tamano={22} /> : <span className="avatar vacio-avatar">?</span>}
          <select
            value={tarea.responsable ?? ""}
            onChange={(e) => e.target.value && alAsignar(e.target.value)}
            disabled={ocupada}
            aria-label="Responsable"
          >
            {!tarea.responsable && <option value="">Sin asignar</option>}
            {miembros.map((m) => (
              <option key={m.usuario} value={m.usuario}>
                {nombreCorto(m.usuario)}
              </option>
            ))}
          </select>
        </label>
        <div className="fila">
          {flujo.siguientes(tarea.estado).map((destino) => {
            const atras = flujo.orden(destino) < flujo.orden(tarea.estado);
            return (
              <button
                key={destino}
                className="secundario pequeno"
                onClick={() => alMover(destino)}
                disabled={ocupada}
                title={`Mover a ${flujo.etiqueta(destino)}`}
              >
                {atras ? "← " : ""}
                {flujo.etiqueta(destino)}
                {atras ? "" : " →"}
              </button>
            );
          })}
        </div>
      </div>
    </article>
  );
}
