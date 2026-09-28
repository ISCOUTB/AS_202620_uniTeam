"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { alCaducarSesion } from "./api";
import {
  caducado,
  cerrarSesion as olvidar,
  cerrarSesionEnProveedor,
  contenidoDelToken,
  iniciarSesion,
  leerToken,
} from "./oidc";

interface Sesion {
  token: string | null;
  /** Identidad en minúsculas, igual que la normaliza la API. */
  usuario: string | null;
  cargado: boolean;
  /** Por qué se cerró la sesión sin que el usuario lo pidiera. */
  motivoCierre: string | null;
  entrar: () => Promise<void>;
  salir: () => void;
  refrescar: () => void;
}

const Contexto = createContext<Sesion | null>(null);

/** Sesión del usuario, compartida por toda la aplicación. */
export function ProveedorSesion({ children }: { children: React.ReactNode }) {
  const [token, establecer] = useState<string | null>(null);
  const [cargado, marcarCargado] = useState(false);
  const [motivoCierre, establecerMotivo] = useState<string | null>(null);

  const refrescar = useCallback(() => {
    const guardado = leerToken();
    establecer(guardado && !caducado(guardado) ? guardado : null);
    if (guardado && caducado(guardado)) olvidar();
  }, []);

  const caducar = useCallback((motivo: string) => {
    olvidar();
    establecer(null);
    establecerMotivo(motivo);
  }, []);

  useEffect(() => {
    refrescar();
    marcarCargado(true);
  }, [refrescar]);

  // Un 401 de la API cierra la sesión en lugar de dejar un error técnico.
  useEffect(() => {
    alCaducarSesion(() => caducar("Tu sesión ha caducado. Vuelve a iniciar sesión."));
    return () => alCaducarSesion(null);
  }, [caducar]);

  // El token dice cuándo caduca: se cierra la sesión en ese momento, no al
  // siguiente clic que fallaría.
  useEffect(() => {
    if (!token) return;
    const expira = contenidoDelToken(token)?.expira ?? 0;
    const espera = Math.max(expira - Date.now(), 0);
    const temporizador = window.setTimeout(
      () => caducar("Tu sesión ha caducado. Vuelve a iniciar sesión."),
      Math.min(espera, 2 ** 31 - 1),
    );
    return () => window.clearTimeout(temporizador);
  }, [token, caducar]);

  const salir = useCallback(() => {
    establecer(null);
    establecerMotivo(null);
    void cerrarSesionEnProveedor();
  }, []);

  const entrar = useCallback(() => {
    establecerMotivo(null);
    return iniciarSesion();
  }, []);

  const valor = useMemo<Sesion>(
    () => ({
      token,
      usuario: token ? (contenidoDelToken(token)?.usuario.toLowerCase() ?? null) : null,
      cargado,
      motivoCierre,
      entrar,
      salir,
      refrescar,
    }),
    [token, cargado, motivoCierre, entrar, salir, refrescar],
  );

  return <Contexto.Provider value={valor}>{children}</Contexto.Provider>;
}

export function useSesion(): Sesion {
  const sesion = useContext(Contexto);
  if (!sesion) throw new Error("useSesion debe usarse dentro de <ProveedorSesion>.");
  return sesion;
}
