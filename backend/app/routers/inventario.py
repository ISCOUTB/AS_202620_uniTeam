"""Router: Inventario (sesiones + escaneos)"""

from typing import List
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.sesion_inventario import SesionInventario
from app.models.item_inventario import ItemInventario
from app.models.activo import Activo
from app.models.enums import EstadoSesionInventario, ResultadoEscaneoInventario
from app.schemas.inventario import SesionInventarioCreate, SesionInventarioResponse, SesionInventarioDetalleResponse, ScanRequest, ItemInventarioResponse
from app.core.dependencies import get_current_user, require_tecnico
from app.core.exceptions import not_found, bad_request
from app.models.usuario import Usuario

router = APIRouter(prefix="/inventario", tags=["Inventario"])


def _generar_numero_sesion(db: Session) -> str:
    fecha = datetime.now(timezone.utc).strftime("%Y%m%d")
    count = db.query(SesionInventario).filter(SesionInventario.numero_sesion.like(f"INV-{fecha}-%")).count()
    return f"INV-{fecha}-{count + 1:04d}"


@router.get("/sesiones", response_model=List[SesionInventarioResponse])
def listar_sesiones(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return db.query(SesionInventario).order_by(SesionInventario.iniciado_en.desc()).all()


@router.post("/sesiones", response_model=SesionInventarioResponse, status_code=201)
def crear_sesion(data: SesionInventarioCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(require_tecnico)):
    # Contar activos esperados en esa ubicación
    total_esperado = db.query(Activo).filter(
        Activo.ubicacion_actual_id == data.ubicacion_id,
        Activo.eliminado_en.is_(None),
    ).count()

    sesion = SesionInventario(
        numero_sesion=_generar_numero_sesion(db),
        ubicacion_id=data.ubicacion_id,
        iniciado_por=current_user.id,
        total_esperado=total_esperado,
    )
    db.add(sesion)
    db.commit()
    db.refresh(sesion)
    return sesion


@router.get("/sesiones/{id}", response_model=SesionInventarioDetalleResponse)
def obtener_sesion(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    sesion = db.query(SesionInventario).filter(SesionInventario.id == id).first()
    if not sesion:
        not_found("Sesión de inventario", str(id))
    return sesion


@router.post("/sesiones/{id}/scan", response_model=ItemInventarioResponse, status_code=201)
def registrar_escaneo(id: UUID, data: ScanRequest, db: Session = Depends(get_db), current_user: Usuario = Depends(require_tecnico)):
    sesion = db.query(SesionInventario).filter(SesionInventario.id == id).first()
    if not sesion:
        not_found("Sesión de inventario", str(id))
    if sesion.estado == EstadoSesionInventario.CERRADA:
        bad_request("La sesión ya está cerrada", "SESION_CERRADA")

    # Buscar activo
    activo = None
    resultado = ResultadoEscaneoInventario.EXTRA
    ubicacion_esperada_id = None

    if data.activo_id:
        activo = db.query(Activo).filter(Activo.id == data.activo_id).first()
    elif data.codigo_escaneado:
        activo = db.query(Activo).filter(
            (Activo.codigo == data.codigo_escaneado) |
            (Activo.codigo_barras == data.codigo_escaneado) |
            (Activo.etiqueta_rfid == data.codigo_escaneado) |
            (Activo.codigo_qr == data.codigo_escaneado)
        ).first()

    if activo:
        ubicacion_esperada_id = activo.ubicacion_actual_id
        if activo.ubicacion_actual_id == sesion.ubicacion_id:
            resultado = ResultadoEscaneoInventario.ENCONTRADO
        else:
            resultado = ResultadoEscaneoInventario.UBICACION_INCORRECTA

    # Actualizar estado sesión
    if sesion.estado == EstadoSesionInventario.ABIERTA:
        sesion.estado = EstadoSesionInventario.EN_PROGRESO

    item = ItemInventario(
        sesion_id=id,
        activo_id=activo.id if activo else None,
        codigo_escaneado=data.codigo_escaneado,
        resultado_escaneo=resultado,
        ubicacion_esperada_id=ubicacion_esperada_id,
        ubicacion_encontrada_id=sesion.ubicacion_id,
        escaneado_por=current_user.id,
        id_evento_cliente=data.id_evento_cliente,
        notas=data.notas,
    )
    db.add(item)
    sesion.total_escaneado += 1
    if resultado == ResultadoEscaneoInventario.ENCONTRADO:
        sesion.total_encontrado += 1
    elif resultado == ResultadoEscaneoInventario.EXTRA:
        sesion.total_extra += 1

    db.commit()
    db.refresh(item)
    return item


@router.put("/sesiones/{id}/cerrar", response_model=SesionInventarioResponse)
def cerrar_sesion(id: UUID, db: Session = Depends(get_db), current_user: Usuario = Depends(require_tecnico)):
    sesion = db.query(SesionInventario).filter(SesionInventario.id == id).first()
    if not sesion:
        not_found("Sesión de inventario", str(id))
    if sesion.estado == EstadoSesionInventario.CERRADA:
        bad_request("La sesión ya está cerrada", "SESION_CERRADA")

    # Calcular faltantes
    sesion.total_faltante = sesion.total_esperado - sesion.total_encontrado
    if sesion.total_faltante < 0:
        sesion.total_faltante = 0
    sesion.estado = EstadoSesionInventario.CERRADA
    sesion.cerrado_por = current_user.id
    sesion.cerrado_en = datetime.now(timezone.utc)
    db.commit()
    db.refresh(sesion)
    return sesion


@router.get("/sesiones/{id}/reporte", response_model=SesionInventarioDetalleResponse)
def reporte_sesion(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    sesion = db.query(SesionInventario).filter(SesionInventario.id == id).first()
    if not sesion:
        not_found("Sesión de inventario", str(id))
    return sesion
