"""Modelo ORM: predicciones_ia"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class PrediccionIA(Base):
    __tablename__ = "predicciones_ia"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activo_id = Column(UUID(as_uuid=True), ForeignKey("activos.id", ondelete="CASCADE"), nullable=False)
    nombre_modelo = Column(String(100), nullable=False)
    tipo_prediccion = Column(String(100), nullable=False)
    puntaje = Column(Numeric(5, 4))
    fecha_predicha = Column(Date)
    detalle = Column(JSONB)
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relaciones
    activo = relationship("Activo", back_populates="predicciones")
