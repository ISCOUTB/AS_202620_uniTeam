"""Router: Activos"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.activo import Activo
from app.models.movimiento_activo import MovimientoActivo
from app.models.enums import EstadoActivo, TipoMovimientoActivo
from app.schemas.activo import ActivoCreate, ActivoUpdate, ActivoResponse, ActivoListResponse, ActivoEstadoUpdate, ActivoAsignarUpdate
from app.schemas.movimiento_activo import MovimientoActivoResponse
from app.core.dependencies import get_current_user, require_admin
from app.core.exceptions import not_found
from app.models.usuario import Usuario

router = APIRouter(prefix="/activos", tags=["Activos"])


@router.get("", response_model=ActivoListResponse)
def listar(
    estado: Optional[EstadoActivo] = None,
    categoria_id: Optional[UUID] = None,
    ubicacion_id: Optional[UUID] = None,
    busqueda: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    q = db.query(Activo).filter(Activo.eliminado_en.is_(None))
    if estado:
        q = q.filter(Activo.estado == estado)
    if categoria_id:
        q = q.filter(Activo.categoria_id == categoria_id)
    if ubicacion_id:
        q = q.filter(Activo.ubicacion_actual_id == ubicacion_id)
    if busqueda:
        like = f"%{busqueda}%"
        q = q.filter(
            (Activo.nombre.ilike(like)) | (Activo.codigo.ilike(like)) |
            (Activo.marca.ilike(like)) | (Activo.numero_serie.ilike(like))
        )
    total = q.count()
    items = q.order_by(Activo.nombre).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.post("", response_model=ActivoResponse, status_code=201)
def crear(data: ActivoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    activo = Activo(**data.model_dump(), creado_por=current_user.id)
    db.add(activo)

    # Registrar movimiento de creación
    mov = MovimientoActivo(
        activo_id=activo.id,
        tipo_movimiento=TipoMovimientoActivo.CREACION,
        ubicacion_hasta_id=data.ubicacion_actual_id,
        usuario_hasta_id=data.asignado_a_usuario_id,
        estado_hasta=EstadoActivo.ACTIVO,
        realizado_por=current_user.id,
        notas="Activo registrado en el sistema",
    )
    db.add(mov)
    db.commit()
    db.refresh(activo)
    return activo


@router.get("/escanear/{codigo}")
def escanear(codigo: str, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    """Busca un activo por código QR, código de barras o etiqueta RFID."""
    activo = db.query(Activo).filter(
        Activo.eliminado_en.is_(None),
        (Activo.codigo == codigo) | (Activo.codigo_barras == codigo) |
        (Activo.etiqueta_rfid == codigo) | (Activo.codigo_qr == codigo)
    ).first()
    if not activo:
        not_found("Activo", codigo)
    return ActivoResponse.model_validate(activo)


@router.get("/{id}", response_model=ActivoResponse)
def obtener(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    activo = db.query(Activo).filter(Activo.id == id, Activo.eliminado_en.is_(None)).first()
    if not activo:
        not_found("Activo", str(id))
    return activo


@router.put("/{id}", response_model=ActivoResponse)
def actualizar(id: UUID, data: ActivoUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    activo = db.query(Activo).filter(Activo.id == id, Activo.eliminado_en.is_(None)).first()
    if not activo:
        not_found("Activo", str(id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(activo, key, value)
    activo.version += 1

    mov = MovimientoActivo(
        activo_id=activo.id,
        tipo_movimiento=TipoMovimientoActivo.ACTUALIZACION,
        realizado_por=current_user.id,
        notas="Datos del activo actualizados",
    )
    db.add(mov)
    db.commit()
    db.refresh(activo)
    return activo


@router.delete("/{id}", status_code=204)
def eliminar(id: UUID, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    activo = db.query(Activo).filter(Activo.id == id, Activo.eliminado_en.is_(None)).first()
    if not activo:
        not_found("Activo", str(id))
    from datetime import datetime, timezone
    activo.eliminado_en = datetime.now(timezone.utc)
    activo.estado = EstadoActivo.DESINCORPORADO
    db.commit()
    return None


@router.patch("/{id}/estado", response_model=ActivoResponse)
def cambiar_estado(id: UUID, data: ActivoEstadoUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    activo = db.query(Activo).filter(Activo.id == id, Activo.eliminado_en.is_(None)).first()
    if not activo:
        not_found("Activo", str(id))
    estado_anterior = activo.estado
    activo.estado = data.estado
    activo.version += 1

    mov = MovimientoActivo(
        activo_id=activo.id,
        tipo_movimiento=TipoMovimientoActivo.CAMBIO_ESTADO,
        estado_desde=estado_anterior,
        estado_hasta=data.estado,
        realizado_por=current_user.id,
        notas=data.notas or f"Estado cambiado de {estado_anterior.value} a {data.estado.value}",
    )
    db.add(mov)
    db.commit()
    db.refresh(activo)
    return activo


@router.patch("/{id}/asignar", response_model=ActivoResponse)
def asignar(id: UUID, data: ActivoAsignarUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    activo = db.query(Activo).filter(Activo.id == id, Activo.eliminado_en.is_(None)).first()
    if not activo:
        not_found("Activo", str(id))
    usuario_anterior = activo.asignado_a_usuario_id
    activo.asignado_a_usuario_id = data.asignado_a_usuario_id
    activo.version += 1

    mov = MovimientoActivo(
        activo_id=activo.id,
        tipo_movimiento=TipoMovimientoActivo.ASIGNACION,
        usuario_desde_id=usuario_anterior,
        usuario_hasta_id=data.asignado_a_usuario_id,
        realizado_por=current_user.id,
        notas=data.notas or "Activo reasignado",
    )
    db.add(mov)
    db.commit()
    db.refresh(activo)
    return activo


@router.get("/{id}/historial", response_model=List[MovimientoActivoResponse])
def historial(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    activo = db.query(Activo).filter(Activo.id == id).first()
    if not activo:
        not_found("Activo", str(id))
    return db.query(MovimientoActivo).filter(
        MovimientoActivo.activo_id == id
    ).order_by(MovimientoActivo.creado_en.desc()).all()
