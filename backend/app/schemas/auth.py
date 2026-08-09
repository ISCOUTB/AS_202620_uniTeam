"""Schemas: Autenticación"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from app.models.enums import RolUsuario


class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str


class RegisterRequest(BaseModel):
    correo: EmailStr
    contrasena: str
    nombre_completo: str
    rol: RolUsuario = RolUsuario.CUSTODIO
    departamento_id: Optional[UUID] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class MeResponse(BaseModel):
    id: UUID
    correo: str
    nombre_completo: str
    rol: RolUsuario
    departamento_id: Optional[UUID] = None
    esta_activo: bool

    class Config:
        from_attributes = True
