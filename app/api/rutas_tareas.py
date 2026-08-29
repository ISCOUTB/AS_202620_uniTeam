"""Endpoints de tareas: la capa de interfaz del corte vertical."""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencias import obtener_servicio, usuario_actual
from app.api.esquemas import (
    AsignarTarea,
    CambiarEstado,
    CrearTarea,
    ProgresoSalida,
    TareaSalida,
)
from app.application.servicio_tareas import ServicioTareas
from app.domain.modelos import EstadoTarea, Tarea

router = APIRouter(prefix="/proyectos/{proyecto_id}/tareas", tags=["tareas"])


def _salida(t: Tarea) -> TareaSalida:
    return TareaSalida(
        id=t.id,
        proyecto_id=t.proyecto_id,
        titulo=t.titulo,
        prioridad=t.prioridad,
        estado=t.estado,
        responsable=t.responsable,
        fecha_limite=t.fecha_limite,
        creada_por=t.creada_por,
        creada_en=t.creada_en,
    )


@router.post("", response_model=TareaSalida, status_code=status.HTTP_201_CREATED)
def crear_tarea(
    proyecto_id: str,
    datos: CrearTarea,
    usuario: str = Depends(usuario_actual),
    servicio: ServicioTareas = Depends(obtener_servicio),
) -> TareaSalida:
    tarea = servicio.crear_tarea(
        usuario=usuario,
        proyecto_id=proyecto_id,
        titulo=datos.titulo,
        prioridad=datos.prioridad,
        responsable=datos.responsable,
        fecha_limite=datos.fecha_limite,
    )
    return _salida(tarea)


@router.get("", response_model=list[TareaSalida])
def consultar_tablero(
    proyecto_id: str,
    estado: Optional[EstadoTarea] = None,
    responsable: Optional[str] = None,
    limite: int = Query(50, ge=1, le=200),
    desplazamiento: int = Query(0, ge=0),
    usuario: str = Depends(usuario_actual),
    servicio: ServicioTareas = Depends(obtener_servicio),
) -> list[TareaSalida]:
    """Tablero del proyecto, con filtros opcionales y paginación.

    El tope de 200 no es arbitrario: es el tamaño de proyecto para el que
    ESC-01 compromete la latencia.
    """
    tareas = servicio.consultar_tablero(
        usuario,
        proyecto_id,
        estado=estado,
        responsable=responsable,
        limite=limite,
        desplazamiento=desplazamiento,
    )
    return [_salida(t) for t in tareas]



@router.get("/{tarea_id}", response_model=TareaSalida)
def obtener_tarea(
    proyecto_id: str,
    tarea_id: str,
    usuario: str = Depends(usuario_actual),
    servicio: ServicioTareas = Depends(obtener_servicio),
) -> TareaSalida:
    return _salida(servicio.obtener_tarea(usuario, proyecto_id, tarea_id))


@router.put("/{tarea_id}/responsable", response_model=TareaSalida)
def asignar_tarea(
    proyecto_id: str,
    tarea_id: str,
    datos: AsignarTarea,
    usuario: str = Depends(usuario_actual),
    servicio: ServicioTareas = Depends(obtener_servicio),
) -> TareaSalida:
    return _salida(
        servicio.asignar_tarea(usuario, proyecto_id, tarea_id, datos.responsable)
    )


@router.put("/{tarea_id}/estado", response_model=TareaSalida)
def cambiar_estado(
    proyecto_id: str,
    tarea_id: str,
    datos: CambiarEstado,
    usuario: str = Depends(usuario_actual),
    servicio: ServicioTareas = Depends(obtener_servicio),
) -> TareaSalida:
    return _salida(
        servicio.cambiar_estado(usuario, proyecto_id, tarea_id, datos.estado)
    )
