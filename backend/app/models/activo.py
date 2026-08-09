"""Modelo ORM: activos"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Numeric, Date, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import EstadoActivo


class Activo(Base):
    __tablename__ = "activos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(100), unique=True, nullable=False)
    codigo_qr = Column(Text)
    codigo_barras = Column(String(100))
    etiqueta_rfid = Column(String(100))
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    marca = Column(String(100))
    modelo = Column(String(100))
    numero_serie = Column(String(100))
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias_activos.id", ondelete="RESTRICT"))
    estado = Column(Enum(EstadoActivo, name="estado_activo", create_type=False), nullable=False, default=EstadoActivo.ACTIVO)
    ubicacion_actual_id = Column(UUID(as_uuid=True), ForeignKey("ubicaciones.id", ondelete="SET NULL"))
    asignado_a_usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    fecha_adquisicion = Column(Date)
    valor_adquisicion = Column(Numeric(15, 2))
    moneda = Column(String(10), nullable=False, default="USD")
    proveedor = Column(String(255))
    numero_factura = Column(String(100))
    garantia_hasta = Column(Date)
    url_imagen = Column(Text)
    notas = Column(Text)
    creado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    version = Column(Integer, nullable=False, default=1)
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    actualizado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    eliminado_en = Column(DateTime(timezone=True))

    # Relaciones
    categoria = relationship("CategoriaActivo", back_populates="activos")
    ubicacion_actual = relationship("Ubicacion", back_populates="activos", foreign_keys=[ubicacion_actual_id])
    asignado_a_usuario = relationship("Usuario", back_populates="activos_asignados", foreign_keys=[asignado_a_usuario_id])
    creado_por_usuario = relationship("Usuario", back_populates="activos_creados", foreign_keys=[creado_por])
    documentos = relationship("DocumentoActivo", back_populates="activo", cascade="all, delete-orphan")
    traslados = relationship("Traslado", back_populates="activo")
    movimientos = relationship("MovimientoActivo", back_populates="activo")
    planes_mantenimiento = relationship("PlanMantenimiento", back_populates="activo", cascade="all, delete-orphan")
    ordenes_mantenimiento = relationship("OrdenMantenimiento", back_populates="activo")
    predicciones = relationship("PrediccionIA", back_populates="activo", cascade="all, delete-orphan")
