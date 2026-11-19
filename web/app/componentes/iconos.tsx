/**
 * Iconografía de UniTeam.
 *
 * Un solo set, dibujado a mano, con el mismo trazo y la misma rejilla de 24 px.
 * Sustituye a los emoji del prototipo: cada sistema operativo dibujaba los
 * suyos y el tablero cambiaba de aspecto según la máquina. Todos heredan el
 * color del texto (`currentColor`) y son decorativos por defecto: la etiqueta
 * accesible la pone siempre el control que los contiene.
 */

interface PropsIcono {
  tamano?: number;
  className?: string;
}

function Svg({
  tamano = 20,
  className,
  children,
}: PropsIcono & { children: React.ReactNode }) {
  return (
    <svg
      width={tamano}
      height={tamano}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      className={className}
    >
      {children}
    </svg>
  );
}

export function IconoMas(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="M12 5v14M5 12h14" />
    </Svg>
  );
}

export function IconoBuscar(p: PropsIcono) {
  return (
    <Svg {...p}>
      <circle cx="11" cy="11" r="6.5" />
      <path d="m16 16 4 4" />
    </Svg>
  );
}

export function IconoCalendario(p: PropsIcono) {
  return (
    <Svg {...p}>
      <rect x="3.5" y="5" width="17" height="15.5" rx="3" />
      <path d="M8 3v4M16 3v4M3.5 10h17" />
    </Svg>
  );
}

export function IconoLapiz(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="M4 20h4l10.5-10.5a2.1 2.1 0 0 0-3-3L5 17v3Z" />
      <path d="m13.5 6.5 3 3" />
    </Svg>
  );
}

export function IconoPapelera(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="M4 7h16M9.5 7V4.8A1.8 1.8 0 0 1 11.3 3h1.4a1.8 1.8 0 0 1 1.8 1.8V7" />
      <path d="M6.5 7l.8 12a2 2 0 0 0 2 1.9h5.4a2 2 0 0 0 2-1.9l.8-12" />
      <path d="M10.5 11v6M13.5 11v6" />
    </Svg>
  );
}

export function IconoFlechaIzquierda(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="M19 12H5M11 6l-6 6 6 6" />
    </Svg>
  );
}

export function IconoFlechaDerecha(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="M5 12h14M13 6l6 6-6 6" />
    </Svg>
  );
}

export function IconoChevronAbajo(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="m6 9 6 6 6-6" />
    </Svg>
  );
}

export function IconoChevronArriba(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="m6 15 6-6 6 6" />
    </Svg>
  );
}

export function IconoUsuarios(p: PropsIcono) {
  return (
    <Svg {...p}>
      <circle cx="9" cy="8" r="3.2" />
      <path d="M3.5 19.5c0-3 2.5-5 5.5-5s5.5 2 5.5 5" />
      <path d="M16 5.4a3 3 0 0 1 0 5.9M17.5 14.8c1.9.6 3 2.3 3 4.7" />
    </Svg>
  );
}

export function IconoSalir(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="M14 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4" />
      <path d="M10 8l-4 4 4 4M6 12h9" />
    </Svg>
  );
}

export function IconoSol(p: PropsIcono) {
  return (
    <Svg {...p}>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </Svg>
  );
}

export function IconoLuna(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="M20.5 13.5A8.5 8.5 0 0 1 10.5 3.5a8.5 8.5 0 1 0 10 10Z" />
    </Svg>
  );
}

export function IconoCerrar(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="M6 6l12 12M18 6 6 18" />
    </Svg>
  );
}

export function IconoDeshacer(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="M4 8h10a5 5 0 0 1 0 10H8" />
      <path d="M8 4 4 8l4 4" />
    </Svg>
  );
}

export function IconoArrastrar(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="M9 6h.01M15 6h.01M9 12h.01M15 12h.01M9 18h.01M15 18h.01" strokeWidth="2.5" />
    </Svg>
  );
}

export function IconoAlerta(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="M12 4.5 21 20H3L12 4.5Z" />
      <path d="M12 10v4.5M12 17.5h.01" />
    </Svg>
  );
}

export function IconoReloj(p: PropsIcono) {
  return (
    <Svg {...p}>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7.5V12l3 2" />
    </Svg>
  );
}

export function IconoTablero(p: PropsIcono) {
  return (
    <Svg {...p}>
      <rect x="3.5" y="4" width="17" height="16" rx="3" />
      <path d="M9.5 4v16M15 8h2.5M15 12h2.5M15 16h2.5" />
    </Svg>
  );
}

export function IconoBandeja(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="M3.5 13.5 6 5.5A2 2 0 0 1 8 4h8a2 2 0 0 1 2 1.5l2.5 8" />
      <path d="M3.5 13.5h4l1.5 2.5h6l1.5-2.5h4v4a2.5 2.5 0 0 1-2.5 2.5h-12a2.5 2.5 0 0 1-2.5-2.5v-4Z" />
    </Svg>
  );
}

export function IconoCheck(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="m5 12.5 4.5 4.5L19 7" />
    </Svg>
  );
}

export function IconoInfo(p: PropsIcono) {
  return (
    <Svg {...p}>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 11v5M12 8h.01" />
    </Svg>
  );
}

export function IconoFiltro(p: PropsIcono) {
  return (
    <Svg {...p}>
      <path d="M4 6h16M7 12h10M10 18h4" />
    </Svg>
  );
}
