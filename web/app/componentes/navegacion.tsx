"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSesion } from "@/lib/sesion";
import { IconoBandeja, IconoTablero } from "./iconos";

const SECCIONES = [
  {
    href: "/",
    etiqueta: "Proyectos",
    Icono: IconoTablero,
    activa: (ruta: string) => ruta === "/" || ruta.startsWith("/proyecto"),
  },
  {
    href: "/mis-tareas/",
    etiqueta: "Mis tareas",
    Icono: IconoBandeja,
    activa: (ruta: string) => ruta.startsWith("/mis-tareas"),
  },
];

/** Pestañas principales. Solo con sesión: sin ella, la portada es la única página. */
export function Navegacion() {
  const { token } = useSesion();
  const ruta = usePathname() ?? "/";
  if (!token) return null;
  return (
    <nav className="navegacion" aria-label="Secciones">
      {SECCIONES.map(({ href, etiqueta, Icono, activa }) => (
        <Link
          key={href}
          href={href}
          className={activa(ruta) ? "activa" : undefined}
          aria-current={activa(ruta) ? "page" : undefined}
        >
          <Icono tamano={17} />
          <span>{etiqueta}</span>
        </Link>
      ))}
    </nav>
  );
}
