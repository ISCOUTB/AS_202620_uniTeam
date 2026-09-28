"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api, ErrorApi, ETIQUETA_PRIORIDAD, obtenerFlujo, type MiTarea } from "@/lib/api";
import { Flujo } from "@/lib/flujo";
import { diasHasta, fechaRelativa, formatearDia } from "@/lib/formato";
import { useLento } from "@/lib/lento";
import { useSesion } from "@/lib/sesion";
import { Portada } from "../componentes/portada";

/** Grupos por urgencia, como en las bandejas de Asana o Todoist. */
const GRUPOS = [
  { id: "vencidas", titulo: "Vencidas", de: (d: number | null) => d !== null && d < 0 },
  { id: "hoy", titulo: "Hoy", de: (d: number | null) => d === 0 },
  { id: "semana", titulo: "Próximos 7 días", de: (d: number | null) => d !== null && d > 0 && d <= 7 },
  { id: "despues", titulo: "Más adelante", de: (d: number | null) => d !== null && d > 7 },
  { id: "sin_fecha", titulo: "Sin fecha", de: (d: number | null) => d === null },
] as const;

export default function PaginaMisTareas() {
  const { token, cargado } = useSesion();
  const [tareas, establecerTareas] = useState<MiTarea[] | null>(null);
  const [flujo, establecerFlujo] = useState<Flujo | null>(null);
  const [error, establecerError] = useState<string | null>(null);
  const [terminadas, establecerTerminadas] = useState(false);
  const lento = useLento(token !== null && tareas === null && !error);

  useEffect(() => {
    document.title = "Mis tareas · UniTeam";
  }, []);

  useEffect(() => {
    if (!token) return;
    establecerTareas(null);
    Promise.all([api.misTareas(token, terminadas), obtenerFlujo()])
      .then(([t, f]) => {
        establecerTareas(t);
        establecerFlujo(new Flujo(f));
        establecerError(null);
      })
      .catch((e) => establecerError(e instanceof ErrorApi ? e.message : "No se pudo contactar con la API."));
  }, [token, terminadas]);

  const grupos = useMemo(
    () =>
      GRUPOS.map((g) => ({
        ...g,
        tareas: (tareas ?? []).filter((t) => g.de(t.fecha_limite ? diasHasta(t.fecha_limite) : null)),
      })).filter((g) => g.tareas.length > 0),
    [tareas],
  );

  if (!cargado) return null;
  if (!token) return <Portada />;

  return (
    <>
      <div className="encabezado-pagina">
        <div>
          <h1>Mis tareas</h1>
          <p className="subtitulo">Lo que tienes asignado en todos tus proyectos, de lo más urgente a lo menos.</p>
        </div>
        <label className="fila interruptor">
          <input type="checkbox" checked={terminadas} onChange={(e) => establecerTerminadas(e.target.checked)} />
          Mostrar terminadas
        </label>
      </div>

      {error && <div className="aviso error">{error}</div>}

      {tareas === null && !error ? (
        <>
          {[0, 1, 2].map((i) => (
            <div key={i} className="tarjeta esqueleto" style={{ height: 64, marginBottom: 10 }} />
          ))}
          {lento && <p className="vacio">El servidor está despertando; la primera carga del día tarda un poco más.</p>}
        </>
      ) : tareas && tareas.length === 0 ? (
        <div className="vacio-grande">
          <h2>No tienes nada pendiente</h2>
          <p>Cuando alguien de tu equipo te asigne una tarea, aparecerá aquí.</p>
          <Link href="/">Ir a mis proyectos</Link>
        </div>
      ) : (
        grupos.map((g) => (
          <section key={g.id} className={`grupo-tareas grupo-${g.id}`}>
            <h2>
              {g.titulo} <span className="contador">{g.tareas.length}</span>
            </h2>
            <ul className="lista-tareas">
              {g.tareas.map((t) => (
                <li key={t.id} className={`fila-tarea prioridad-${t.prioridad}`}>
                  <div className="fila-tarea-principal">
                    <Link href={`/proyecto/?id=${encodeURIComponent(t.proyecto_id)}`} className="titulo-tarea">
                      {t.titulo}
                    </Link>
                    <span className="suave">{t.proyecto_nombre}</span>
                  </div>
                  <div className="fila">
                    <span className={`pastilla ${t.prioridad}`}>{ETIQUETA_PRIORIDAD[t.prioridad]}</span>
                    {flujo && <span className="pastilla estado">{flujo.etiqueta(t.estado)}</span>}
                    {t.fecha_limite && (
                      <span className="fecha-relativa" title={formatearDia(t.fecha_limite)}>
                        {fechaRelativa(t.fecha_limite)}
                      </span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </section>
        ))
      )}
    </>
  );
}
