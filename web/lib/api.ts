/**
 * Cliente de la API de UniTeam.
 *
 * El navegador habla directamente con el contenedor «API» del C4 nivel 2, que
 * es la relación «Aplicación Web → API (REST/JSON)» del diagrama.
 */

export const API =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Prioridad = "baja" | "media" | "alta";
export type EstadoTarea = "pendiente" | "en_progreso" | "completada";
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

export class ErrorApi extends Error {
  constructor(readonly estado: number, mensaje: string) {
    super(mensaje);
  }
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
    const parametros = new URLSearchParams();
    if (filtros.estado) parametros.set("estado", filtros.estado);
    if (filtros.responsable) parametros.set("responsable", filtros.responsable);
    const consulta = parametros.toString();
    return pedir<Tarea[]>(
      `/proyectos/${id}/tareas${consulta ? `?${consulta}` : ""}`,
      token,
    );
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

  progreso: (token: string, id: string) =>
    pedir<Progreso>(`/proyectos/${id}/progreso`, token),
};

/** Estados a los que se puede pasar desde cada estado (espeja el dominio). */
export const TRANSICIONES: Record<EstadoTarea, EstadoTarea[]> = {
  pendiente: ["en_progreso"],
  en_progreso: ["pendiente", "completada"],
  completada: ["en_progreso"],
};

export const ETIQUETA_ESTADO: Record<EstadoTarea, string> = {
  pendiente: "Pendiente",
  en_progreso: "En progreso",
  completada: "Completada",
};
