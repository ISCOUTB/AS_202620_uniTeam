"use client";

import { useEffect, useRef, useState } from "react";
import {
  ETIQUETA_PRIORIDAD,
  PRIORIDADES,
  type Miembro,
  type Prioridad,
  type Tarea,
} from "@/lib/api";
import { nombreCorto } from "@/lib/formato";

export interface DatosTarea {
  titulo: string;
  prioridad: Prioridad;
  responsable: string | null;
  fecha_limite: string | null;
}

interface Props {
  /** Si viene una tarea, se edita; si no, se crea. */
  tarea?: Tarea;
  miembros: Miembro[];
  guardando: boolean;
  /** Motivo del último fallo al guardar, para mostrarlo dentro del diálogo. */
  error?: string | null;
  alGuardar: (datos: DatosTarea) => void;
  alCerrar: () => void;
}

/** Diálogo modal para crear o editar una tarea. Escape y Cancelar lo cierran. */
export function DialogoTarea({ tarea, miembros, guardando, error, alGuardar, alCerrar }: Props) {
  const [titulo, establecerTitulo] = useState(tarea?.titulo ?? "");
  const [prioridad, establecerPrioridad] = useState<Prioridad>(tarea?.prioridad ?? "media");
  const [responsable, establecerResponsable] = useState(tarea?.responsable ?? "");
  const [fecha, establecerFecha] = useState(tarea?.fecha_limite ?? "");
  const dialogo = useRef<HTMLDialogElement>(null);
  const primerCampo = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Quien abrió el diálogo lo recupera al cerrarlo: sin esto, el foco vuelve
    // al principio del documento y el teclado pierde el hilo.
    const anterior = document.activeElement as HTMLElement | null;
    if (!dialogo.current?.open) dialogo.current?.showModal();
    primerCampo.current?.focus();
    return () => anterior?.focus?.();
  }, []);

  function enviar(e: React.FormEvent) {
    e.preventDefault();
    if (!titulo.trim() || guardando) return;
    alGuardar({
      titulo: titulo.trim(),
      prioridad,
      responsable: responsable || null,
      fecha_limite: fecha || null,
    });
  }

  let textoGuardar = "Crear tarea";
  if (guardando) textoGuardar = "Guardando…";
  else if (tarea) textoGuardar = "Guardar cambios";

  return (
    <dialog
      ref={dialogo}
      className="fondo-modal"
      aria-labelledby="titulo-dialogo"
      aria-describedby="descripcion-dialogo"
      onCancel={(e) => {
        e.preventDefault();
        if (!guardando) alCerrar();
      }}
    >
      <div className="modal">
        <form onSubmit={enviar}>
          <div className="modal-cabecera">
            <div>
              <p className="ceja">{tarea ? "Editar" : "Nueva"}</p>
              <h2 id="titulo-dialogo">{tarea ? "Editar tarea" : "Nueva tarea"}</h2>
            </div>
          </div>
          <p className="ayuda" id="descripcion-dialogo">
            El título es obligatorio. Prioridad, responsable y fecha puedes cambiarlos después.
          </p>

          <label className="campo">
            <span className="etiqueta">Título</span>
            <input
              ref={primerCampo}
              value={titulo}
              onChange={(e) => establecerTitulo(e.target.value)}
              placeholder="Redactar la sección 7 de arc42"
              maxLength={300}
              required
            />
          </label>

          <div className="campos">
            <fieldset className="campo">
              <legend className="etiqueta">Prioridad</legend>
              <div className="segmentado">
                {PRIORIDADES.map((p) => (
                  <label
                    key={p}
                    className={`segmento prioridad-${p}${prioridad === p ? " activo" : ""}`}
                  >
                    <input
                      type="radio"
                      name="prioridad"
                      value={p}
                      checked={prioridad === p}
                      onChange={() => establecerPrioridad(p)}
                    />
                    <span>{ETIQUETA_PRIORIDAD[p]}</span>
                  </label>
                ))}
              </div>
            </fieldset>

            <label className="campo">
              <span className="etiqueta">Responsable</span>
              <select value={responsable} onChange={(e) => establecerResponsable(e.target.value)}>
                {/* La API asigna, pero no des-asigna: una tarea con responsable
                    cambia de responsable, no se queda sin él. */}
                {!tarea?.responsable && <option value="">Sin asignar</option>}
                {miembros.map((m) => (
                  <option key={m.usuario} value={m.usuario}>
                    {nombreCorto(m.usuario)}
                  </option>
                ))}
              </select>
            </label>

            <label className="campo">
              <span className="etiqueta">Fecha límite</span>
              <input type="date" value={fecha} onChange={(e) => establecerFecha(e.target.value)} />
            </label>
          </div>

          <div className="acciones">
            <button type="button" className="secundario" onClick={alCerrar} disabled={guardando}>
              Cancelar
            </button>
            <button type="submit" disabled={guardando || !titulo.trim()}>
              {textoGuardar}
            </button>
          </div>

          {error && (
            <p className="aviso error" role="alert">
              {error}
            </p>
          )}
        </form>
      </div>
    </dialog>
  );
}
