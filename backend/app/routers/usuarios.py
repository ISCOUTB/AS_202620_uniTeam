"""Router: Usuarios"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.models.enums import RolUsuario
from app.schemas.usuario import UsuarioResponse, UsuarioUpdate, UsuarioRolUpdate, UsuarioEstadoUpdate
from app.core.dependencies import get_current_user, require_admin, require_superadmin
from app.core.exceptions import not_found, forbidden

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("", response_model=List[UsuarioResponse])
def listar(
    rol: Optional[RolUsuario] = None,
    esta_activo: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    q = db.query(Usuario)
    if rol:
        q = q.filter(Usuario.rol == rol)
    if esta_activo is not None:
        q = q.filter(Usuario.esta_activo == esta_activo)
    return q.order_by(Usuario.nombre_completo).offset(skip).limit(limit).all()


@router.get("/{id}", response_model=UsuarioResponse)
def obtener(id: UUID, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if str(current_user.id) != str(id) and current_user.rol not in (RolUsuario.ADMIN, RolUsuario.SUPERADMIN):
        forbidden("Solo puedes ver tu propio perfil")
    user = db.query(Usuario).filter(Usuario.id == id).first()
    if not user:
        not_found("Usuario", str(id))
    return user


@router.put("/{id}", response_model=UsuarioResponse)
def actualizar(id: UUID, data: UsuarioUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if str(current_user.id) != str(id) and current_user.rol not in (RolUsuario.ADMIN, RolUsuario.SUPERADMIN):
        forbidden("Solo puedes editar tu propio perfil")
    user = db.query(Usuario).filter(Usuario.id == id).first()
    if not user:
        not_found("Usuario", str(id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{id}/rol", response_model=UsuarioResponse)
def cambiar_rol(id: UUID, data: UsuarioRolUpdate, db: Session = Depends(get_db), _: Usuario = Depends(require_superadmin)):
    user = db.query(Usuario).filter(Usuario.id == id).first()
    if not user:
        not_found("Usuario", str(id))
    user.rol = data.rol
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{id}/estado", response_model=UsuarioResponse)
def cambiar_estado(id: UUID, data: UsuarioEstadoUpdate, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    user = db.query(Usuario).filter(Usuario.id == id).first()
    if not user:
        not_found("Usuario", str(id))
    user.esta_activo = data.esta_activo
    db.commit()
    db.refresh(user)
    return user
