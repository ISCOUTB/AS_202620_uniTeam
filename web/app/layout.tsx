import type { Metadata } from "next";
import "./globals.css";
import { BarraUsuario } from "./barra-usuario";
import { ProveedorUsuario } from "@/lib/usuario";

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
        <ProveedorUsuario>
          <header className="cabecera">
            <div className="cabecera-interior">
              <a className="marca" href="/">
                UniTeam <span>Gestión de tareas de equipo</span>
              </a>
              <BarraUsuario />
            </div>
          </header>
          <main className="contenido">{children}</main>
        </ProveedorUsuario>
      </body>
    </html>
  );
}
