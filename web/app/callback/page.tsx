"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { completarSesion } from "@/lib/oidc";
import { useSesion } from "@/lib/sesion";
import { IconoAlerta } from "../componentes/iconos";

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
      const sufijo = detalle ? ` — ${detalle}` : "";
      establecerError(`El proveedor de identidad devolvió: ${fallo}${sufijo}`);
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
      <div className="callback">
        <div className="tarjeta callback-tarjeta">
          <span className="callback-icono error" aria-hidden="true">
            <IconoAlerta tamano={22} />
          </span>
          <h1>No se pudo iniciar sesión</h1>
          <div className="aviso error" role="alert">
            {error}
          </div>
          <Link className="boton" href="/">
            Volver al inicio
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="callback">
      <div className="tarjeta callback-tarjeta" role="status" aria-live="polite">
        <span className="cargador" aria-hidden="true" />
        <h1>Completando el inicio de sesión…</h1>
        <p className="ayuda">Estamos comprobando tu cuenta con el proveedor de identidad.</p>
      </div>
    </div>
  );
}

export default function PaginaCallback() {
  useEffect(() => {
    document.title = "Iniciando sesión · UniTeam";
  }, []);

  return (
    <Suspense
      fallback={
        <div className="callback">
          <div className="tarjeta callback-tarjeta" role="status">
            <span className="cargador" aria-hidden="true" />
            <p className="ayuda">Cargando…</p>
          </div>
        </div>
      }
    >
      <Canje />
    </Suspense>
  );
}
