"""Router: Sincronización offline"""

from typing import List
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.cola_sincronizacion import ColaSincronizacion
from app.models.conflicto_sincronizacion import ConflictoSincronizacion
from app.models.enums import EstadoSincronizacion
from app.schemas.sincronizacion import SyncPushRequest, SyncItemResponse, ConflictoResponse, ConflictoResolverRequest
from app.core.dependencies import get_current_user, require_admin
from app.core.exceptions import not_found
from app.models.usuario import Usuario

router = APIRouter(prefix="/sincronizacion", tags=["Sincronización Offline"])


@router.post("/push", response_model=List[SyncItemResponse], status_code=201)
def push(data: SyncPushRequest, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """Recibe un lote de operaciones offline desde un dispositivo."""
    results = []
    for item in data.items:
        sync = ColaSincronizacion(
            dispositivo_id=item.dispositivo_id,
            usuario_id=current_user.id,
            nombre_entidad=item.nombre_entidad,
            entidad_id=item.entidad_id,
            operacion=item.operacion,
            payload=item.payload,
            estado=EstadoSincronizacion.PENDIENTE,
        )
        db.add(sync)
        db.flush()
        results.append(sync)
    db.commit()
    for r in results:
        db.refresh(r)
    return results


@router.get("/conflictos", response_model=List[ConflictoResponse])
def listar_conflictos(db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    return db.query(ConflictoSincronizacion).filter(
        ConflictoSincronizacion.resuelto_en.is_(None)
    ).order_by(ConflictoSincronizacion.creado_en.desc()).all()


@router.put("/conflictos/{id}/resolver", response_model=ConflictoResponse)
def resolver_conflicto(id: UUID, data: ConflictoResolverRequest, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    conflicto = db.query(ConflictoSincronizacion).filter(ConflictoSincronizacion.id == id).first()
    if not conflicto:
        not_found("Conflicto", str(id))
    conflicto.resuelto_por = current_user.id
    conflicto.resuelto_en = datetime.now(timezone.utc)
    conflicto.notas_resolucion = data.notas_resolucion
    db.commit()
    db.refresh(conflicto)
    return conflicto
