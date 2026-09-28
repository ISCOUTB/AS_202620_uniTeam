"""Entidades y reglas del dominio de UniTeam.

Este módulo no depende de FastAPI ni de SQLAlchemy: es el núcleo que la
sección 5 de arc42 describe como «Dominio».
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from app.domain.errores import TransicionInvalida, YaEsMiembro


class Prioridad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class EstadoTarea(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"


# El flujo de estados vive en un único sitio a propósito: ESC-05 mide el costo
# de añadir un estado nuevo, y este bloque es el punto donde se añade. La API
# lo publica en GET /flujo-estados y la Aplicación Web lo lee de ahí, así que
# ningún otro componente conoce los estados (ADR 0012). El orden del enum es el
# orden de las columnas del tablero.
TRANSICIONES: dict[EstadoTarea, tuple[EstadoTarea, ...]] = {
    EstadoTarea.PENDIENTE: (EstadoTarea.EN_PROGRESO,),
    EstadoTarea.EN_PROGRESO: (EstadoTarea.PENDIENTE, EstadoTarea.COMPLETADA),
    EstadoTarea.COMPLETADA: (EstadoTarea.EN_PROGRESO,),
}

ETIQUETAS_ESTADO: dict[EstadoTarea, str] = {
    EstadoTarea.PENDIENTE: "Pendiente",
    EstadoTarea.EN_PROGRESO: "En progreso",
    EstadoTarea.COMPLETADA: "Completada",
}

# Dónde nace una tarea y dónde se da por terminada: la que está en el estado
# final no vence y cuenta para el porcentaje de avance.
ESTADO_INICIAL = EstadoTarea.PENDIENTE
ESTADO_FINAL = EstadoTarea.COMPLETADA


def normalizar_usuario(usuario: str) -> str:
    """Forma canónica de una identidad: sin espacios y en minúsculas.

    Los miembros se identifican por correo, y un correo no distingue
    mayúsculas en la práctica: «Bruno@UTB.edu.co» y «bruno@utb.edu.co» son la
    misma persona. Sin esta regla, añadir a alguien con otra capitalización
    lo dejaba fuera de su propio proyecto (ESC-03 le negaba el acceso).
    """
    return usuario.strip().lower()


class RolMiembro(str, Enum):
    INTEGRANTE = "integrante"
    LIDER = "lider"


@dataclass
class Miembro:
    usuario: str
    rol: RolMiembro = RolMiembro.INTEGRANTE


@dataclass
class Proyecto:
    id: str
    nombre: str
    miembros: list[Miembro] = field(default_factory=list)

    def es_miembro(self, usuario: str) -> bool:
        return any(m.usuario == usuario for m in self.miembros)

    def puede_eliminar(self, usuario: str, tarea: "Tarea") -> bool:
        """Elimina una tarea quien la creó o el líder del proyecto."""
        return tarea.creada_por == usuario or self.es_lider(usuario)

    def es_lider(self, usuario: str) -> bool:
        return any(
            m.usuario == usuario and m.rol is RolMiembro.LIDER for m in self.miembros
        )

    def agregar_miembro(self, usuario: str, rol: "RolMiembro") -> None:
        if self.es_miembro(usuario):
            raise YaEsMiembro(f"'{usuario}' ya pertenece al proyecto.")
        self.miembros.append(Miembro(usuario=usuario, rol=rol))


@dataclass
class Tarea:
    id: str
    proyecto_id: str
    titulo: str
    creada_por: str
    prioridad: Prioridad = Prioridad.MEDIA
    estado: EstadoTarea = field(default_factory=lambda: ESTADO_INICIAL)
    responsable: Optional[str] = None
    fecha_limite: Optional[date] = None
    creada_en: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def cambiar_estado(self, nuevo: EstadoTarea) -> None:
        if nuevo not in TRANSICIONES[self.estado]:
            raise TransicionInvalida(
                f"No se puede pasar de '{self.estado.value}' a '{nuevo.value}'."
            )
        self.estado = nuevo

    def asignar(self, usuario: str) -> None:
        self.responsable = usuario

    def editar(
        self,
        titulo: Optional[str] = None,
        prioridad: Optional[Prioridad] = None,
        fecha_limite: Optional[date] = None,
        quitar_fecha_limite: bool = False,
    ) -> list[str]:
        """Cambia los datos descriptivos. El estado y el responsable no: tienen
        sus propias reglas y sus propios eventos. Devuelve los campos cambiados."""
        cambiados = []
        if titulo is not None and titulo != self.titulo:
            self.titulo = titulo
            cambiados.append("titulo")
        if prioridad is not None and prioridad != self.prioridad:
            self.prioridad = prioridad
            cambiados.append("prioridad")
        if quitar_fecha_limite and self.fecha_limite is not None:
            self.fecha_limite = None
            cambiados.append("fecha_limite")
        elif fecha_limite is not None and fecha_limite != self.fecha_limite:
            self.fecha_limite = fecha_limite
            cambiados.append("fecha_limite")
        return cambiados


@dataclass
class ResumenProgreso:
    """Vista agregada del avance de un proyecto (RF-06).

    Se calcula con una consulta agregada, no trayendo las tareas a memoria:
    es una de las tácticas declaradas para ESC-01.
    """

    total: int
    por_estado: dict[str, int]
    sin_responsable: int
    vencidas: int

    @property
    def porcentaje_completado(self) -> float:
        if self.total == 0:
            return 0.0
        completadas = self.por_estado.get(ESTADO_FINAL.value, 0)
        return round(completadas * 100 / self.total, 1)
