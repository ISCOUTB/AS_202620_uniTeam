"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { completarSesion } from "@/lib/oidc";
import { useSesion } from "@/lib/sesion";

function Canje() {
  const parametros = useSearchParams();
  const router = useRouter();
  const { refrescar } = useSesion();
  const [error, establecerError] = useState<string | null>(null);

  useEffect(() => {
    const codigo = parametros.get("code");
    const estado = parametros.get("state");
    const fallo = parametros.get("error");

    if (fallo) {
      // OIDC acompaña el código de error con una descripción legible
      // (RFC 6749 §4.1.2.1); sin ella no hay forma de saber qué rechazó.
      const detalle = parametros.get("error_description");
      establecerError(
        `El proveedor de identidad devolvió: ${fallo}${detalle ? ` — ${detalle}` : ""}`,
      );
      return;
    }
    if (!codigo || !estado) {
      establecerError("La respuesta del proveedor no trae código ni estado.");
      return;
    }

    completarSesion(codigo, estado)
      .then(() => {
        refrescar();
        router.replace("/");
      })
      .catch((e) => establecerError(e instanceof Error ? e.message : String(e)));
  }, [parametros, router, refrescar]);

  if (error) {
    return (
      <>
        <h1>No se pudo iniciar sesión</h1>
        <div className="aviso error">{error}</div>
      </>
    );
  }
  return <p className="vacio">Completando el inicio de sesión…</p>;
}

export default function PaginaCallback() {
  return (
    <Suspense fallback={<p className="vacio">Cargando…</p>}>
      <Canje />
    </Suspense>
  );
}
