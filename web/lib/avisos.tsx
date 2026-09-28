"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";

/**
 * Notificaciones efímeras: confirman lo que se hizo y avisan de lo que falló
 * sin mover la página. Se anuncian a los lectores de pantalla (aria-live).
 */

type Tipo = "exito" | "error" | "info";
interface Aviso {
  id: number;
  tipo: Tipo;
  texto: string;
}

interface Avisos {
  avisar: (texto: string, tipo?: Tipo) => void;
}

const Contexto = createContext<Avisos | null>(null);
let siguiente = 1;

export function ProveedorAvisos({ children }: { children: React.ReactNode }) {
  const [avisos, establecer] = useState<Aviso[]>([]);

  const cerrar = useCallback((id: number) => {
    establecer((lista) => lista.filter((a) => a.id !== id));
  }, []);

  const avisar = useCallback(
    (texto: string, tipo: Tipo = "exito") => {
      const id = siguiente++;
      // Como mucho tres a la vez: más taparían el tablero.
      establecer((lista) => [...lista.slice(-2), { id, tipo, texto }]);
      window.setTimeout(() => cerrar(id), tipo === "error" ? 7000 : 3500);
    },
    [cerrar],
  );

  const valor = useMemo(() => ({ avisar }), [avisar]);

  return (
    <Contexto.Provider value={valor}>
      {children}
      <div className="avisos" aria-live="polite" role="status">
        {avisos.map((a) => (
          <div key={a.id} className={`aviso-flotante ${a.tipo}`}>
            <span>{a.texto}</span>
            <button className="cerrar" aria-label="Cerrar aviso" onClick={() => cerrar(a.id)}>
              ×
            </button>
          </div>
        ))}
      </div>
    </Contexto.Provider>
  );
}

export function useAvisos(): Avisos {
  const avisos = useContext(Contexto);
  if (!avisos) throw new Error("useAvisos debe usarse dentro de <ProveedorAvisos>.");
  return avisos;
}
