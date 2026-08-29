"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { caducado, cerrarSesion as olvidar, contenidoDelToken, iniciarSesion, leerToken } from "./oidc";

interface Sesion {
  token: string | null;
  usuario: string | null;
  cargado: boolean;
  entrar: () => Promise<void>;
  salir: () => void;
  refrescar: () => void;
}

const Contexto = createContext<Sesion | null>(null);

/** Sesión del usuario, compartida por toda la aplicación. */
export function ProveedorSesion({ children }: { children: React.ReactNode }) {
  const [token, establecer] = useState<string | null>(null);
  const [cargado, marcarCargado] = useState(false);

  const refrescar = useCallback(() => {
    const guardado = leerToken();
    establecer(guardado && !caducado(guardado) ? guardado : null);
    if (guardado && caducado(guardado)) olvidar();
  }, []);

  useEffect(() => {
    refrescar();
    marcarCargado(true);
  }, [refrescar]);

  const salir = useCallback(() => {
    olvidar();
    establecer(null);
  }, []);

  const valor = useMemo<Sesion>(
    () => ({
      token,
      usuario: token ? (contenidoDelToken(token)?.usuario ?? null) : null,
      cargado,
      entrar: iniciarSesion,
      salir,
      refrescar,
    }),
    [token, cargado, salir, refrescar],
  );

  return <Contexto.Provider value={valor}>{children}</Contexto.Provider>;
}

export function useSesion(): Sesion {
  const sesion = useContext(Contexto);
  if (!sesion) throw new Error("useSesion debe usarse dentro de <ProveedorSesion>.");
  return sesion;
}
