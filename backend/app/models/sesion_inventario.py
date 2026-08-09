"""Modelo ORM: sesiones_inventario"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import EstadoSesionInventario


class SesionInventario(Base):
    __tablename__ = "sesiones_inventario"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero_sesion = Column(String(50), unique=True, nullable=False)
    ubicacion_id = Column(UUID(as_uuid=True), ForeignKey("ubicaciones.id", ondelete="RESTRICT"), nullable=False)
    estado = Column(Enum(EstadoSesionInventario, name="estado_sesion_inventario", create_type=False), nullable=False, default=EstadoSesionInventario.ABIERTA)
    iniciado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    cerrado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    iniciado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    cerrado_en = Column(DateTime(timezone=True))
    total_esperado = Column(Integer, nullable=False, default=0)
    total_escaneado = Column(Integer, nullable=False, default=0)
    total_encontrado = Column(Integer, nullable=False, default=0)
    total_faltante = Column(Integer, nullable=False, default=0)
    total_extra = Column(Integer, nullable=False, default=0)

    # Relaciones
    ubicacion = relationship("Ubicacion", foreign_keys=[ubicacion_id])
    usuario_iniciador = relationship("Usuario", foreign_keys=[iniciado_por])
    usuario_cerrador = relationship("Usuario", foreign_keys=[cerrado_por])
    items = relationship("ItemInventario", back_populates="sesion", cascade="all, delete-orphan")
