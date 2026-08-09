"""Modelo ORM: ubicaciones"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Ubicacion(Base):
    __tablename__ = "ubicaciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(255), nullable=False)
    codigo = Column(String(50), unique=True, nullable=False)
    edificio = Column(String(100))
    piso = Column(String(20))
    padre_id = Column(UUID(as_uuid=True), ForeignKey("ubicaciones.id", ondelete="RESTRICT"))
    esta_activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    actualizado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relaciones
    padre = relationship("Ubicacion", remote_side="Ubicacion.id", backref="hijos")
    activos = relationship("Activo", back_populates="ubicacion_actual", foreign_keys="Activo.ubicacion_actual_id")
