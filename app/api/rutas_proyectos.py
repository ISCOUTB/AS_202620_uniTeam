"""Endpoints de proyectos."""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_sesion, usuario_actual
from app.api.esquemas import CrearProyecto, ProyectoSalida
from app.domain.modelos import Miembro, Proyecto, RolMiembro
from app.infrastructure.repositorios import RepositorioProyectosSQL

router = APIRouter(prefix="/proyectos", tags=["proyectos"])


@router.post("", response_model=ProyectoSalida, status_code=status.HTTP_201_CREATED)
def crear_proyecto(
    datos: CrearProyecto,
    usuario: str = Depends(usuario_actual),
    sesion: Session = Depends(obtener_sesion),
) -> ProyectoSalida:
    """Crea un proyecto. Quien lo crea queda como líder."""
    miembros = [Miembro(usuario=usuario, rol=RolMiembro.LIDER)]
    miembros += [
        Miembro(usuario=u) for u in dict.fromkeys(datos.miembros) if u != usuario
    ]
    proyecto = Proyecto(id=str(uuid.uuid4()), nombre=datos.nombre, miembros=miembros)
    RepositorioProyectosSQL(sesion).guardar(proyecto)
    return ProyectoSalida(
        id=proyecto.id,
        nombre=proyecto.nombre,
        miembros=[m.usuario for m in proyecto.miembros],
    )
