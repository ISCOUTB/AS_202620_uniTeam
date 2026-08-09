"""
Enums de PostgreSQL mapeados a Python.
"""

import enum


class RolUsuario(str, enum.Enum):
    SUPERADMIN = "SUPERADMIN"
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"
    CUSTODIO = "CUSTODIO"
    TECNICO = "TECNICO"


class EstadoActivo(str, enum.Enum):
    ACTIVO = "ACTIVO"
    MANTENIMIENTO = "MANTENIMIENTO"
    DESINCORPORADO = "DESINCORPORADO"
    EN_TRASLADO = "EN_TRASLADO"
    PERDIDO = "PERDIDO"


class EstadoTraslado(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    EN_TRANSITO = "EN_TRANSITO"
    COMPLETADO = "COMPLETADO"
    CANCELADO = "CANCELADO"


class TipoMovimientoActivo(str, enum.Enum):
    TRASLADO = "TRASLADO"
    INVENTARIO = "INVENTARIO"
    ASIGNACION = "ASIGNACION"
    CAMBIO_ESTADO = "CAMBIO_ESTADO"
    MANTENIMIENTO = "MANTENIMIENTO"
    CREACION = "CREACION"
    ACTUALIZACION = "ACTUALIZACION"


class EstadoSesionInventario(str, enum.Enum):
    ABIERTA = "ABIERTA"
    EN_PROGRESO = "EN_PROGRESO"
    CERRADA = "CERRADA"


class ResultadoEscaneoInventario(str, enum.Enum):
    ENCONTRADO = "ENCONTRADO"
    FALTANTE = "FALTANTE"
    EXTRA = "EXTRA"
    UBICACION_INCORRECTA = "UBICACION_INCORRECTA"


class TipoDocumento(str, enum.Enum):
    FACTURA = "FACTURA"
    GARANTIA = "GARANTIA"
    MANUAL = "MANUAL"
    FOTO = "FOTO"
    OTRO = "OTRO"


class CanalNotificacion(str, enum.Enum):
    EN_APP = "EN_APP"
    CORREO = "CORREO"
    PUSH = "PUSH"
    SMS = "SMS"


class OperacionSincronizacion(str, enum.Enum):
    INSERTAR = "INSERTAR"
    ACTUALIZAR = "ACTUALIZAR"
    ELIMINAR = "ELIMINAR"


class EstadoSincronizacion(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    SINCRONIZADO = "SINCRONIZADO"
    FALLIDO = "FALLIDO"
    CONFLICTO = "CONFLICTO"


class PrioridadMantenimiento(str, enum.Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class EstadoMantenimiento(str, enum.Enum):
    ABIERTA = "ABIERTA"
    EN_PROGRESO = "EN_PROGRESO"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"
