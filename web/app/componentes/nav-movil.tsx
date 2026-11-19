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

/**
 * Navegación inferior para pantallas estrechas. En escritorio la cabecera ya
 * lleva las pestañas; esta barra aparece solo por debajo del punto de corte y
 * ofrece las mismas rutas, al alcance del pulgar.
 */
export function NavMovil() {
  const { token } = useSesion();
  const ruta = usePathname() ?? "/";
  if (!token) return null;

  return (
    <nav className="nav-movil" aria-label="Secciones">
      {SECCIONES.map(({ href, etiqueta, Icono, activa }) => (
        <Link
          key={href}
          href={href}
          className={activa(ruta) ? "activa" : undefined}
          aria-current={activa(ruta) ? "page" : undefined}
        >
          <Icono tamano={22} />
          <span>{etiqueta}</span>
        </Link>
      ))}
    </nav>
  );
}
