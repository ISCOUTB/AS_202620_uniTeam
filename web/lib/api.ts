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
  usuario: string,
  opciones: RequestInit = {},
): Promise<T> {
  const respuesta = await fetch(`${API}${ruta}`, {
    ...opciones,
    headers: {
      "Content-Type": "application/json",
      // Identidad provisional mientras no se integra OIDC.
      "X-Usuario": usuario,
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
  listarProyectos: (usuario: string) =>
    pedir<Proyecto[]>("/proyectos", usuario),

  obtenerProyecto: (usuario: string, id: string) =>
    pedir<Proyecto>(`/proyectos/${id}`, usuario),

  crearProyecto: (usuario: string, nombre: string, miembros: string[]) =>
    pedir<{ id: string }>("/proyectos", usuario, {
      method: "POST",
      body: JSON.stringify({ nombre, miembros }),
    }),

  agregarMiembro: (usuario: string, id: string, nuevo: string) =>
    pedir<Proyecto>(`/proyectos/${id}/miembros`, usuario, {
      method: "POST",
      body: JSON.stringify({ usuario: nuevo }),
    }),

  listarTareas: (
    usuario: string,
    id: string,
    filtros: { estado?: EstadoTarea; responsable?: string } = {},
  ) => {
    const parametros = new URLSearchParams();
    if (filtros.estado) parametros.set("estado", filtros.estado);
    if (filtros.responsable) parametros.set("responsable", filtros.responsable);
    const consulta = parametros.toString();
    return pedir<Tarea[]>(
      `/proyectos/${id}/tareas${consulta ? `?${consulta}` : ""}`,
      usuario,
    );
  },

  crearTarea: (
    usuario: string,
    id: string,
    datos: {
      titulo: string;
      prioridad: Prioridad;
      responsable?: string | null;
      fecha_limite?: string | null;
    },
  ) =>
    pedir<Tarea>(`/proyectos/${id}/tareas`, usuario, {
      method: "POST",
      body: JSON.stringify(datos),
    }),

  cambiarEstado: (
    usuario: string,
    id: string,
    tareaId: string,
    estado: EstadoTarea,
  ) =>
    pedir<Tarea>(`/proyectos/${id}/tareas/${tareaId}/estado`, usuario, {
      method: "PUT",
      body: JSON.stringify({ estado }),
    }),

  progreso: (usuario: string, id: string) =>
    pedir<Progreso>(`/proyectos/${id}/progreso`, usuario),
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
