"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

const CLAVE = "uniteam.usuario";

interface Sesion {
  usuario: string | null;
  cambiar: (nuevo: string | null) => void;
  cargado: boolean;
}

const Contexto = createContext<Sesion | null>(null);

/**
 * Identidad provisional del usuario, compartida por toda la aplicación.
 *
 * Es un contexto y no un hook suelto a propósito: con un hook independiente
 * por componente, cada uno tendría su propio estado y la página no se
 * enteraría de que el usuario cambió en la barra superior.
 *
 * Sustituye al proveedor de identidad del C4 nivel 2 mientras no se integra
 * OIDC. **No es autenticación**: solo indica con qué nombre se llama a la API.
 * La autorización es real y la aplica el backend.
 */
export function ProveedorUsuario({ children }: { children: React.ReactNode }) {
  const [usuario, establecer] = useState<string | null>(null);
  const [cargado, marcarCargado] = useState(false);

  useEffect(() => {
    try {
      establecer(window.localStorage.getItem(CLAVE));
    } catch {
      /* almacenamiento no disponible */
    }
    marcarCargado(true);
  }, []);

  const cambiar = useCallback((nuevo: string | null) => {
    establecer(nuevo);
    try {
      if (nuevo) window.localStorage.setItem(CLAVE, nuevo);
      else window.localStorage.removeItem(CLAVE);
    } catch {
      /* almacenamiento no disponible */
    }
  }, []);

  const valor = useMemo(
    () => ({ usuario, cambiar, cargado }),
    [usuario, cambiar, cargado],
  );

  return <Contexto.Provider value={valor}>{children}</Contexto.Provider>;
}

export function useUsuario(): Sesion {
  const sesion = useContext(Contexto);
  if (!sesion) {
    throw new Error("useUsuario debe usarse dentro de <ProveedorUsuario>.");
  }
  return sesion;
}
