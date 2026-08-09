"""Schemas: Ubicaciones"""

from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class UbicacionCreate(BaseModel):
    nombre: str
    codigo: str
    edificio: Optional[str] = None
    piso: Optional[str] = None
    padre_id: Optional[UUID] = None


class UbicacionUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    edificio: Optional[str] = None
    piso: Optional[str] = None
    padre_id: Optional[UUID] = None
    esta_activo: Optional[bool] = None


class UbicacionResponse(BaseModel):
    id: UUID
    nombre: str
    codigo: str
    edificio: Optional[str] = None
    piso: Optional[str] = None
    padre_id: Optional[UUID] = None
    esta_activo: bool
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True


class UbicacionArbolResponse(UbicacionResponse):
    hijos: List["UbicacionArbolResponse"] = []

    class Config:
        from_attributes = True
