"""Schemas: Predicciones IA"""

from pydantic import BaseModel
from typing import Optional, Any, Dict
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal


class PrediccionIACreate(BaseModel):
    activo_id: UUID
    nombre_modelo: str
    tipo_prediccion: str
    puntaje: Optional[Decimal] = None
    fecha_predicha: Optional[date] = None
    detalle: Optional[Dict[str, Any]] = None


class PrediccionIAResponse(BaseModel):
    id: UUID
    activo_id: UUID
    nombre_modelo: str
    tipo_prediccion: str
    puntaje: Optional[Decimal] = None
    fecha_predicha: Optional[date] = None
    detalle: Optional[Dict[str, Any]] = None
    creado_en: datetime

    class Config:
        from_attributes = True
