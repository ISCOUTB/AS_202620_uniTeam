"use client";

import { useState } from "react";
import { EMISOR } from "@/lib/oidc";
import { useSesion } from "@/lib/sesion";

/** Estado de la sesión y acceso al proveedor de identidad. */
export function BarraUsuario() {
  const { usuario, cargado, entrar, salir } = useSesion();
  const [error, establecerError] = useState<string | null>(null);
  const [yendo, establecerYendo] = useState(false);

  if (!cargado) return null;

  if (!usuario) {
    // Un fallo al contactar con el proveedor no puede quedar en silencio: el
    // botón no haría nada y no habría forma de saber por qué. Se muestra el
    // emisor configurado, que es lo primero que hay que comprobar.
    const iniciar = () => {
      establecerError(null);
      establecerYendo(true);
      entrar().catch((e: unknown) => {
        establecerYendo(false);
        const motivo = e instanceof Error ? e.message : String(e);
        establecerError(`No se pudo iniciar sesión con ${EMISOR}. ${motivo}`);
        console.error("Inicio de sesión fallido", { emisor: EMISOR, error: e });
      });
    };

    return (
      <div className="fila">
        {error && (
          <span className="error" role="alert">
            {error}
          </span>
        )}
        <button onClick={iniciar} disabled={yendo}>
          {yendo ? "Conectando…" : "Iniciar sesión"}
        </button>
      </div>
    );
  }

  return (
    <div className="fila">
      <span className="pastilla">{usuario}</span>
      <button className="secundario" onClick={salir}>
        Cerrar sesión
      </button>
    </div>
  );
}
