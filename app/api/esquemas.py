"""Esquemas de entrada y salida de la API (Pydantic)."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.domain.modelos import EstadoTarea, Prioridad, RolMiembro


class CrearProyecto(BaseModel):
    nombre: str = Field(min_length=1, max_length=200)
    miembros: list[str] = Field(default_factory=list)


class CrearTarea(BaseModel):
    titulo: str = Field(min_length=1, max_length=300)
    prioridad: Prioridad = Prioridad.MEDIA
    responsable: Optional[str] = None
    fecha_limite: Optional[date] = None


class AsignarTarea(BaseModel):
    responsable: str


class CambiarEstado(BaseModel):
    estado: EstadoTarea


class TareaSalida(BaseModel):
    id: str
    proyecto_id: str
    titulo: str
    prioridad: Prioridad
    estado: EstadoTarea
    responsable: Optional[str]
    fecha_limite: Optional[date]
    creada_por: str
    creada_en: datetime


class ProyectoSalida(BaseModel):
    id: str
    nombre: str
    miembros: list[str]


class AgregarMiembro(BaseModel):
    usuario: str = Field(min_length=1, max_length=120)
    rol: RolMiembro = RolMiembro.INTEGRANTE


class MiembroSalida(BaseModel):
    usuario: str
    rol: RolMiembro


class ProyectoDetalle(BaseModel):
    id: str
    nombre: str
    miembros: list[MiembroSalida]


class ProgresoSalida(BaseModel):
    total: int
    por_estado: dict[str, int]
    sin_responsable: int
    vencidas: int
    porcentaje_completado: float
