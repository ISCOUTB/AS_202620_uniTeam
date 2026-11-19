import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Página no encontrada · UniTeam",
};

/**
 * Página para una dirección que no existe. Reutiliza el lenguaje de los estados
 * vacíos: explica qué pasó y devuelve al usuario a un lugar con contenido.
 */
export default function NoEncontrado() {
  return (
    <div className="vacio-grande no-encontrado">
      <span className="ceja">Error 404</span>
      <h1>Esta página no está en el tablero</h1>
      <p>
        La dirección que abriste no existe o cambió de sitio. Tus proyectos y tus tareas siguen donde
        estaban.
      </p>
      <Link className="boton" href="/">
        Volver a mis proyectos
      </Link>
    </div>
  );
}
