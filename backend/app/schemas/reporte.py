"""Schemas: Reportes"""

from pydantic import BaseModel
from typing import Optional, Any, Dict
from uuid import UUID
from datetime import datetime


class ReporteCreate(BaseModel):
    tipo_reporte: str
    formato_archivo: str  # PDF, XLSX, CSV
    filtros: Optional[Dict[str, Any]] = None


class ReporteResponse(BaseModel):
    id: UUID
    solicitado_por: Optional[UUID] = None
    tipo_reporte: str
    formato_archivo: str
    filtros: Optional[Dict[str, Any]] = None
    estado: str
    url_archivo: Optional[str] = None
    creado_en: datetime
    finalizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True
