"""Schemas: Documentos de Activos"""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.enums import TipoDocumento


class DocumentoActivoCreate(BaseModel):
    tipo_documento: TipoDocumento
    nombre_archivo: str
    url_archivo: str
    tipo_mime: Optional[str] = None
    tamano_bytes: Optional[int] = None


class DocumentoActivoResponse(BaseModel):
    id: UUID
    activo_id: UUID
    tipo_documento: TipoDocumento
    nombre_archivo: str
    url_archivo: str
    tipo_mime: Optional[str] = None
    tamano_bytes: Optional[int] = None
    subido_por: Optional[UUID] = None
    creado_en: datetime

    class Config:
        from_attributes = True
