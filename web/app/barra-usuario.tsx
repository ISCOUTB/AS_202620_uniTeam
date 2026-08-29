"use client";

import { useState } from "react";
import { useUsuario } from "@/lib/usuario";

/**
 * Selector de identidad provisional.
 *
 * Mientras no se integra OIDC, el usuario se escribe a mano y viaja en la
 * cabecera `X-Usuario`. No autentica a nadie: solo indica con qué nombre se
 * llama a la API. Quien no pertenezca al proyecto recibirá 403 igualmente.
 */
export function BarraUsuario() {
  const { usuario, cambiar, cargado } = useUsuario();
  const [borrador, escribir] = useState("");

  if (!cargado) return null;

  if (!usuario) {
    return (
      <form
        className="fila"
        onSubmit={(e) => {
          e.preventDefault();
          if (borrador.trim()) cambiar(borrador.trim());
        }}
      >
        <input
          value={borrador}
          onChange={(e) => escribir(e.target.value)}
          placeholder="Tu usuario"
          aria-label="Usuario"
        />
        <button type="submit">Entrar</button>
      </form>
    );
  }

  return (
    <div className="fila">
      <span className="pastilla">{usuario}</span>
      <button className="secundario" onClick={() => cambiar(null)}>
        Cambiar
      </button>
    </div>
  );
}
