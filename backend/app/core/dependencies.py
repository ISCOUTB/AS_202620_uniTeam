"""
Dependencias reutilizables de FastAPI:
- get_db: sesión de base de datos
- get_current_user: usuario autenticado
- RoleChecker: verificación de roles
"""

from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_token
from app.models.usuario import Usuario
from app.models.enums import RolUsuario

security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Obtiene el usuario autenticado a partir del token JWT."""
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "TOKEN_INVALIDO", "mensaje": "Token de acceso inválido o expirado", "codigo": 401},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "TIPO_TOKEN_INVALIDO", "mensaje": "Se requiere un token de acceso", "codigo": 401},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "TOKEN_SIN_SUJETO", "mensaje": "Token no contiene información del usuario", "codigo": 401},
        )

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "USUARIO_NO_ENCONTRADO", "mensaje": "El usuario del token no existe", "codigo": 404},
        )

    if not user.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "USUARIO_INACTIVO", "mensaje": "La cuenta de usuario está desactivada", "codigo": 403},
        )

    return user


class RoleChecker:
    """
    Dependencia para verificar que el usuario tenga uno de los roles permitidos.
    Uso: Depends(RoleChecker([RolUsuario.ADMIN, RolUsuario.SUPERADMIN]))
    """

    def __init__(self, allowed_roles: List[RolUsuario]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.rol not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "PERMISO_DENEGADO",
                    "mensaje": f"Se requiere rol: {', '.join(r.value for r in self.allowed_roles)}",
                    "codigo": 403,
                },
            )
        return current_user


# Atajos comunes de roles
require_admin = RoleChecker([RolUsuario.SUPERADMIN, RolUsuario.ADMIN])
require_superadmin = RoleChecker([RolUsuario.SUPERADMIN])
require_tecnico = RoleChecker([RolUsuario.SUPERADMIN, RolUsuario.ADMIN, RolUsuario.TECNICO])
require_auditor = RoleChecker([RolUsuario.SUPERADMIN, RolUsuario.ADMIN, RolUsuario.AUDITOR])
