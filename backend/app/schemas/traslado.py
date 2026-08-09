"""Schemas: Traslados"""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.models.enums import EstadoTraslado


class TrasladoCreate(BaseModel):
    activo_id: UUID
    ubicacion_destino_id: UUID
    usuario_destino_id: Optional[UUID] = None
    motivo: Optional[str] = None
    fecha_esperada: Optional[date] = None


class TrasladoRechazarRequest(BaseModel):
    motivo_rechazo: str


class TrasladoResponse(BaseModel):
    id: UUID
    numero_traslado: str
    activo_id: UUID
    ubicacion_origen_id: Optional[UUID] = None
    ubicacion_destino_id: UUID
    usuario_origen_id: Optional[UUID] = None
    usuario_destino_id: Optional[UUID] = None
    motivo: Optional[str] = None
    estado: EstadoTraslado
    solicitado_por: UUID
    aprobado_por: Optional[UUID] = None
    aprobado_en: Optional[datetime] = None
    motivo_rechazo: Optional[str] = None
    confirmado_por: Optional[UUID] = None
    confirmado_en: Optional[datetime] = None
    fecha_esperada: Optional[date] = None
    completado_en: Optional[datetime] = None
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True
