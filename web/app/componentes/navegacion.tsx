"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSesion } from "@/lib/sesion";

const SECCIONES = [
  { href: "/", etiqueta: "Proyectos", activa: (ruta: string) => ruta === "/" || ruta.startsWith("/proyecto") },
  { href: "/mis-tareas/", etiqueta: "Mis tareas", activa: (ruta: string) => ruta.startsWith("/mis-tareas") },
];

/** Pestañas principales. Solo con sesión: sin ella, la portada es la única página. */
export function Navegacion() {
  const { token } = useSesion();
  const ruta = usePathname() ?? "/";
  if (!token) return null;
  return (
    <nav className="navegacion" aria-label="Secciones">
      {SECCIONES.map((s) => (
        <Link key={s.href} href={s.href} className={s.activa(ruta) ? "activa" : undefined} aria-current={s.activa(ruta) ? "page" : undefined}>
          {s.etiqueta}
        </Link>
      ))}
    </nav>
  );
}
