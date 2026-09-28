import type { Metadata, Viewport } from "next";
import "./globals.css";
import { BarraUsuario } from "./barra-usuario";
import { Logo } from "./componentes/logo";
import { Navegacion } from "./componentes/navegacion";
import { ProveedorAvisos } from "@/lib/avisos";
import { ProveedorSesion } from "@/lib/sesion";

export const metadata: Metadata = {
  title: "UniTeam",
  description: "Gestión colaborativa de tareas para equipos universitarios.",
  // Instalable como aplicación de escritorio desde Chrome o Edge (restricción
  // T2: web y/o escritorio), sin escribir una aplicación nativa.
  manifest: "/manifest.webmanifest",
  applicationName: "UniTeam",
  appleWebApp: { capable: true, title: "UniTeam", statusBarStyle: "default" },
  icons: { apple: "/apple-touch-icon.png" },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#161b22" },
  ],
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
                <div className="fila cabecera-izquierda">
                  <a className="marca" href="/">
                    <Logo />
                    <span className="marca-nombre">UniTeam</span>
                  </a>
                  <Navegacion />
                </div>
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
