"""Router: Departamentos"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.departamento import Departamento
from app.schemas.departamento import DepartamentoCreate, DepartamentoUpdate, DepartamentoResponse
from app.core.dependencies import get_current_user, require_admin
from app.core.exceptions import not_found
from app.models.usuario import Usuario

router = APIRouter(prefix="/departamentos", tags=["Departamentos"])


@router.get("", response_model=List[DepartamentoResponse])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return db.query(Departamento).order_by(Departamento.nombre).all()


@router.post("", response_model=DepartamentoResponse, status_code=201)
def crear(data: DepartamentoCreate, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    dep = Departamento(**data.model_dump())
    db.add(dep)
    db.commit()
    db.refresh(dep)
    return dep


@router.get("/{id}", response_model=DepartamentoResponse)
def obtener(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    dep = db.query(Departamento).filter(Departamento.id == id).first()
    if not dep:
        not_found("Departamento", str(id))
    return dep


@router.put("/{id}", response_model=DepartamentoResponse)
def actualizar(id: UUID, data: DepartamentoUpdate, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    dep = db.query(Departamento).filter(Departamento.id == id).first()
    if not dep:
        not_found("Departamento", str(id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(dep, key, value)
    db.commit()
    db.refresh(dep)
    return dep


@router.delete("/{id}", status_code=204)
def eliminar(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    dep = db.query(Departamento).filter(Departamento.id == id).first()
    if not dep:
        not_found("Departamento", str(id))
    dep.esta_activo = False
    db.commit()
    return None
