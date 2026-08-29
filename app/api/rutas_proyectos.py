"""Endpoints de proyectos."""
from fastapi import APIRouter, Depends, status

from app.api.dependencias import obtener_servicio_proyectos, usuario_actual
from app.api.esquemas import (
    AgregarMiembro,
    CrearProyecto,
    MiembroSalida,
    ProyectoDetalle,
    ProyectoSalida,
)
from app.application.servicio_proyectos import ServicioProyectos
from app.domain.modelos import Proyecto

router = APIRouter(prefix="/proyectos", tags=["proyectos"])


def _detalle(p: Proyecto) -> ProyectoDetalle:
    return ProyectoDetalle(
        id=p.id,
        nombre=p.nombre,
        miembros=[MiembroSalida(usuario=m.usuario, rol=m.rol) for m in p.miembros],
    )


@router.post("", response_model=ProyectoSalida, status_code=status.HTTP_201_CREATED)
def crear_proyecto(
    datos: CrearProyecto,
    usuario: str = Depends(usuario_actual),
    servicio: ServicioProyectos = Depends(obtener_servicio_proyectos),
) -> ProyectoSalida:
    """Crea un proyecto. Quien lo crea queda como líder."""
    proyecto = servicio.crear(usuario, datos.nombre, datos.miembros)
    return ProyectoSalida(
        id=proyecto.id,
        nombre=proyecto.nombre,
        miembros=[m.usuario for m in proyecto.miembros],
    )


@router.get("", response_model=list[ProyectoDetalle])
def listar_mis_proyectos(
    usuario: str = Depends(usuario_actual),
    servicio: ServicioProyectos = Depends(obtener_servicio_proyectos),
) -> list[ProyectoDetalle]:
    """Proyectos de los que el usuario es miembro."""
    return [_detalle(p) for p in servicio.listar_mios(usuario)]


@router.get("/{proyecto_id}", response_model=ProyectoDetalle)
def obtener_proyecto(
    proyecto_id: str,
    usuario: str = Depends(usuario_actual),
    servicio: ServicioProyectos = Depends(obtener_servicio_proyectos),
) -> ProyectoDetalle:
    return _detalle(servicio.obtener(usuario, proyecto_id))


@router.post(
    "/{proyecto_id}/miembros",
    response_model=ProyectoDetalle,
    status_code=status.HTTP_201_CREATED,
)
def agregar_miembro(
    proyecto_id: str,
    datos: AgregarMiembro,
    usuario: str = Depends(usuario_actual),
    servicio: ServicioProyectos = Depends(obtener_servicio_proyectos),
) -> ProyectoDetalle:
    """Agrega un miembro al proyecto. Reservado al líder."""
    return _detalle(
        servicio.agregar_miembro(usuario, proyecto_id, datos.usuario, datos.rol)
    )
