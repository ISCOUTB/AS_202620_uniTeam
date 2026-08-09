"""Router: Autenticación"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, RefreshRequest, MeResponse
from app.services.auth_service import register_user, authenticate_user, refresh_access_token, logout_user
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=MeResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Registrar un nuevo usuario."""
    user = register_user(db, data)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Iniciar sesión y obtener tokens JWT."""
    return authenticate_user(db, data)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    """Renovar el access token usando un refresh token."""
    return refresh_access_token(db, data.refresh_token)


@router.post("/logout", status_code=204)
def logout(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cerrar sesión (revocar tokens de refresh)."""
    logout_user(db, str(current_user.id))
    return None


@router.get("/me", response_model=MeResponse)
def me(current_user: Usuario = Depends(get_current_user)):
    """Obtener perfil del usuario autenticado."""
    return current_user
