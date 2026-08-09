"""Modelo ORM: sesiones_autenticacion"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from app.database import Base


class SesionAutenticacion(Base):
    __tablename__ = "sesiones_autenticacion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    hash_token_refresh = Column(Text, nullable=False)
    dispositivo_id = Column(String(100))
    agente_usuario = Column(Text)
    direccion_ip = Column(INET)
    emitido_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    expira_en = Column(DateTime(timezone=True), nullable=False)
    revocado_en = Column(DateTime(timezone=True))
    reemplazado_por = Column(UUID(as_uuid=True), ForeignKey("sesiones_autenticacion.id", ondelete="SET NULL"))

    __table_args__ = (
        UniqueConstraint("usuario_id", "hash_token_refresh"),
    )

    # Relaciones
    usuario = relationship("Usuario", back_populates="sesiones_autenticacion")
