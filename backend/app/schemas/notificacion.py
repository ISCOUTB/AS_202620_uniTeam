"""Schemas: Notificaciones"""

from pydantic import BaseModel
from typing import Optional, Any, Dict
from uuid import UUID
from datetime import datetime
from app.models.enums import CanalNotificacion


class NotificacionCreate(BaseModel):
    usuario_id: UUID
    tipo: str
    titulo: str
    mensaje: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class NotificacionResponse(BaseModel):
    id: UUID
    usuario_id: UUID
    tipo: str
    titulo: str
    mensaje: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    esta_leido: bool
    creado_en: datetime
    leido_en: Optional[datetime] = None

    class Config:
        from_attributes = True


class EntregaNotificacionResponse(BaseModel):
    id: UUID
    notificacion_id: UUID
    canal: CanalNotificacion
    id_externo: Optional[str] = None
    entregado_en: Optional[datetime] = None
    fallido_en: Optional[datetime] = None
    mensaje_error: Optional[str] = None

    class Config:
        from_attributes = True
