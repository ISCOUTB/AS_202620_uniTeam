"""Eventos de dominio.

Se publican **después** de que la operación se autorizó y se ejecutó. El
despacho es en proceso (ADR 0003): no hay broker ni cola externa.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class EventoDominio:
    ocurrido_en: datetime = field(default_factory=_ahora)


@dataclass(frozen=True)
class TareaCreada(EventoDominio):
    tarea_id: str = ""
    proyecto_id: str = ""
    usuario: str = ""


@dataclass(frozen=True)
class TareaAsignada(EventoDominio):
    tarea_id: str = ""
    proyecto_id: str = ""
    responsable: str = ""
    usuario: str = ""


@dataclass(frozen=True)
class EstadoCambiado(EventoDominio):
    tarea_id: str = ""
    proyecto_id: str = ""
    estado: str = ""
    usuario: str = ""


@dataclass(frozen=True)
class AccesoDenegado(EventoDominio):
    """Intento de acceso a un proyecto del que el usuario no es miembro.

    Es la fuente del registro de auditoría que exige ESC-03.
    """
    usuario: str = ""
    recurso: str = ""
    operacion: str = ""
