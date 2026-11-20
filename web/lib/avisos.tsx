"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { IconoAlerta, IconoCheck, IconoCerrar, IconoInfo } from "@/app/componentes/iconos";

/**
 * Notificaciones efímeras: confirman lo que se hizo y avisan de lo que falló
 * sin mover la página. Cada aviso se anuncia por su cuenta —cortés si es un
 * éxito, urgente si es un error— y se detiene mientras el puntero o el foco
 * están encima, para que nadie pierda un «Deshacer».
 */

type Tipo = "exito" | "error" | "info";

/** Un botón dentro del aviso, como «Deshacer». */
export interface AccionAviso {
  etiqueta: string;
  alPulsar: () => void;
}

interface Aviso {
  id: number;
  tipo: Tipo;
  texto: string;
  accion?: AccionAviso;
  duracion: number;
}

interface Avisos {
  avisar: (texto: string, tipo?: Tipo, accion?: AccionAviso, duracionMs?: number) => void;
}

const Contexto = createContext<Avisos | null>(null);
let siguiente = 1;

const ICONOS: Record<Tipo, typeof IconoCheck> = {
  exito: IconoCheck,
  error: IconoAlerta,
  info: IconoInfo,
};

function AvisoFlotante({ aviso, cerrar }: { aviso: Aviso; cerrar: (id: number) => void }) {
  const [pausado, establecerPausado] = useState(false);
  const restante = useRef(aviso.duracion);
  const desde = useRef(0);
  const temporizador = useRef<number | undefined>(undefined);

  const programar = useCallback(
    (ms: number) => {
      window.clearTimeout(temporizador.current);
      desde.current = Date.now();
      temporizador.current = window.setTimeout(() => cerrar(aviso.id), ms);
    },
    [aviso.id, cerrar],
  );

  useEffect(() => {
    programar(restante.current);
    return () => window.clearTimeout(temporizador.current);
  }, [programar]);

  function pausar() {
    if (pausado) return;
    window.clearTimeout(temporizador.current);
    restante.current = Math.max(900, restante.current - (Date.now() - desde.current));
    establecerPausado(true);
  }

  function reanudar() {
    if (!pausado) return;
    establecerPausado(false);
    programar(restante.current);
  }

  const Icono = ICONOS[aviso.tipo];

  return (
    <div
      className={`aviso-flotante ${aviso.tipo}${pausado ? " pausado" : ""}`}
      style={{ "--duracion": `${aviso.duracion}ms` } as React.CSSProperties}
      role={aviso.tipo === "error" ? "alert" : "status"}
      aria-atomic="true"
      onMouseEnter={pausar}
      onMouseLeave={reanudar}
      onFocus={pausar}
      onBlur={reanudar}
    >
      <span className="aviso-icono" aria-hidden="true">
        <Icono tamano={18} />
      </span>
      <span className="aviso-texto">{aviso.texto}</span>
      {aviso.accion && (
        <button
          className="enlace accion-aviso"
          onClick={() => {
            aviso.accion?.alPulsar();
            cerrar(aviso.id);
          }}
        >
          {aviso.accion.etiqueta}
        </button>
      )}
      <button className="cerrar" aria-label="Cerrar aviso" onClick={() => cerrar(aviso.id)}>
        <IconoCerrar tamano={15} />
      </button>
      <span className="aviso-barra" aria-hidden="true" />
    </div>
  );
}

export function ProveedorAvisos({ children }: { children: React.ReactNode }) {
  const [avisos, establecer] = useState<Aviso[]>([]);

  const cerrar = useCallback((id: number) => {
    establecer((lista) => lista.filter((a) => a.id !== id));
  }, []);

  const avisar = useCallback(
    (texto: string, tipo: Tipo = "exito", accion?: AccionAviso, duracionMs?: number) => {
      const id = siguiente++;
      const duracion = duracionMs ?? (tipo === "error" ? 7000 : 3500);
      // Como mucho tres a la vez: más taparían el tablero.
      establecer((lista) => [...lista.slice(-2), { id, tipo, texto, accion, duracion }]);
    },
    [],
  );

  const valor = useMemo(() => ({ avisar }), [avisar]);

  return (
    <Contexto.Provider value={valor}>
      {children}
      <div className="avisos">
        {avisos.map((a) => (
          <AvisoFlotante key={a.id} aviso={a} cerrar={cerrar} />
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
