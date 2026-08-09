"""Modelo ORM: trabajos_integracion"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class TrabajoIntegracion(Base):
    __tablename__ = "trabajos_integracion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proveedor = Column(String(50), nullable=False)
    direccion = Column(String(10), nullable=False)
    nombre_entidad = Column(String(100), nullable=False)
    payload = Column(JSONB)
    estado = Column(String(20), nullable=False, default="PENDIENTE")
    reintentos = Column(Integer, nullable=False, default=0)
    mensaje_error = Column(Text)
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    procesado_en = Column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("proveedor IN ('SAP', 'ODOO', 'OTRO')", name="chk_proveedor"),
        CheckConstraint("direccion IN ('ENTRADA', 'SALIDA')", name="chk_direccion"),
        CheckConstraint("estado IN ('PENDIENTE', 'EJECUTANDO', 'FINALIZADO', 'FALLIDO')", name="chk_estado_integracion"),
    )
