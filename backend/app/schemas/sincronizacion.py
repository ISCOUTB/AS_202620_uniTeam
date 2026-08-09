"""Schemas: Sincronización offline"""

from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from uuid import UUID
from datetime import datetime
from app.models.enums import OperacionSincronizacion, EstadoSincronizacion


class SyncItemRequest(BaseModel):
    dispositivo_id: str
    nombre_entidad: str
    entidad_id: Optional[UUID] = None
    operacion: OperacionSincronizacion
    payload: Dict[str, Any]


class SyncPushRequest(BaseModel):
    items: List[SyncItemRequest]


class SyncItemResponse(BaseModel):
    id: UUID
    dispositivo_id: str
    nombre_entidad: str
    entidad_id: Optional[UUID] = None
    operacion: OperacionSincronizacion
    estado: EstadoSincronizacion
    reintentos: int
    ultimo_error: Optional[str] = None
    creado_en: datetime
    sincronizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConflictoResponse(BaseModel):
    id: UUID
    cola_id: Optional[UUID] = None
    nombre_entidad: str
    entidad_id: Optional[UUID] = None
    payload_cliente: Dict[str, Any]
    payload_servidor: Dict[str, Any]
    resuelto_por: Optional[UUID] = None
    resuelto_en: Optional[datetime] = None
    notas_resolucion: Optional[str] = None
    creado_en: datetime

    class Config:
        from_attributes = True


class ConflictoResolverRequest(BaseModel):
    notas_resolucion: str
    usar_payload_cliente: bool = False
