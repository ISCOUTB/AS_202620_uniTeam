"""Router: Ubicaciones"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.ubicacion import Ubicacion
from app.schemas.ubicacion import UbicacionCreate, UbicacionUpdate, UbicacionResponse, UbicacionArbolResponse
from app.core.dependencies import get_current_user, require_admin
from app.core.exceptions import not_found
from app.models.usuario import Usuario

router = APIRouter(prefix="/ubicaciones", tags=["Ubicaciones"])


def _build_tree(ubicaciones: List[Ubicacion], padre_id=None) -> List[dict]:
    """Construye el árbol jerárquico de ubicaciones."""
    tree = []
    for u in ubicaciones:
        if u.padre_id == padre_id:
            node = {
                "id": u.id, "nombre": u.nombre, "codigo": u.codigo,
                "edificio": u.edificio, "piso": u.piso, "padre_id": u.padre_id,
                "esta_activo": u.esta_activo, "creado_en": u.creado_en,
                "actualizado_en": u.actualizado_en,
                "hijos": _build_tree(ubicaciones, u.id),
            }
            tree.append(node)
    return tree


@router.get("", response_model=List[UbicacionResponse])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return db.query(Ubicacion).filter(Ubicacion.esta_activo == True).order_by(Ubicacion.nombre).all()


@router.get("/arbol", response_model=List[UbicacionArbolResponse])
def arbol(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    all_ubicaciones = db.query(Ubicacion).filter(Ubicacion.esta_activo == True).all()
    return _build_tree(all_ubicaciones, None)


@router.post("", response_model=UbicacionResponse, status_code=201)
def crear(data: UbicacionCreate, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    ub = Ubicacion(**data.model_dump())
    db.add(ub)
    db.commit()
    db.refresh(ub)
    return ub


@router.get("/{id}", response_model=UbicacionResponse)
def obtener(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    ub = db.query(Ubicacion).filter(Ubicacion.id == id).first()
    if not ub:
        not_found("Ubicación", str(id))
    return ub


@router.put("/{id}", response_model=UbicacionResponse)
def actualizar(id: UUID, data: UbicacionUpdate, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    ub = db.query(Ubicacion).filter(Ubicacion.id == id).first()
    if not ub:
        not_found("Ubicación", str(id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(ub, key, value)
    db.commit()
    db.refresh(ub)
    return ub


@router.delete("/{id}", status_code=204)
def eliminar(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    ub = db.query(Ubicacion).filter(Ubicacion.id == id).first()
    if not ub:
        not_found("Ubicación", str(id))
    ub.esta_activo = False
    db.commit()
    return None
