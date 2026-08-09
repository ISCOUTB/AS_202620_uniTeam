"""Schemas: Movimientos de Activos"""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.enums import TipoMovimientoActivo, EstadoActivo


class MovimientoActivoResponse(BaseModel):
    id: UUID
    activo_id: UUID
    tipo_movimiento: TipoMovimientoActivo
    ubicacion_desde_id: Optional[UUID] = None
    ubicacion_hasta_id: Optional[UUID] = None
    usuario_desde_id: Optional[UUID] = None
    usuario_hasta_id: Optional[UUID] = None
    estado_desde: Optional[EstadoActivo] = None
    estado_hasta: Optional[EstadoActivo] = None
    realizado_por: UUID
    traslado_id: Optional[UUID] = None
    notas: Optional[str] = None
    creado_en: datetime

    class Config:
        from_attributes = True
