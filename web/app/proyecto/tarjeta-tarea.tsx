"use client";

import { ETIQUETA_PRIORIDAD, type EstadoTarea, type Miembro, type Tarea } from "@/lib/api";
import type { Flujo } from "@/lib/flujo";
import { diasHasta, fechaRelativa, formatearDia, nombreCorto, vencimiento } from "@/lib/formato";
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
  alEmpezarArrastre: () => void;
  alTerminarArrastre: () => void;
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
  alEmpezarArrastre,
  alTerminarArrastre,
}: Props) {
  const situacion = tarea.fecha_limite
    ? vencimiento(tarea.fecha_limite, flujo.esFinal(tarea.estado))
    : null;

  return (
    <article
      className={`tarjeta-tarea prioridad-${tarea.prioridad}${ocupada ? " ocupada" : ""}`}
      draggable={!ocupada}
      onDragStart={(e) => {
        e.dataTransfer.setData("text/plain", tarea.id);
        e.dataTransfer.effectAllowed = "move";
        alEmpezarArrastre();
      }}
      onDragEnd={alTerminarArrastre}
    >
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
          <span className={`fecha ${situacion ?? ""}`} title={formatearDia(tarea.fecha_limite)}>
            📅 {textoFecha(tarea.fecha_limite, situacion === "vencida")}
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

/** «Vence mañana», «Venció hace 2 días»; lo lejano, con la fecha: «30 nov 2026». */
function textoFecha(fecha: string, vencida: boolean): string {
  const dias = diasHasta(fecha);
  if (Math.abs(dias) > 14) return formatearDia(fecha);
  const relativa = fechaRelativa(fecha);
  return vencida ? `Venció ${relativa}` : `Vence ${relativa}`;
}
