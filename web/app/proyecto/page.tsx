"use client";

import { Suspense } from "react";
import { Tablero } from "./tablero";

// useSearchParams exige un límite de Suspense en una exportación estática.
export default function PaginaTablero() {
  return (
    <Suspense fallback={<p className="vacio">Cargando…</p>}>
      <Tablero />
    </Suspense>
  );
}
