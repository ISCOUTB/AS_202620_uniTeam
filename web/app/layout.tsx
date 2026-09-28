import type { Metadata } from "next";
import "./globals.css";
import { BarraUsuario } from "./barra-usuario";
import { Logo } from "./componentes/logo";
import { ProveedorAvisos } from "@/lib/avisos";
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
          <ProveedorAvisos>
            <header className="cabecera">
              <div className="cabecera-interior">
                <a className="marca" href="/">
                  <Logo />
                  <span className="marca-nombre">UniTeam</span>
                </a>
                <BarraUsuario />
              </div>
            </header>
            <main className="contenido">{children}</main>
            <footer className="pie">
              UniTeam · Arquitecturas de Software 2026-20 · Universidad Tecnológica de Bolívar
            </footer>
          </ProveedorAvisos>
        </ProveedorSesion>
      </body>
    </html>
  );
}
