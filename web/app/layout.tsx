import type { Metadata } from "next";
import "./globals.css";
import { BarraUsuario } from "./barra-usuario";
import { ProveedorSesion } from "@/lib/sesion";

export const metadata: Metadata = {
  title: "UniTeam",
  description: "Gestión colaborativa de tareas para equipos universitarios.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>
        <ProveedorSesion>
          <header className="cabecera">
            <div className="cabecera-interior">
              <a className="marca" href="/">
                UniTeam <span>Gestión de tareas de equipo</span>
              </a>
              <BarraUsuario />
            </div>
          </header>
          <main className="contenido">{children}</main>
        </ProveedorSesion>
      </body>
    </html>
  );
}
