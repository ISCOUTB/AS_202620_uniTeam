"""Router: Categorías de Activos"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.categoria_activo import CategoriaActivo
from app.schemas.categoria_activo import CategoriaActivoCreate, CategoriaActivoUpdate, CategoriaActivoResponse, CategoriaArbolResponse
from app.core.dependencies import get_current_user, require_admin
from app.core.exceptions import not_found
from app.models.usuario import Usuario

router = APIRouter(prefix="/categorias", tags=["Categorías de Activos"])


def _build_tree(categorias: List[CategoriaActivo], padre_id=None) -> List[dict]:
    tree = []
    for c in categorias:
        if c.padre_id == padre_id:
            node = {
                "id": c.id, "nombre": c.nombre, "codigo": c.codigo,
                "anos_depreciacion": c.anos_depreciacion,
                "intervalo_mantenimiento_dias": c.intervalo_mantenimiento_dias,
                "padre_id": c.padre_id, "creado_en": c.creado_en,
                "actualizado_en": c.actualizado_en,
                "subcategorias": _build_tree(categorias, c.id),
            }
            tree.append(node)
    return tree


@router.get("", response_model=List[CategoriaActivoResponse])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return db.query(CategoriaActivo).order_by(CategoriaActivo.nombre).all()


@router.get("/arbol", response_model=List[CategoriaArbolResponse])
def arbol(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    all_cats = db.query(CategoriaActivo).all()
    return _build_tree(all_cats, None)


@router.post("", response_model=CategoriaActivoResponse, status_code=201)
def crear(data: CategoriaActivoCreate, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    cat = CategoriaActivo(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.get("/{id}", response_model=CategoriaActivoResponse)
def obtener(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    cat = db.query(CategoriaActivo).filter(CategoriaActivo.id == id).first()
    if not cat:
        not_found("Categoría", str(id))
    return cat


@router.put("/{id}", response_model=CategoriaActivoResponse)
def actualizar(id: UUID, data: CategoriaActivoUpdate, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    cat = db.query(CategoriaActivo).filter(CategoriaActivo.id == id).first()
    if not cat:
        not_found("Categoría", str(id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, key, value)
    db.commit()
    db.refresh(cat)
    return cat
