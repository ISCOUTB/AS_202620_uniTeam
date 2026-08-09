"""
Servicio de autenticación: registro, login, refresh, logout.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.sesion_autenticacion import SesionAutenticacion
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import bad_request, not_found
from app.schemas.auth import RegisterRequest, LoginRequest
from app.config import settings
from datetime import timedelta


def register_user(db: Session, data: RegisterRequest) -> Usuario:
    """Registra un usuario nuevo."""
    existing = db.query(Usuario).filter(Usuario.correo == data.correo).first()
    if existing:
        bad_request("Ya existe un usuario con ese correo electrónico", "CORREO_DUPLICADO")

    user = Usuario(
        correo=data.correo,
        hash_contrasena=hash_password(data.contrasena),
        nombre_completo=data.nombre_completo,
        rol=data.rol,
        departamento_id=data.departamento_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, data: LoginRequest) -> dict:
    """Autentica usuario y retorna tokens."""
    user = db.query(Usuario).filter(Usuario.correo == data.correo).first()
    if not user or not verify_password(data.contrasena, user.hash_contrasena):
        bad_request("Correo o contraseña incorrectos", "CREDENCIALES_INVALIDAS")

    if not user.esta_activo:
        bad_request("La cuenta está desactivada", "CUENTA_INACTIVA")

    # Generar tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Guardar sesión de refresh
    session = SesionAutenticacion(
        usuario_id=user.id,
        hash_token_refresh=hash_password(refresh_token),
        expira_en=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(session)

    # Actualizar último login
    user.ultimo_inicio_sesion_en = datetime.now(timezone.utc)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(db: Session, refresh_token: str) -> dict:
    """Genera nuevo access token a partir de un refresh token válido."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        bad_request("Refresh token inválido o expirado", "REFRESH_INVALIDO")

    user_id = payload.get("sub")
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user or not user.esta_activo:
        bad_request("Usuario no válido", "USUARIO_INVALIDO")

    new_access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def logout_user(db: Session, user_id: str) -> None:
    """Revoca todas las sesiones activas del usuario."""
    db.query(SesionAutenticacion).filter(
        SesionAutenticacion.usuario_id == user_id,
        SesionAutenticacion.revocado_en.is_(None),
    ).update({"revocado_en": datetime.now(timezone.utc)})
    db.commit()
