"""Router: Mantenimiento (planes + órdenes)"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.orden_mantenimiento import OrdenMantenimiento
from app.models.enums import EstadoMantenimiento
from app.schemas.mantenimiento import (
    PlanMantenimientoCreate, PlanMantenimientoUpdate, PlanMantenimientoResponse,
    OrdenMantenimientoCreate, OrdenMantenimientoUpdate, OrdenMantenimientoResponse,
)
from app.core.dependencies import get_current_user, require_admin, require_tecnico
from app.core.exceptions import not_found
from app.models.usuario import Usuario

router = APIRouter(prefix="/mantenimiento", tags=["Mantenimiento"])

# ─── Planes ───

@router.get("/planes", response_model=List[PlanMantenimientoResponse])
def listar_planes(activo_id: Optional[UUID] = None, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    q = db.query(PlanMantenimiento)
    if activo_id:
        q = q.filter(PlanMantenimiento.activo_id == activo_id)
    return q.order_by(PlanMantenimiento.proxima_fecha).all()


@router.post("/planes", response_model=PlanMantenimientoResponse, status_code=201)
def crear_plan(data: PlanMantenimientoCreate, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    plan = PlanMantenimiento(**data.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.put("/planes/{id}", response_model=PlanMantenimientoResponse)
def actualizar_plan(id: UUID, data: PlanMantenimientoUpdate, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    plan = db.query(PlanMantenimiento).filter(PlanMantenimiento.id == id).first()
    if not plan:
        not_found("Plan de mantenimiento", str(id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan

# ─── Órdenes ───

@router.get("/ordenes", response_model=List[OrdenMantenimientoResponse])
def listar_ordenes(
    activo_id: Optional[UUID] = None,
    estado: Optional[EstadoMantenimiento] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    q = db.query(OrdenMantenimiento)
    if activo_id:
        q = q.filter(OrdenMantenimiento.activo_id == activo_id)
    if estado:
        q = q.filter(OrdenMantenimiento.estado == estado)
    return q.order_by(OrdenMantenimiento.abierto_en.desc()).offset(skip).limit(limit).all()


@router.post("/ordenes", response_model=OrdenMantenimientoResponse, status_code=201)
def crear_orden(data: OrdenMantenimientoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(require_tecnico)):
    orden = OrdenMantenimiento(**data.model_dump(), abierto_por=current_user.id)
    db.add(orden)
    db.commit()
    db.refresh(orden)
    return orden


@router.get("/ordenes/{id}", response_model=OrdenMantenimientoResponse)
def obtener_orden(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    orden = db.query(OrdenMantenimiento).filter(OrdenMantenimiento.id == id).first()
    if not orden:
        not_found("Orden de mantenimiento", str(id))
    return orden


@router.put("/ordenes/{id}", response_model=OrdenMantenimientoResponse)
def actualizar_orden(id: UUID, data: OrdenMantenimientoUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(require_tecnico)):
    orden = db.query(OrdenMantenimiento).filter(OrdenMantenimiento.id == id).first()
    if not orden:
        not_found("Orden de mantenimiento", str(id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(orden, key, value)
    if data.estado == EstadoMantenimiento.COMPLETADA or data.estado == EstadoMantenimiento.CANCELADA:
        orden.cerrado_por = current_user.id
        orden.cerrado_en = datetime.now(timezone.utc)
    db.commit()
    db.refresh(orden)
    return orden
