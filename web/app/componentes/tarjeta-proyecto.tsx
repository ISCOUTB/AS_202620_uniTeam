import Link from "next/link";
import type { ProyectoConResumen } from "@/lib/api";
import { GrupoAvatares } from "./avatar";
import { IconoFlechaDerecha } from "./iconos";

/** Tarjeta de un proyecto en «Mis proyectos»: avance, equipo y vencimientos. */
export function TarjetaProyecto({
  proyecto,
  usuario,
}: {
  proyecto: ProyectoConResumen;
  usuario: string | null;
}) {
  const lider = proyecto.miembros.find((m) => m.rol === "lider")?.usuario === usuario;
  const porcentaje = proyecto.resumen.total
    ? Math.round((proyecto.resumen.terminadas * 100) / proyecto.resumen.total)
    : 0;

  return (
    <Link
      href={`/proyecto/?id=${encodeURIComponent(proyecto.id)}`}
      className="tarjeta tarjeta-proyecto"
    >
      <div className="fila separado">
        <strong className="titulo-proyecto">{proyecto.nombre}</strong>
        {lider && <span className="insignia">Líder</span>}
      </div>

      <div className="avance-proyecto">
        <div className="fila separado suave">
          <span>
            {proyecto.resumen.total === 0
              ? "Sin tareas todavía"
              : `${proyecto.resumen.terminadas} de ${proyecto.resumen.total} tareas terminadas`}
          </span>
          {proyecto.resumen.vencidas > 0 && (
            <span className="vencidas-proyecto">
              {proyecto.resumen.vencidas} vencida{proyecto.resumen.vencidas === 1 ? "" : "s"}
            </span>
          )}
        </div>
        <div className="barra fina" aria-hidden="true">
          <div style={{ width: `${porcentaje}%` }} />
        </div>
      </div>

      <div className="fila separado pie-tarjeta">
        <GrupoAvatares usuarios={proyecto.miembros.map((m) => m.usuario)} />
        <span className="suave tarjeta-proyecto-pie">
          {proyecto.miembros.length} integrante{proyecto.miembros.length === 1 ? "" : "s"}
          <IconoFlechaDerecha tamano={16} />
        </span>
      </div>
    </Link>
  );
}
