"""Router: Traslados"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.traslado import Traslado
from app.models.enums import EstadoTraslado
from app.schemas.traslado import TrasladoCreate, TrasladoResponse, TrasladoRechazarRequest
from app.core.dependencies import get_current_user, require_admin
from app.core.exceptions import not_found
from app.models.usuario import Usuario
from app.services.traslado_service import (
    crear_traslado, aprobar_traslado, rechazar_traslado,
    poner_en_transito, confirmar_traslado, cancelar_traslado,
)

router = APIRouter(prefix="/traslados", tags=["Traslados"])


@router.get("", response_model=List[TrasladoResponse])
def listar(
    estado: Optional[EstadoTraslado] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    q = db.query(Traslado)
    if estado:
        q = q.filter(Traslado.estado == estado)
    return q.order_by(Traslado.creado_en.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=TrasladoResponse, status_code=201)
def crear(data: TrasladoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return crear_traslado(db, data, current_user.id)


@router.get("/{id}", response_model=TrasladoResponse)
def obtener(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    t = db.query(Traslado).filter(Traslado.id == id).first()
    if not t:
        not_found("Traslado", str(id))
    return t


@router.put("/{id}/aprobar", response_model=TrasladoResponse)
def aprobar(id: UUID, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    return aprobar_traslado(db, id, current_user.id)


@router.put("/{id}/rechazar", response_model=TrasladoResponse)
def rechazar(id: UUID, data: TrasladoRechazarRequest, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    return rechazar_traslado(db, id, current_user.id, data.motivo_rechazo)


@router.put("/{id}/en-transito", response_model=TrasladoResponse)
def en_transito(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    return poner_en_transito(db, id)


@router.put("/{id}/confirmar", response_model=TrasladoResponse)
def confirmar(id: UUID, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return confirmar_traslado(db, id, current_user.id)


@router.put("/{id}/cancelar", response_model=TrasladoResponse)
def cancelar(id: UUID, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return cancelar_traslado(db, id, current_user.id)
