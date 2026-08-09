"""Schemas: Categorías de Activos"""

from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class CategoriaActivoCreate(BaseModel):
    nombre: str
    codigo: Optional[str] = None
    anos_depreciacion: Optional[int] = None
    intervalo_mantenimiento_dias: Optional[int] = None
    padre_id: Optional[UUID] = None


class CategoriaActivoUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    anos_depreciacion: Optional[int] = None
    intervalo_mantenimiento_dias: Optional[int] = None
    padre_id: Optional[UUID] = None


class CategoriaActivoResponse(BaseModel):
    id: UUID
    nombre: str
    codigo: Optional[str] = None
    anos_depreciacion: Optional[int] = None
    intervalo_mantenimiento_dias: Optional[int] = None
    padre_id: Optional[UUID] = None
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True


class CategoriaArbolResponse(CategoriaActivoResponse):
    subcategorias: List["CategoriaArbolResponse"] = []

    class Config:
        from_attributes = True
