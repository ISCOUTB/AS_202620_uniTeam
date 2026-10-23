"use client";

import { useEffect, useState } from "react";

/**
 * Verdadero si algo lleva cargando más de `ms`. La API gratuita se duerme y
 * tarda en despertar: pasado ese umbral se le explica al usuario, en lugar
 * de dejarle mirando un «Cargando…» sin saber si algo se ha roto.
 */
export function useLento(cargando: boolean, ms = 4000): boolean {
  const [lento, establecer] = useState(false);
  useEffect(() => {
    if (!cargando) {
      establecer(false);
      return;
    }
    const temporizador = window.setTimeout(() => establecer(true), ms);
    return () => window.clearTimeout(temporizador);
  }, [cargando, ms]);
  return lento;
}

/** Correo con forma razonable. La API no lo exige; la interfaz, sí, para evitar erratas. */
export function pareceCorreo(texto: string): boolean {
  const arroba = texto.indexOf("@");
  const punto = texto.indexOf(".", arroba + 1);
  return arroba > 0
    && punto > arroba + 1
    && punto < texto.length - 1
    && !/[\s@]/.test(texto.slice(0, arroba))
    && !/[\s@]/.test(texto.slice(arroba + 1, punto))
    && !/[\s@]/.test(texto.slice(punto + 1));
}
