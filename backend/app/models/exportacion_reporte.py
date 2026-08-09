"""Modelo ORM: exportaciones_reportes"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class ExportacionReporte(Base):
    __tablename__ = "exportaciones_reportes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solicitado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    tipo_reporte = Column(String(100), nullable=False)
    formato_archivo = Column(String(10), nullable=False)
    filtros = Column(JSONB)
    estado = Column(String(20), nullable=False, default="PENDIENTE")
    url_archivo = Column(Text)
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    finalizado_en = Column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("formato_archivo IN ('PDF', 'XLSX', 'CSV')", name="chk_formato_archivo"),
        CheckConstraint("estado IN ('PENDIENTE', 'EJECUTANDO', 'FINALIZADO', 'FALLIDO')", name="chk_estado_reporte"),
    )

    # Relaciones
    usuario_solicitante = relationship("Usuario", foreign_keys=[solicitado_por])
