"use client";

import { useEffect, useRef, useState } from "react";
import { IconoLuna, IconoSol } from "./iconos";

type Tema = "light" | "dark";
const CLAVE_TEMA = "uniteam-tema";

function leerTemaSistema(): Tema {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function SelectorTema() {
  const [tema, setTema] = useState<Tema>("light");
  const preferenciaManual = useRef(false);

  useEffect(() => {
    let inicial: Tema;
    let manual = false;
    try {
      const guardado = window.localStorage.getItem(CLAVE_TEMA);
      manual = guardado === "light" || guardado === "dark";
      inicial = guardado === "light" || guardado === "dark" ? guardado : leerTemaSistema();
    } catch {
      inicial = leerTemaSistema();
    }
    preferenciaManual.current = manual;
    setTema(inicial);
    if (manual) document.documentElement.dataset.theme = inicial;

    const sistema = window.matchMedia("(prefers-color-scheme: dark)");
    const actualizarDesdeSistema = (evento: MediaQueryListEvent) => {
      if (preferenciaManual.current) return;
      setTema(evento.matches ? "dark" : "light");
    };
    sistema.addEventListener("change", actualizarDesdeSistema);
    return () => sistema.removeEventListener("change", actualizarDesdeSistema);
  }, []);

  function alternar() {
    const nuevo: Tema = tema === "dark" ? "light" : "dark";
    preferenciaManual.current = true;
    setTema(nuevo);
    document.documentElement.dataset.theme = nuevo;
    try {
      window.localStorage.setItem(CLAVE_TEMA, nuevo);
    } catch {
      // La preferencia sigue vigente durante esta sesión aunque el navegador bloquee storage.
    }
  }

  const modoOscuro = tema === "dark";
  const etiqueta = `Activar modo ${modoOscuro ? "claro" : "oscuro"}`;

  return (
    <button
      className="selector-tema"
      type="button"
      role="switch"
      aria-checked={modoOscuro}
      aria-label={etiqueta}
      title={etiqueta}
      onClick={alternar}
    >
      <span className="selector-tema-pista" aria-hidden="true">
        <span className="selector-tema-thumb">
          <span className="selector-tema-icono">
            {modoOscuro ? <IconoLuna tamano={14} /> : <IconoSol tamano={14} />}
          </span>
        </span>
      </span>
      <span className="selector-tema-texto">{modoOscuro ? "Oscuro" : "Claro"}</span>
    </button>
  );
}
