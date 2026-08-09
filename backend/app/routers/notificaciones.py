"""Router: Notificaciones"""

from typing import List
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notificacion import Notificacion
from app.schemas.notificacion import NotificacionCreate, NotificacionResponse
from app.core.dependencies import get_current_user, require_admin
from app.core.exceptions import not_found
from app.models.usuario import Usuario

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.get("", response_model=List[NotificacionResponse])
def listar(
    solo_no_leidas: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    q = db.query(Notificacion).filter(Notificacion.usuario_id == current_user.id)
    if solo_no_leidas:
        q = q.filter(Notificacion.esta_leido == False)
    return q.order_by(Notificacion.creado_en.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=NotificacionResponse, status_code=201)
def crear(data: NotificacionCreate, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    notif = Notificacion(**data.model_dump())
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


@router.put("/{id}/leer", response_model=NotificacionResponse)
def marcar_leida(id: UUID, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    notif = db.query(Notificacion).filter(Notificacion.id == id, Notificacion.usuario_id == current_user.id).first()
    if not notif:
        not_found("Notificación", str(id))
    notif.esta_leido = True
    notif.leido_en = datetime.now(timezone.utc)
    db.commit()
    db.refresh(notif)
    return notif


@router.put("/leer-todas", status_code=204)
def marcar_todas_leidas(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    db.query(Notificacion).filter(
        Notificacion.usuario_id == current_user.id,
        Notificacion.esta_leido == False,
    ).update({"esta_leido": True, "leido_en": datetime.now(timezone.utc)})
    db.commit()
    return None
