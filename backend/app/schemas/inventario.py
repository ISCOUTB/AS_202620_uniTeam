"""Schemas: Inventario (sesiones + items)"""

from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.enums import EstadoSesionInventario, ResultadoEscaneoInventario


class SesionInventarioCreate(BaseModel):
    ubicacion_id: UUID


class ScanRequest(BaseModel):
    codigo_escaneado: Optional[str] = None
    activo_id: Optional[UUID] = None
    id_evento_cliente: Optional[UUID] = None
    notas: Optional[str] = None


class ItemInventarioResponse(BaseModel):
    id: UUID
    sesion_id: UUID
    activo_id: Optional[UUID] = None
    codigo_escaneado: Optional[str] = None
    resultado_escaneo: ResultadoEscaneoInventario
    ubicacion_esperada_id: Optional[UUID] = None
    ubicacion_encontrada_id: Optional[UUID] = None
    escaneado_por: Optional[UUID] = None
    escaneado_en: datetime
    id_evento_cliente: Optional[UUID] = None
    notas: Optional[str] = None

    class Config:
        from_attributes = True


class SesionInventarioResponse(BaseModel):
    id: UUID
    numero_sesion: str
    ubicacion_id: UUID
    estado: EstadoSesionInventario
    iniciado_por: Optional[UUID] = None
    cerrado_por: Optional[UUID] = None
    iniciado_en: datetime
    cerrado_en: Optional[datetime] = None
    total_esperado: int
    total_escaneado: int
    total_encontrado: int
    total_faltante: int
    total_extra: int

    class Config:
        from_attributes = True


class SesionInventarioDetalleResponse(SesionInventarioResponse):
    items: List[ItemInventarioResponse] = []

    class Config:
        from_attributes = True
