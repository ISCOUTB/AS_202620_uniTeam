"use client";

import { useState } from "react";
import type { Proyecto } from "@/lib/api";
import { pareceCorreo } from "@/lib/lento";
import { Avatar } from "../componentes/avatar";

interface Props {
  proyecto: Proyecto;
  esLider: boolean;
  alAgregar: (correo: string) => Promise<boolean>;
}

/** Integrantes del proyecto. Solo el líder puede añadir (ESC-03). */
export function PanelMiembros({ proyecto, esLider, alAgregar }: Props) {
  const [correo, establecerCorreo] = useState("");
  const [enviando, establecerEnviando] = useState(false);
  const limpio = correo.trim().toLowerCase();
  const valido = pareceCorreo(limpio);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    if (!valido || enviando) return;
    establecerEnviando(true);
    if (await alAgregar(limpio)) establecerCorreo("");
    establecerEnviando(false);
  }

  return (
    <section className="tarjeta panel-miembros">
      <h2>Integrantes</h2>
      <ul className="lista-miembros">
        {proyecto.miembros.map((m) => (
          <li key={m.usuario}>
            <Avatar usuario={m.usuario} />
            <span className="correo">{m.usuario}</span>
            {m.rol === "lider" && <span className="insignia">Líder</span>}
          </li>
        ))}
      </ul>
      {esLider ? (
        <form onSubmit={enviar} className="fila">
          <input
            value={correo}
            onChange={(e) => establecerCorreo(e.target.value)}
            placeholder="correo@utb.edu.co"
            aria-label="Correo del nuevo integrante"
            aria-invalid={correo !== "" && !valido}
            style={{ flex: 1, minWidth: 0 }}
          />
          <button type="submit" disabled={!valido || enviando}>
            {enviando ? "Añadiendo…" : "Añadir"}
          </button>
        </form>
      ) : (
        <p className="ayuda">Solo el líder del proyecto puede añadir integrantes.</p>
      )}
    </section>
  );
}
