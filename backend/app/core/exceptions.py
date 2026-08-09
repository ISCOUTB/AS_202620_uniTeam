"""
Excepciones y respuestas de error estándar.
"""

from fastapi import HTTPException, status


def not_found(entidad: str, id: str = ""):
    """404 – Entidad no encontrada."""
    msg = f"{entidad} no encontrado"
    if id:
        msg = f"{entidad} con ID '{id}' no encontrado"
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": f"{entidad.upper()}_NO_ENCONTRADO", "mensaje": msg, "codigo": 404},
    )


def bad_request(mensaje: str, error_code: str = "SOLICITUD_INVALIDA"):
    """400 – Solicitud inválida."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error": error_code, "mensaje": mensaje, "codigo": 400},
    )


def forbidden(mensaje: str = "No tienes permiso para realizar esta acción"):
    """403 – Prohibido."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"error": "PERMISO_DENEGADO", "mensaje": mensaje, "codigo": 403},
    )


def conflict(mensaje: str, error_code: str = "CONFLICTO"):
    """409 – Conflicto."""
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"error": error_code, "mensaje": mensaje, "codigo": 409},
    )
