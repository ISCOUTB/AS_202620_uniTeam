"""Modelo ORM: cola_sincronizacion"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import OperacionSincronizacion, EstadoSincronizacion


class ColaSincronizacion(Base):
    __tablename__ = "cola_sincronizacion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispositivo_id = Column(String(100), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    nombre_entidad = Column(String(100), nullable=False)
    entidad_id = Column(UUID(as_uuid=True))
    operacion = Column(Enum(OperacionSincronizacion, name="operacion_sincronizacion", create_type=False), nullable=False)
    payload = Column(JSONB, nullable=False)
    estado = Column(Enum(EstadoSincronizacion, name="estado_sincronizacion", create_type=False), nullable=False, default=EstadoSincronizacion.PENDIENTE)
    reintentos = Column(Integer, nullable=False, default=0)
    ultimo_error = Column(Text)
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    sincronizado_en = Column(DateTime(timezone=True))

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    conflictos = relationship("ConflictoSincronizacion", back_populates="cola", cascade="all, delete-orphan")
