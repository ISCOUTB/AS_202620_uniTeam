"""Schemas: Activos"""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from app.models.enums import EstadoActivo


class ActivoCreate(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    codigo_qr: Optional[str] = None
    codigo_barras: Optional[str] = None
    etiqueta_rfid: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    numero_serie: Optional[str] = None
    categoria_id: Optional[UUID] = None
    ubicacion_actual_id: Optional[UUID] = None
    asignado_a_usuario_id: Optional[UUID] = None
    fecha_adquisicion: Optional[date] = None
    valor_adquisicion: Optional[Decimal] = None
    moneda: str = "USD"
    proveedor: Optional[str] = None
    numero_factura: Optional[str] = None
    garantia_hasta: Optional[date] = None
    url_imagen: Optional[str] = None
    notas: Optional[str] = None


class ActivoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    codigo_qr: Optional[str] = None
    codigo_barras: Optional[str] = None
    etiqueta_rfid: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    numero_serie: Optional[str] = None
    categoria_id: Optional[UUID] = None
    ubicacion_actual_id: Optional[UUID] = None
    fecha_adquisicion: Optional[date] = None
    valor_adquisicion: Optional[Decimal] = None
    moneda: Optional[str] = None
    proveedor: Optional[str] = None
    numero_factura: Optional[str] = None
    garantia_hasta: Optional[date] = None
    url_imagen: Optional[str] = None
    notas: Optional[str] = None


class ActivoEstadoUpdate(BaseModel):
    estado: EstadoActivo
    notas: Optional[str] = None


class ActivoAsignarUpdate(BaseModel):
    asignado_a_usuario_id: Optional[UUID] = None
    notas: Optional[str] = None


class ActivoResponse(BaseModel):
    id: UUID
    codigo: str
    codigo_qr: Optional[str] = None
    codigo_barras: Optional[str] = None
    etiqueta_rfid: Optional[str] = None
    nombre: str
    descripcion: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    numero_serie: Optional[str] = None
    categoria_id: Optional[UUID] = None
    estado: EstadoActivo
    ubicacion_actual_id: Optional[UUID] = None
    asignado_a_usuario_id: Optional[UUID] = None
    fecha_adquisicion: Optional[date] = None
    valor_adquisicion: Optional[Decimal] = None
    moneda: str
    proveedor: Optional[str] = None
    numero_factura: Optional[str] = None
    garantia_hasta: Optional[date] = None
    url_imagen: Optional[str] = None
    notas: Optional[str] = None
    creado_por: Optional[UUID] = None
    version: int
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True


class ActivoListResponse(BaseModel):
    total: int
    items: list[ActivoResponse]
