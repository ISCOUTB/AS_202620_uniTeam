import type { Progreso } from "@/lib/api";
import type { Flujo } from "@/lib/flujo";
import { AnilloProgreso } from "../componentes/anillo-progreso";

/**
 * El «pulso» del proyecto: cuánto está hecho, cuánto está en curso y qué
 * reclama atención. Es informativo: si la API no responde, no aparece y el
 * tablero sigue sirviendo.
 */
export function ResumenProyecto({ progreso, flujo }: { progreso: Progreso; flujo: Flujo }) {
  const terminadas = progreso.por_estado[flujo.final?.id ?? ""] ?? 0;
  const enCurso = flujo.enCurso.reduce((suma, e) => suma + (progreso.por_estado[e.id] ?? 0), 0);

  return (
    <section className="tarjeta resumen" aria-label="Resumen del proyecto">
      <div className="progreso-cabecera">
        <div>
          <p className="ceja">Avance</p>
          <strong className="progreso-cifra">{progreso.porcentaje_completado}% completado</strong>
          <span className="suave">
            {terminadas} de {progreso.total} tareas
          </span>
        </div>
        <AnilloProgreso porcentaje={progreso.porcentaje_completado} />
      </div>

      <progress
        className="barra fina"
        max={100}
        value={progreso.porcentaje_completado}
        aria-label="Porcentaje de tareas completadas"
      >
        {progreso.porcentaje_completado}%
      </progress>

      <div className="metricas">
        <div className="metrica">
          <div className="valor">{progreso.total}</div>
          <div className="nombre">Tareas</div>
        </div>
        <div className="metrica">
          <div className="valor">{enCurso}</div>
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
  );
}
