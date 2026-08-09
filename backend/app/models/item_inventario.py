"""Modelo ORM: items_inventario"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import ResultadoEscaneoInventario


class ItemInventario(Base):
    __tablename__ = "items_inventario"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sesion_id = Column(UUID(as_uuid=True), ForeignKey("sesiones_inventario.id", ondelete="CASCADE"), nullable=False)
    activo_id = Column(UUID(as_uuid=True), ForeignKey("activos.id", ondelete="SET NULL"))
    codigo_escaneado = Column(String(200))
    resultado_escaneo = Column(Enum(ResultadoEscaneoInventario, name="resultado_escaneo_inventario", create_type=False), nullable=False)
    ubicacion_esperada_id = Column(UUID(as_uuid=True), ForeignKey("ubicaciones.id", ondelete="SET NULL"))
    ubicacion_encontrada_id = Column(UUID(as_uuid=True), ForeignKey("ubicaciones.id", ondelete="SET NULL"))
    escaneado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    escaneado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    id_evento_cliente = Column(UUID(as_uuid=True))
    notas = Column(Text)

    # Relaciones
    sesion = relationship("SesionInventario", back_populates="items")
    activo = relationship("Activo", foreign_keys=[activo_id])
    ubicacion_esperada = relationship("Ubicacion", foreign_keys=[ubicacion_esperada_id])
    ubicacion_encontrada = relationship("Ubicacion", foreign_keys=[ubicacion_encontrada_id])
    usuario_escaneador = relationship("Usuario", foreign_keys=[escaneado_por])
