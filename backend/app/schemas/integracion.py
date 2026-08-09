"""Schemas: Integraciones"""

from pydantic import BaseModel
from typing import Optional, Any, Dict
from uuid import UUID
from datetime import datetime


class IntegracionCreate(BaseModel):
    proveedor: str  # SAP, ODOO, OTRO
    direccion: str  # ENTRADA, SALIDA
    nombre_entidad: str
    payload: Optional[Dict[str, Any]] = None


class IntegracionResponse(BaseModel):
    id: UUID
    proveedor: str
    direccion: str
    nombre_entidad: str
    payload: Optional[Dict[str, Any]] = None
    estado: str
    reintentos: int
    mensaje_error: Optional[str] = None
    creado_en: datetime
    procesado_en: Optional[datetime] = None

    class Config:
        from_attributes = True
