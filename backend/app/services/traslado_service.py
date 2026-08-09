"""
Servicio de traslados: lógica de negocio para el flujo completo.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.traslado import Traslado
from app.models.activo import Activo
from app.models.movimiento_activo import MovimientoActivo
from app.models.enums import EstadoTraslado, EstadoActivo, TipoMovimientoActivo
from app.core.exceptions import bad_request, not_found, forbidden
from app.schemas.traslado import TrasladoCreate


def generar_numero_traslado(db: Session) -> str:
    """Genera un número de traslado único con formato TRS-YYYYMMDD-XXXX."""
    fecha = datetime.now(timezone.utc).strftime("%Y%m%d")
    count = db.query(Traslado).filter(Traslado.numero_traslado.like(f"TRS-{fecha}-%")).count()
    return f"TRS-{fecha}-{count + 1:04d}"


def crear_traslado(db: Session, data: TrasladoCreate, solicitado_por_id: uuid.UUID) -> Traslado:
    """Crea una nueva solicitud de traslado."""
    activo = db.query(Activo).filter(Activo.id == data.activo_id, Activo.eliminado_en.is_(None)).first()
    if not activo:
        not_found("Activo", str(data.activo_id))

    if activo.estado == EstadoActivo.DESINCORPORADO:
        bad_request("No se puede trasladar un activo desincorporado", "ACTIVO_DESINCORPORADO")

    traslado = Traslado(
        numero_traslado=generar_numero_traslado(db),
        activo_id=data.activo_id,
        ubicacion_origen_id=activo.ubicacion_actual_id,
        ubicacion_destino_id=data.ubicacion_destino_id,
        usuario_origen_id=activo.asignado_a_usuario_id,
        usuario_destino_id=data.usuario_destino_id,
        motivo=data.motivo,
        fecha_esperada=data.fecha_esperada,
        solicitado_por=solicitado_por_id,
    )
    db.add(traslado)
    db.commit()
    db.refresh(traslado)
    return traslado


def aprobar_traslado(db: Session, traslado_id: uuid.UUID, aprobado_por_id: uuid.UUID) -> Traslado:
    """Aprueba un traslado pendiente."""
    traslado = db.query(Traslado).filter(Traslado.id == traslado_id).first()
    if not traslado:
        not_found("Traslado", str(traslado_id))

    if traslado.estado != EstadoTraslado.PENDIENTE:
        bad_request(f"El traslado no está PENDIENTE (estado actual: {traslado.estado.value})", "ESTADO_INVALIDO")

    traslado.estado = EstadoTraslado.APROBADO
    traslado.aprobado_por = aprobado_por_id
    traslado.aprobado_en = datetime.now(timezone.utc)

    # Marcar activo como EN_TRASLADO
    activo = db.query(Activo).filter(Activo.id == traslado.activo_id).first()
    if activo:
        activo.estado = EstadoActivo.EN_TRASLADO

    db.commit()
    db.refresh(traslado)
    return traslado


def rechazar_traslado(db: Session, traslado_id: uuid.UUID, aprobado_por_id: uuid.UUID, motivo_rechazo: str) -> Traslado:
    """Rechaza un traslado pendiente."""
    traslado = db.query(Traslado).filter(Traslado.id == traslado_id).first()
    if not traslado:
        not_found("Traslado", str(traslado_id))

    if traslado.estado != EstadoTraslado.PENDIENTE:
        bad_request(f"El traslado no está PENDIENTE (estado actual: {traslado.estado.value})", "ESTADO_INVALIDO")

    traslado.estado = EstadoTraslado.RECHAZADO
    traslado.aprobado_por = aprobado_por_id
    traslado.aprobado_en = datetime.now(timezone.utc)
    traslado.motivo_rechazo = motivo_rechazo
    db.commit()
    db.refresh(traslado)
    return traslado


def poner_en_transito(db: Session, traslado_id: uuid.UUID) -> Traslado:
    """Marca un traslado aprobado como en tránsito."""
    traslado = db.query(Traslado).filter(Traslado.id == traslado_id).first()
    if not traslado:
        not_found("Traslado", str(traslado_id))

    if traslado.estado != EstadoTraslado.APROBADO:
        bad_request(f"El traslado debe estar APROBADO para pasar a EN_TRANSITO", "ESTADO_INVALIDO")

    traslado.estado = EstadoTraslado.EN_TRANSITO
    db.commit()
    db.refresh(traslado)
    return traslado


def confirmar_traslado(db: Session, traslado_id: uuid.UUID, confirmado_por_id: uuid.UUID) -> Traslado:
    """
    Confirma la recepción del activo y completa el traslado.
    Nota: El trigger de PostgreSQL `fn_completar_traslado_aplicar_activo`
    actualiza automáticamente el activo y crea el movimiento.
    """
    traslado = db.query(Traslado).filter(Traslado.id == traslado_id).first()
    if not traslado:
        not_found("Traslado", str(traslado_id))

    if traslado.estado not in (EstadoTraslado.APROBADO, EstadoTraslado.EN_TRANSITO):
        bad_request("El traslado debe estar APROBADO o EN_TRANSITO para confirmar", "ESTADO_INVALIDO")

    traslado.estado = EstadoTraslado.COMPLETADO
    traslado.confirmado_por = confirmado_por_id
    traslado.confirmado_en = datetime.now(timezone.utc)
    traslado.completado_en = datetime.now(timezone.utc)

    db.commit()
    db.refresh(traslado)
    return traslado


def cancelar_traslado(db: Session, traslado_id: uuid.UUID, cancelado_por_id: uuid.UUID) -> Traslado:
    """Cancela un traslado que no ha sido completado."""
    traslado = db.query(Traslado).filter(Traslado.id == traslado_id).first()
    if not traslado:
        not_found("Traslado", str(traslado_id))

    if traslado.estado in (EstadoTraslado.COMPLETADO, EstadoTraslado.CANCELADO):
        bad_request("No se puede cancelar un traslado ya completado o cancelado", "ESTADO_INVALIDO")

    # Si el activo estaba EN_TRASLADO, restaurar a ACTIVO
    if traslado.estado in (EstadoTraslado.APROBADO, EstadoTraslado.EN_TRANSITO):
        activo = db.query(Activo).filter(Activo.id == traslado.activo_id).first()
        if activo and activo.estado == EstadoActivo.EN_TRASLADO:
            activo.estado = EstadoActivo.ACTIVO

    traslado.estado = EstadoTraslado.CANCELADO
    db.commit()
    db.refresh(traslado)
    return traslado
