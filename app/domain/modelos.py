"""Entidades y reglas del dominio de UniTeam.

Este módulo no depende de FastAPI ni de SQLAlchemy: es el núcleo que la
sección 5 de arc42 describe como «Dominio».
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from app.domain.errores import TransicionInvalida


class Prioridad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class EstadoTarea(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"


# El flujo de estados vive en un único sitio a propósito: ESC-05 mide el costo
# de añadir un estado nuevo, y esta tabla es el punto donde se añade.
TRANSICIONES: dict[EstadoTarea, tuple[EstadoTarea, ...]] = {
    EstadoTarea.PENDIENTE: (EstadoTarea.EN_PROGRESO,),
    EstadoTarea.EN_PROGRESO: (EstadoTarea.PENDIENTE, EstadoTarea.COMPLETADA),
    EstadoTarea.COMPLETADA: (EstadoTarea.EN_PROGRESO,),
}


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


@dataclass
class Tarea:
    id: str
    proyecto_id: str
    titulo: str
    creada_por: str
    prioridad: Prioridad = Prioridad.MEDIA
    estado: EstadoTarea = EstadoTarea.PENDIENTE
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
