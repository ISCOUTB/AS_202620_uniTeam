"""Schemas: Usuarios"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.enums import RolUsuario


class UsuarioCreate(BaseModel):
    correo: EmailStr
    contrasena: str
    nombre_completo: str
    rol: RolUsuario = RolUsuario.CUSTODIO
    departamento_id: Optional[UUID] = None


class UsuarioUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    departamento_id: Optional[UUID] = None


class UsuarioRolUpdate(BaseModel):
    rol: RolUsuario


class UsuarioEstadoUpdate(BaseModel):
    esta_activo: bool


class UsuarioResponse(BaseModel):
    id: UUID
    correo: str
    nombre_completo: str
    rol: RolUsuario
    departamento_id: Optional[UUID] = None
    esta_activo: bool
    ultimo_inicio_sesion_en: Optional[datetime] = None
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True
