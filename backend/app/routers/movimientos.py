"""Router: Movimientos de Activos (solo lectura – historial inmutable)"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.movimiento_activo import MovimientoActivo
from app.models.enums import TipoMovimientoActivo
from app.schemas.movimiento_activo import MovimientoActivoResponse
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/movimientos", tags=["Movimientos (Historial)"])


@router.get("", response_model=List[MovimientoActivoResponse])
def listar(
    tipo: Optional[TipoMovimientoActivo] = None,
    activo_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    q = db.query(MovimientoActivo)
    if tipo:
        q = q.filter(MovimientoActivo.tipo_movimiento == tipo)
    if activo_id:
        q = q.filter(MovimientoActivo.activo_id == activo_id)
    return q.order_by(MovimientoActivo.creado_en.desc()).offset(skip).limit(limit).all()


@router.get("/{activo_id}", response_model=List[MovimientoActivoResponse])
def historial_activo(activo_id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return db.query(MovimientoActivo).filter(
        MovimientoActivo.activo_id == activo_id
    ).order_by(MovimientoActivo.creado_en.desc()).all()
