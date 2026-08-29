"use client";

import { useSesion } from "@/lib/sesion";

/** Estado de la sesión y acceso al proveedor de identidad. */
export function BarraUsuario() {
  const { usuario, cargado, entrar, salir } = useSesion();

  if (!cargado) return null;

  if (!usuario) {
    return (
      <button onClick={() => void entrar()}>Iniciar sesión</button>
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
