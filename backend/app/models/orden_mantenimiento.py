"""Modelo ORM: ordenes_mantenimiento"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import PrioridadMantenimiento, EstadoMantenimiento


class OrdenMantenimiento(Base):
    __tablename__ = "ordenes_mantenimiento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activo_id = Column(UUID(as_uuid=True), ForeignKey("activos.id", ondelete="RESTRICT"), nullable=False)
    prioridad = Column(Enum(PrioridadMantenimiento, name="prioridad_mantenimiento", create_type=False), nullable=False, default=PrioridadMantenimiento.MEDIA)
    estado = Column(Enum(EstadoMantenimiento, name="estado_mantenimiento", create_type=False), nullable=False, default=EstadoMantenimiento.ABIERTA)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text)
    programado_para = Column(DateTime(timezone=True))
    abierto_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    asignado_a = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    cerrado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    abierto_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    cerrado_en = Column(DateTime(timezone=True))

    # Relaciones
    activo = relationship("Activo", back_populates="ordenes_mantenimiento")
    usuario_apertura = relationship("Usuario", foreign_keys=[abierto_por])
    usuario_asignado = relationship("Usuario", foreign_keys=[asignado_a])
    usuario_cierre = relationship("Usuario", foreign_keys=[cerrado_por])
