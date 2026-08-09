"""Modelo ORM: usuarios"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import RolUsuario


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    correo = Column(String, unique=True, nullable=False)
    hash_contrasena = Column(String, nullable=False)
    nombre_completo = Column(String(255), nullable=False)
    rol = Column(Enum(RolUsuario, name="rol_usuario", create_type=False), nullable=False)
    departamento_id = Column(UUID(as_uuid=True), ForeignKey("departamentos.id", ondelete="SET NULL"))
    esta_activo = Column(Boolean, nullable=False, default=True)
    ultimo_inicio_sesion_en = Column(DateTime(timezone=True))
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    actualizado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relaciones
    departamento = relationship("Departamento", back_populates="usuarios")
    activos_asignados = relationship("Activo", back_populates="asignado_a_usuario", foreign_keys="Activo.asignado_a_usuario_id")
    activos_creados = relationship("Activo", back_populates="creado_por_usuario", foreign_keys="Activo.creado_por")
    sesiones_autenticacion = relationship("SesionAutenticacion", back_populates="usuario")
    notificaciones = relationship("Notificacion", back_populates="usuario")
