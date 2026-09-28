/**
 * Formato de fechas y nombres para la interfaz.
 *
 * Las fechas límite son días, no instantes: «2026-11-30» es el 30 de
 * noviembre en cualquier zona horaria. Por eso se comparan como texto contra
 * la fecha **local** de hoy, nunca contra `toISOString()`, que da la fecha en
 * UTC y desde las 19:00 en Colombia ya es mañana.
 */

export function hoyLocal(): string {
  const d = new Date();
  const dos = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${dos(d.getMonth() + 1)}-${dos(d.getDate())}`;
}

const FORMATO_DIA = new Intl.DateTimeFormat("es-CO", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

/** «2026-11-30» → «30 nov 2026», sin desplazarse de día por la zona horaria. */
export function formatearDia(iso: string): string {
  const [a, m, d] = iso.split("-").map(Number);
  return FORMATO_DIA.format(new Date(a, m - 1, d));
}

export type Vencimiento = "vencida" | "hoy" | "pronto" | "a_tiempo";

/** Situación de una fecha límite respecto a hoy. «Pronto» son los 3 días siguientes. */
export function vencimiento(fecha: string, completada: boolean): Vencimiento | null {
  if (completada) return null;
  const hoy = hoyLocal();
  if (fecha < hoy) return "vencida";
  if (fecha === hoy) return "hoy";
  const [a, m, d] = hoy.split("-").map(Number);
  const limite = new Date(a, m - 1, d + 3);
  const tope = `${limite.getFullYear()}-${String(limite.getMonth() + 1).padStart(2, "0")}-${String(limite.getDate()).padStart(2, "0")}`;
  return fecha <= tope ? "pronto" : "a_tiempo";
}

export const ETIQUETA_VENCIMIENTO: Record<Vencimiento, string> = {
  vencida: "Vencida",
  hoy: "Vence hoy",
  pronto: "Vence pronto",
  a_tiempo: "",
};

/** Nombre corto para mostrar: la parte del correo antes de la arroba. */
export function nombreCorto(usuario: string): string {
  return usuario.split("@")[0];
}

/** Hasta dos iniciales: «ana.perez@utb.edu.co» → «AP». */
export function iniciales(usuario: string): string {
  const partes = nombreCorto(usuario).split(/[._\-\s]+/).filter(Boolean);
  const letras = partes.length > 1 ? partes[0][0] + partes[1][0] : nombreCorto(usuario).slice(0, 2);
  return letras.toUpperCase();
}

/** Un tono estable por persona, para distinguir avatares sin configurar nada. */
export function tono(usuario: string): number {
  let h = 0;
  for (const c of usuario) h = (h * 31 + c.charCodeAt(0)) % 360;
  return h;
}
