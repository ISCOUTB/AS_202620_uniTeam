"""Modelo ORM: notificaciones"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(String(100), nullable=False)
    titulo = Column(String(255), nullable=False)
    mensaje = Column(Text)
    data = Column(JSONB)
    esta_leido = Column(Boolean, nullable=False, default=False)
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    leido_en = Column(DateTime(timezone=True))

    # Relaciones
    usuario = relationship("Usuario", back_populates="notificaciones")
    entregas = relationship("EntregaNotificacion", back_populates="notificacion", cascade="all, delete-orphan")
