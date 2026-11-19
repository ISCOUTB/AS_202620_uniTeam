import type { Metadata, Viewport } from "next";
import { Fraunces, Manrope } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { BarraUsuario } from "./barra-usuario";
import { Logo } from "./componentes/logo";
import { NavMovil } from "./componentes/nav-movil";
import { Navegacion } from "./componentes/navegacion";
import { ProveedorAvisos } from "@/lib/avisos";
import { ProveedorSesion } from "@/lib/sesion";
import { SelectorTema } from "./componentes/selector-tema";

/**
 * Fraunces para la voz editorial (títulos, cifras grandes) y Manrope para la
 * interfaz. `next/font` las descarga en el build y las sirve desde el mismo
 * sitio: ninguna petición a Google en tiempo de ejecución.
 */
const fraunces = Fraunces({
  subsets: ["latin"],
  display: "swap",
  variable: "--fuente-display",
});

const manrope = Manrope({
  subsets: ["latin"],
  display: "swap",
  variable: "--fuente-ui",
});

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
    { media: "(prefers-color-scheme: light)", color: "#f7f4eb" },
    { media: "(prefers-color-scheme: dark)", color: "#101814" },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" suppressHydrationWarning className={`${fraunces.variable} ${manrope.variable}`}>
      <head>
        <Script id="tema-inicial" strategy="beforeInteractive">
          {`try { var temaGuardado = localStorage.getItem("uniteam-tema"); if (temaGuardado === "light" || temaGuardado === "dark") document.documentElement.dataset.theme = temaGuardado; } catch (_) {}`}
        </Script>
      </head>
      <body>
        <ProveedorSesion>
          <ProveedorAvisos>
            <a className="saltar" href="#contenido">
              Saltar al contenido
            </a>
            <header className="cabecera">
              <div className="cabecera-interior">
                <div className="cabecera-izquierda">
                  <a className="marca" href="/" aria-label="UniTeam, ir a mis proyectos">
                    <Logo />
                    <span className="marca-nombre">UniTeam</span>
                  </a>
                  <Navegacion />
                </div>
                <div className="cabecera-acciones">
                  <SelectorTema />
                  <BarraUsuario />
                </div>
              </div>
            </header>
            <main className="contenido" id="contenido" tabIndex={-1}>
              {children}
            </main>
            <footer className="pie">
              <span className="pie-marca">UniTeam</span>
              <span>Arquitecturas de Software 2026-20 · Universidad Tecnológica de Bolívar</span>
            </footer>
            <NavMovil />
          </ProveedorAvisos>
        </ProveedorSesion>
      </body>
    </html>
  );
}
