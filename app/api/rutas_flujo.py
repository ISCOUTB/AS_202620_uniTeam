"""Flujo de estados de las tareas, publicado por la API (ADR 0012).

La Aplicación Web no conoce los estados: los lee de aquí. Así, añadir un
estado es un cambio del dominio y nada más, que es lo que ESC-05 mide.
"""
from fastapi import APIRouter

from app.api.esquemas import EstadoFlujo, FlujoEstados
from app.domain.modelos import (
    ESTADO_FINAL,
    ESTADO_INICIAL,
    ETIQUETAS_ESTADO,
    TRANSICIONES,
    EstadoTarea,
)

router = APIRouter(tags=["tareas"])


@router.get("/flujo-estados", response_model=FlujoEstados)
def flujo_estados() -> FlujoEstados:
    """Estados en el orden de las columnas, sus etiquetas y las transiciones
    permitidas. No exige credencial: no contiene datos de nadie."""
    return FlujoEstados(
        estados=[
            EstadoFlujo(
                id=e.value,
                etiqueta=ETIQUETAS_ESTADO[e],
                inicial=e is ESTADO_INICIAL,
                final=e is ESTADO_FINAL,
                siguientes=[d.value for d in TRANSICIONES[e]],
            )
            for e in EstadoTarea
        ],
    )
