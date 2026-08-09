"""Schemas: Mantenimiento (planes + órdenes)"""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.models.enums import PrioridadMantenimiento, EstadoMantenimiento


# ─── Planes ───
class PlanMantenimientoCreate(BaseModel):
    activo_id: UUID
    intervalo_dias: int
    proxima_fecha: Optional[date] = None


class PlanMantenimientoUpdate(BaseModel):
    intervalo_dias: Optional[int] = None
    proxima_fecha: Optional[date] = None
    esta_activo: Optional[bool] = None


class PlanMantenimientoResponse(BaseModel):
    id: UUID
    activo_id: UUID
    intervalo_dias: int
    proxima_fecha: Optional[date] = None
    esta_activo: bool
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True


# ─── Órdenes ───
class OrdenMantenimientoCreate(BaseModel):
    activo_id: UUID
    prioridad: PrioridadMantenimiento = PrioridadMantenimiento.MEDIA
    titulo: str
    descripcion: Optional[str] = None
    programado_para: Optional[datetime] = None
    asignado_a: Optional[UUID] = None


class OrdenMantenimientoUpdate(BaseModel):
    prioridad: Optional[PrioridadMantenimiento] = None
    estado: Optional[EstadoMantenimiento] = None
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    programado_para: Optional[datetime] = None
    asignado_a: Optional[UUID] = None


class OrdenMantenimientoResponse(BaseModel):
    id: UUID
    activo_id: UUID
    prioridad: PrioridadMantenimiento
    estado: EstadoMantenimiento
    titulo: str
    descripcion: Optional[str] = None
    programado_para: Optional[datetime] = None
    abierto_por: Optional[UUID] = None
    asignado_a: Optional[UUID] = None
    cerrado_por: Optional[UUID] = None
    abierto_en: datetime
    cerrado_en: Optional[datetime] = None

    class Config:
        from_attributes = True
