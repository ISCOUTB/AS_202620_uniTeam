"""Endpoint de progreso del proyecto (RF-06).

Va en su propio router porque cuelga del proyecto, no del tablero de tareas.
"""
from fastapi import APIRouter, Depends

from app.api.dependencias import obtener_servicio, usuario_actual
from app.api.esquemas import ProgresoSalida
from app.application.servicio_tareas import ServicioTareas

router = APIRouter(prefix="/proyectos/{proyecto_id}", tags=["proyectos"])


@router.get("/progreso", response_model=ProgresoSalida)
def consultar_progreso(
    proyecto_id: str,
    usuario: str = Depends(usuario_actual),
    servicio: ServicioTareas = Depends(obtener_servicio),
) -> ProgresoSalida:
    """Resumen agregado del avance: cuántas tareas hay en cada estado."""
    resumen = servicio.consultar_progreso(usuario, proyecto_id)
    return ProgresoSalida(
        total=resumen.total,
        por_estado=resumen.por_estado,
        sin_responsable=resumen.sin_responsable,
        vencidas=resumen.vencidas,
        porcentaje_completado=resumen.porcentaje_completado,
    )
