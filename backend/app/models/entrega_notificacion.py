"""Modelo ORM: entregas_notificacion"""

import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import CanalNotificacion


class EntregaNotificacion(Base):
    __tablename__ = "entregas_notificacion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notificacion_id = Column(UUID(as_uuid=True), ForeignKey("notificaciones.id", ondelete="CASCADE"), nullable=False)
    canal = Column(Enum(CanalNotificacion, name="canal_notificacion", create_type=False), nullable=False)
    id_externo = Column(String(255))
    entregado_en = Column(DateTime(timezone=True))
    fallido_en = Column(DateTime(timezone=True))
    mensaje_error = Column(Text)

    # Relaciones
    notificacion = relationship("Notificacion", back_populates="entregas")
