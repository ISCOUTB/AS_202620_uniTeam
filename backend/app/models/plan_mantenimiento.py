"""Modelo ORM: planes_mantenimiento"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Boolean, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class PlanMantenimiento(Base):
    __tablename__ = "planes_mantenimiento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activo_id = Column(UUID(as_uuid=True), ForeignKey("activos.id", ondelete="CASCADE"), nullable=False)
    intervalo_dias = Column(Integer, nullable=False)
    proxima_fecha = Column(Date)
    esta_activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    actualizado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("intervalo_dias > 0", name="chk_intervalo_dias"),
    )

    # Relaciones
    activo = relationship("Activo", back_populates="planes_mantenimiento")
