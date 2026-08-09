"""Router: Integraciones"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.trabajo_integracion import TrabajoIntegracion
from app.schemas.integracion import IntegracionCreate, IntegracionResponse
from app.core.dependencies import require_admin
from app.core.exceptions import not_found
from app.models.usuario import Usuario

router = APIRouter(prefix="/integraciones", tags=["Integraciones"])


@router.get("", response_model=List[IntegracionResponse])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    return db.query(TrabajoIntegracion).order_by(TrabajoIntegracion.creado_en.desc()).limit(100).all()


@router.post("", response_model=IntegracionResponse, status_code=201)
def crear(data: IntegracionCreate, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    job = TrabajoIntegracion(**data.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/{id}", response_model=IntegracionResponse)
def obtener(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    job = db.query(TrabajoIntegracion).filter(TrabajoIntegracion.id == id).first()
    if not job:
        not_found("Trabajo de integración", str(id))
    return job
