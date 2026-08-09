"""Modelo ORM: categorias_activos"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class CategoriaActivo(Base):
    __tablename__ = "categorias_activos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(255), nullable=False)
    codigo = Column(String(50), unique=True)
    anos_depreciacion = Column(Integer)
    intervalo_mantenimiento_dias = Column(Integer)
    padre_id = Column(UUID(as_uuid=True), ForeignKey("categorias_activos.id", ondelete="RESTRICT"))
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    actualizado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("anos_depreciacion IS NULL OR anos_depreciacion > 0", name="chk_anos_depreciacion"),
        CheckConstraint("intervalo_mantenimiento_dias IS NULL OR intervalo_mantenimiento_dias > 0", name="chk_intervalo_mantenimiento"),
    )

    # Relaciones
    padre = relationship("CategoriaActivo", remote_side="CategoriaActivo.id", backref="subcategorias")
    activos = relationship("Activo", back_populates="categoria")
