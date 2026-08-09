"""Modelo ORM: movimientos_activos (inmutable)"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import TipoMovimientoActivo, EstadoActivo


class MovimientoActivo(Base):
    __tablename__ = "movimientos_activos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activo_id = Column(UUID(as_uuid=True), ForeignKey("activos.id", ondelete="RESTRICT"), nullable=False)
    tipo_movimiento = Column(Enum(TipoMovimientoActivo, name="tipo_movimiento_activo", create_type=False), nullable=False)
    ubicacion_desde_id = Column(UUID(as_uuid=True), ForeignKey("ubicaciones.id", ondelete="SET NULL"))
    ubicacion_hasta_id = Column(UUID(as_uuid=True), ForeignKey("ubicaciones.id", ondelete="SET NULL"))
    usuario_desde_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    usuario_hasta_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    estado_desde = Column(Enum(EstadoActivo, name="estado_activo", create_type=False))
    estado_hasta = Column(Enum(EstadoActivo, name="estado_activo", create_type=False))
    realizado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    traslado_id = Column(UUID(as_uuid=True), ForeignKey("traslados.id", ondelete="SET NULL"))
    notas = Column(Text)
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relaciones
    activo = relationship("Activo", back_populates="movimientos")
    ubicacion_desde = relationship("Ubicacion", foreign_keys=[ubicacion_desde_id])
    ubicacion_hasta = relationship("Ubicacion", foreign_keys=[ubicacion_hasta_id])
    usuario_desde = relationship("Usuario", foreign_keys=[usuario_desde_id])
    usuario_hasta = relationship("Usuario", foreign_keys=[usuario_hasta_id])
    usuario_realizado = relationship("Usuario", foreign_keys=[realizado_por])
    traslado = relationship("Traslado", back_populates="movimientos")
