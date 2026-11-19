/** Marca de UniTeam: una «U» que contiene al equipo. La misma del favicon. */
export function Logo({ tamano = 28 }: { tamano?: number }) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <rect width="32" height="32" rx="9" fill="var(--primario)" />
      <path
        d="M9 9v8.5a7 7 0 0 0 14 0V9"
        fill="none"
        stroke="var(--sobre-primario)"
        strokeWidth="3.2"
        strokeLinecap="round"
      />
      <circle cx="16" cy="17.5" r="2.2" fill="var(--acento)" />
    </svg>
  );
}
