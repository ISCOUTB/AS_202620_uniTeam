/**
 * Anillo de progreso dibujado con SVG.
 *
 * `pathLength={100}` deja el trazo normalizado: el desplazamiento es
 * directamente `100 - porcentaje`, sin trigonometría ni cálculos de radio.
 * El porcentaje se anuncia una sola vez, en el texto que lo acompaña.
 */
export function AnilloProgreso({
  porcentaje,
  tamano = 76,
}: {
  porcentaje: number;
  tamano?: number;
}) {
  const valor = Math.max(0, Math.min(100, Math.round(porcentaje)));
  return (
    <svg
      className="anillo"
      width={tamano}
      height={tamano}
      viewBox="0 0 64 64"
      aria-hidden="true"
      focusable="false"
    >
      <circle className="anillo-fondo" cx="32" cy="32" r="27" pathLength={100} />
      <circle
        className="anillo-valor"
        cx="32"
        cy="32"
        r="27"
        pathLength={100}
        strokeDasharray="100"
        strokeDashoffset={100 - valor}
      />
    </svg>
  );
}
