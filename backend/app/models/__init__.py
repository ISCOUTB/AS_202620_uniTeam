"""
Exporta todos los modelos ORM para que SQLAlchemy los descubra.
"""

from app.models.departamento import Departamento
from app.models.usuario import Usuario
from app.models.ubicacion import Ubicacion
from app.models.categoria_activo import CategoriaActivo
from app.models.activo import Activo
from app.models.documento_activo import DocumentoActivo
from app.models.traslado import Traslado
from app.models.movimiento_activo import MovimientoActivo
from app.models.sesion_inventario import SesionInventario
from app.models.item_inventario import ItemInventario
from app.models.cola_sincronizacion import ColaSincronizacion
from app.models.conflicto_sincronizacion import ConflictoSincronizacion
from app.models.sesion_autenticacion import SesionAutenticacion
from app.models.notificacion import Notificacion
from app.models.entrega_notificacion import EntregaNotificacion
from app.models.exportacion_reporte import ExportacionReporte
from app.models.trabajo_integracion import TrabajoIntegracion
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.orden_mantenimiento import OrdenMantenimiento
from app.models.prediccion_ia import PrediccionIA

__all__ = [
    "Departamento",
    "Usuario",
    "Ubicacion",
    "CategoriaActivo",
    "Activo",
    "DocumentoActivo",
    "Traslado",
    "MovimientoActivo",
    "SesionInventario",
    "ItemInventario",
    "ColaSincronizacion",
    "ConflictoSincronizacion",
    "SesionAutenticacion",
    "Notificacion",
    "EntregaNotificacion",
    "ExportacionReporte",
    "TrabajoIntegracion",
    "PlanMantenimiento",
    "OrdenMantenimiento",
    "PrediccionIA",
]
