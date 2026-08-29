"""Tablas SQLAlchemy. Traducen el dominio a filas; no llevan reglas."""
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db import Base


class ProyectoTabla(Base):
    __tablename__ = "proyectos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)

    miembros: Mapped[list["MiembroTabla"]] = relationship(
        back_populates="proyecto", cascade="all, delete-orphan", lazy="selectin"
    )


class MiembroTabla(Base):
    __tablename__ = "miembros"

    proyecto_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("proyectos.id"), primary_key=True
    )
    usuario: Mapped[str] = mapped_column(String(120), primary_key=True)
    rol: Mapped[str] = mapped_column(String(20), nullable=False, default="integrante")

    proyecto: Mapped[ProyectoTabla] = relationship(back_populates="miembros")


class TareaTabla(Base):
    __tablename__ = "tareas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    proyecto_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("proyectos.id"), index=True, nullable=False
    )
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    creada_por: Mapped[str] = mapped_column(String(120), nullable=False)
    prioridad: Mapped[str] = mapped_column(String(20), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    responsable: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    fecha_limite: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    creada_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class AuditoriaTabla(Base):
    """Registro de auditoría que exige ESC-03."""

    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    recurso: Mapped[str] = mapped_column(String(200), nullable=False)
    operacion: Mapped[str] = mapped_column(String(60), nullable=False)
    resultado: Mapped[str] = mapped_column(String(30), nullable=False)
    ocurrido_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
