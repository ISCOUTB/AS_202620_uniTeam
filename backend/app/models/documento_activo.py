"""Modelo ORM: documentos_activos"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, BigInteger, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import TipoDocumento


class DocumentoActivo(Base):
    __tablename__ = "documentos_activos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activo_id = Column(UUID(as_uuid=True), ForeignKey("activos.id", ondelete="CASCADE"), nullable=False)
    tipo_documento = Column(Enum(TipoDocumento, name="tipo_documento", create_type=False), nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    url_archivo = Column(Text, nullable=False)
    tipo_mime = Column(String(100))
    tamano_bytes = Column(BigInteger)
    subido_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relaciones
    activo = relationship("Activo", back_populates="documentos")
    usuario_subido = relationship("Usuario", foreign_keys=[subido_por])
