"""Router: Predicciones IA"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.prediccion_ia import PrediccionIA
from app.schemas.prediccion_ia import PrediccionIACreate, PrediccionIAResponse
from app.core.dependencies import get_current_user, require_admin
from app.core.exceptions import not_found
from app.models.usuario import Usuario

router = APIRouter(prefix="/predicciones", tags=["Predicciones IA"])


@router.get("", response_model=List[PrediccionIAResponse])
def listar(
    activo_id: Optional[UUID] = None,
    tipo: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    q = db.query(PrediccionIA)
    if activo_id:
        q = q.filter(PrediccionIA.activo_id == activo_id)
    if tipo:
        q = q.filter(PrediccionIA.tipo_prediccion == tipo)
    return q.order_by(PrediccionIA.creado_en.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=PrediccionIAResponse, status_code=201)
def crear(data: PrediccionIACreate, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    pred = PrediccionIA(**data.model_dump())
    db.add(pred)
    db.commit()
    db.refresh(pred)
    return pred


@router.get("/{id}", response_model=PrediccionIAResponse)
def obtener(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    pred = db.query(PrediccionIA).filter(PrediccionIA.id == id).first()
    if not pred:
        not_found("Predicción", str(id))
    return pred
