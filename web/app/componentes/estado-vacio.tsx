import type { ReactNode } from "react";

type Ilustracion = "proyecto" | "tablero" | "bandeja";

interface Props {
  titulo: string;
  children: ReactNode;
  accion?: ReactNode;
  ilustracion?: Ilustracion;
}

/**
 * Estado vacío ilustrado. Un vacío no es un error: explica qué falta y cuál es
 * el siguiente paso, con un dibujo de línea en vez de una caja gris.
 */
export function EstadoVacio({ titulo, children, accion, ilustracion = "bandeja" }: Props) {
  return (
    <div className="vacio-grande">
      <div className={`vacio-ilustracion vacio-ilustracion-${ilustracion}`} aria-hidden="true">
        {ilustracion === "proyecto" && (
          <svg viewBox="0 0 96 72" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <rect x="10" y="12" width="40" height="48" rx="6" />
            <rect x="54" y="24" width="32" height="36" rx="6" />
            <path d="M18 24h24M18 34h18M18 44h22" />
            <path d="M62 38h16M62 46h10" />
            <circle cx="50" cy="60" r="8" fill="var(--superficie)" />
            <path d="M50 56v8M46 60h8" />
          </svg>
        )}
        {ilustracion === "tablero" && (
          <svg viewBox="0 0 96 72" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <rect x="8" y="10" width="24" height="52" rx="5" />
            <rect x="36" y="10" width="24" height="52" rx="5" />
            <rect x="64" y="10" width="24" height="52" rx="5" />
            <path d="M14 20h12M14 30h12M14 40h8" />
            <path d="M42 20h12M42 30h12M42 40h8" />
            <path d="M70 20h12M70 30h12" />
          </svg>
        )}
        {ilustracion === "bandeja" && (
          <svg viewBox="0 0 96 72" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 38 22 18a6 6 0 0 1 5.6-4h40.8A6 6 0 0 1 74 18l8 20" />
            <path d="M14 38h16l4 8h28l4-8h16v14a8 8 0 0 1-8 8H22a8 8 0 0 1-8-8V38Z" />
            <path d="M34 28h28M38 36h20" />
          </svg>
        )}
      </div>
      <h2>{titulo}</h2>
      <p>{children}</p>
      {accion}
    </div>
  );
}
