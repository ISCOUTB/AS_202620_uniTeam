"""Modelo ORM: conflictos_sincronizacion"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class ConflictoSincronizacion(Base):
    __tablename__ = "conflictos_sincronizacion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cola_id = Column(UUID(as_uuid=True), ForeignKey("cola_sincronizacion.id", ondelete="CASCADE"))
    nombre_entidad = Column(String(100), nullable=False)
    entidad_id = Column(UUID(as_uuid=True))
    payload_cliente = Column(JSONB, nullable=False)
    payload_servidor = Column(JSONB, nullable=False)
    resuelto_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    resuelto_en = Column(DateTime(timezone=True))
    notas_resolucion = Column(Text)
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relaciones
    cola = relationship("ColaSincronizacion", back_populates="conflictos")
    usuario_resolutor = relationship("Usuario", foreign_keys=[resuelto_por])
