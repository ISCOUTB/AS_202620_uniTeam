"""Schemas: Departamentos"""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class DepartamentoCreate(BaseModel):
    nombre: str
    codigo: Optional[str] = None


class DepartamentoUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    esta_activo: Optional[bool] = None


class DepartamentoResponse(BaseModel):
    id: UUID
    nombre: str
    codigo: Optional[str] = None
    esta_activo: bool
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True
