/**
 * Cliente de la API de UniTeam.
 *
 * El navegador habla directamente con el contenedor «API» del C4 nivel 2, que
 * es la relación «Aplicación Web → API (REST/JSON)» del diagrama.
 */

export const API =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Prioridad = "baja" | "media" | "alta";
/** Identificador de estado. Cuáles existen lo dice la API (GET /flujo-estados). */
export type EstadoTarea = string;
export type RolMiembro = "integrante" | "lider";

export interface Miembro {
  usuario: string;
  rol: RolMiembro;
}

export interface Proyecto {
  id: string;
  nombre: string;
  miembros: Miembro[];
}

export interface Tarea {
  id: string;
  proyecto_id: string;
  titulo: string;
  prioridad: Prioridad;
  estado: EstadoTarea;
  responsable: string | null;
  fecha_limite: string | null;
  creada_por: string;
  creada_en: string;
}

export interface Progreso {
  total: number;
  por_estado: Record<string, number>;
  sin_responsable: number;
  vencidas: number;
  porcentaje_completado: number;
}

export interface EstadoFlujo {
  id: EstadoTarea;
  etiqueta: string;
  inicial: boolean;
  final: boolean;
  siguientes: EstadoTarea[];
}

export class ErrorApi extends Error {
  constructor(readonly estado: number, mensaje: string) {
    super(mensaje);
  }
}

/**
 * Qué hacer cuando la API responde 401: el token caducó o dejó de valer. La
 * sesión se registra aquí para cerrarse sola en lugar de dejar la pantalla
 * mostrando «Token inválido: Signature has expired».
 */
let alCaducar: (() => void) | null = null;
export function alCaducarSesion(accion: (() => void) | null): void {
  alCaducar = accion;
}

async function pedir<T>(
  ruta: string,
  token: string,
  opciones: RequestInit = {},
): Promise<T> {
  const respuesta = await fetch(`${API}${ruta}`, {
    ...opciones,
    headers: {
      "Content-Type": "application/json",
      // La identidad la lleva el token; la API la verifica contra el emisor.
      Authorization: `Bearer ${token}`,
      ...(opciones.headers ?? {}),
    },
    cache: "no-store",
  });

  if (respuesta.status === 401) {
    alCaducar?.();
    throw new ErrorApi(401, "Tu sesión ha caducado. Vuelve a iniciar sesión.");
  }

  if (!respuesta.ok) {
    let detalle = `Error ${respuesta.status}`;
    try {
      const cuerpo = await respuesta.json();
      if (cuerpo?.detail) detalle = String(cuerpo.detail);
    } catch {
      /* la respuesta no traía JSON */
    }
    throw new ErrorApi(respuesta.status, detalle);
  }

  return respuesta.status === 204 ? (undefined as T) : respuesta.json();
}

let flujo: Promise<EstadoFlujo[]> | null = null;

/**
 * Flujo de estados, tal como lo define el dominio (ADR 0012). Se pide una vez
 * por carga de la aplicación: no cambia mientras la API no se redespliegue.
 */
export function obtenerFlujo(): Promise<EstadoFlujo[]> {
  flujo ??= fetch(`${API}/flujo-estados`, { cache: "no-store" })
    .then((r) => {
      if (!r.ok) throw new ErrorApi(r.status, "No se pudo leer el flujo de estados.");
      return r.json() as Promise<{ estados: EstadoFlujo[] }>;
    })
    .then((cuerpo) => cuerpo.estados)
    .catch((e) => {
      flujo = null;
      throw e;
    });
  return flujo;
}

export const api = {
  listarProyectos: (token: string) =>
    pedir<Proyecto[]>("/proyectos", token),

  obtenerProyecto: (token: string, id: string) =>
    pedir<Proyecto>(`/proyectos/${id}`, token),

  crearProyecto: (token: string, nombre: string, miembros: string[]) =>
    pedir<{ id: string }>("/proyectos", token, {
      method: "POST",
      body: JSON.stringify({ nombre, miembros }),
    }),

  agregarMiembro: (token: string, id: string, nuevo: string) =>
    pedir<Proyecto>(`/proyectos/${id}/miembros`, token, {
      method: "POST",
      body: JSON.stringify({ usuario: nuevo }),
    }),

  listarTareas: (
    token: string,
    id: string,
    filtros: { estado?: EstadoTarea; responsable?: string } = {},
  ) => {
    // 200 es el tope de la API y el tamaño de proyecto de ESC-01. Sin él, la
    // API devolvía 50 y el tablero ocultaba el resto sin avisar.
    const parametros = new URLSearchParams({ limite: "200" });
    if (filtros.estado) parametros.set("estado", filtros.estado);
    if (filtros.responsable) parametros.set("responsable", filtros.responsable);
    return pedir<Tarea[]>(`/proyectos/${id}/tareas?${parametros}`, token);
  },

  crearTarea: (
    token: string,
    id: string,
    datos: {
      titulo: string;
      prioridad: Prioridad;
      responsable?: string | null;
      fecha_limite?: string | null;
    },
  ) =>
    pedir<Tarea>(`/proyectos/${id}/tareas`, token, {
      method: "POST",
      body: JSON.stringify(datos),
    }),

  cambiarEstado: (
    token: string,
    id: string,
    tareaId: string,
    estado: EstadoTarea,
  ) =>
    pedir<Tarea>(`/proyectos/${id}/tareas/${tareaId}/estado`, token, {
      method: "PUT",
      body: JSON.stringify({ estado }),
    }),

  editarTarea: (
    token: string,
    id: string,
    tareaId: string,
    cambios: { titulo?: string; prioridad?: Prioridad; fecha_limite?: string | null },
  ) =>
    pedir<Tarea>(`/proyectos/${id}/tareas/${tareaId}`, token, {
      method: "PATCH",
      body: JSON.stringify(cambios),
    }),

  eliminarTarea: (token: string, id: string, tareaId: string) =>
    pedir<void>(`/proyectos/${id}/tareas/${tareaId}`, token, { method: "DELETE" }),

  asignarTarea: (token: string, id: string, tareaId: string, responsable: string) =>
    pedir<Tarea>(`/proyectos/${id}/tareas/${tareaId}/responsable`, token, {
      method: "PUT",
      body: JSON.stringify({ responsable }),
    }),

  progreso: (token: string, id: string) =>
    pedir<Progreso>(`/proyectos/${id}/progreso`, token),
};

export const PRIORIDADES: Prioridad[] = ["alta", "media", "baja"];

export const ETIQUETA_PRIORIDAD: Record<Prioridad, string> = {
  alta: "Alta",
  media: "Media",
  baja: "Baja",
};

/** Orden de prioridad para ordenar tarjetas: alta primero. */
export const PESO_PRIORIDAD: Record<Prioridad, number> = { alta: 0, media: 1, baja: 2 };
