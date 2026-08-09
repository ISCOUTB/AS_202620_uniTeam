"""Modelo ORM: traslados"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Date, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import EstadoTraslado


class Traslado(Base):
    __tablename__ = "traslados"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero_traslado = Column(String(50), unique=True, nullable=False)
    activo_id = Column(UUID(as_uuid=True), ForeignKey("activos.id", ondelete="RESTRICT"), nullable=False)
    ubicacion_origen_id = Column(UUID(as_uuid=True), ForeignKey("ubicaciones.id", ondelete="SET NULL"))
    ubicacion_destino_id = Column(UUID(as_uuid=True), ForeignKey("ubicaciones.id", ondelete="RESTRICT"), nullable=False)
    usuario_origen_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    usuario_destino_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    motivo = Column(Text)
    estado = Column(Enum(EstadoTraslado, name="estado_traslado", create_type=False), nullable=False, default=EstadoTraslado.PENDIENTE)
    solicitado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    aprobado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    aprobado_en = Column(DateTime(timezone=True))
    motivo_rechazo = Column(Text)
    confirmado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    confirmado_en = Column(DateTime(timezone=True))
    fecha_esperada = Column(Date)
    completado_en = Column(DateTime(timezone=True))
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    actualizado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relaciones
    activo = relationship("Activo", back_populates="traslados")
    ubicacion_origen = relationship("Ubicacion", foreign_keys=[ubicacion_origen_id])
    ubicacion_destino = relationship("Ubicacion", foreign_keys=[ubicacion_destino_id])
    usuario_origen = relationship("Usuario", foreign_keys=[usuario_origen_id])
    usuario_destino = relationship("Usuario", foreign_keys=[usuario_destino_id])
    usuario_solicitante = relationship("Usuario", foreign_keys=[solicitado_por])
    usuario_aprobador = relationship("Usuario", foreign_keys=[aprobado_por])
    usuario_confirmador = relationship("Usuario", foreign_keys=[confirmado_por])
    movimientos = relationship("MovimientoActivo", back_populates="traslado")
