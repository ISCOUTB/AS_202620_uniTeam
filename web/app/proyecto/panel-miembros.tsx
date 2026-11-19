"use client";

import { useState } from "react";
import type { Proyecto } from "@/lib/api";
import { pareceCorreo } from "@/lib/lento";
import { Avatar } from "../componentes/avatar";
import { IconoMas, IconoUsuarios } from "../componentes/iconos";

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
  const invalido = correo.trim() !== "" && !valido;

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    if (!valido || enviando) return;
    establecerEnviando(true);
    if (await alAgregar(limpio)) establecerCorreo("");
    establecerEnviando(false);
  }

  return (
    <section id="panel-miembros" className="tarjeta panel-miembros" aria-label="Integrantes del proyecto">
      <h2>
        <IconoUsuarios tamano={18} />
        Integrantes
      </h2>
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
        <>
          <form onSubmit={enviar} className="fila anadir-miembro">
            <input
              type="email"
              autoComplete="email"
              inputMode="email"
              value={correo}
              onChange={(e) => establecerCorreo(e.target.value)}
              placeholder="correo@utb.edu.co"
              aria-label="Correo del nuevo integrante"
              aria-invalid={invalido}
              aria-describedby={invalido ? "error-miembro" : undefined}
              style={{ flex: 1, minWidth: 0 }}
            />
            <button type="submit" disabled={!valido || enviando}>
              <IconoMas tamano={16} />
              {enviando ? "Añadiendo…" : "Añadir"}
            </button>
          </form>
          {invalido && (
            <p className="ayuda error" id="error-miembro">
              Escribe un correo completo, como ana@utb.edu.co.
            </p>
          )}
        </>
      ) : (
        <p className="ayuda">Solo el líder del proyecto puede añadir integrantes.</p>
      )}
    </section>
  );
}
