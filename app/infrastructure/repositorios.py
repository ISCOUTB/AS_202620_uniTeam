"""Adaptadores de persistencia: implementan los puertos con SQLAlchemy."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.modelos import (
    EstadoTarea,
    Miembro,
    Prioridad,
    Proyecto,
    RolMiembro,
    Tarea,
)
from app.infrastructure.tablas import (
    AuditoriaTabla,
    MiembroTabla,
    ProyectoTabla,
    TareaTabla,
)


class RepositorioProyectosSQL:
    def __init__(self, sesion: Session) -> None:
        self._s = sesion

    def obtener(self, proyecto_id: str) -> Optional[Proyecto]:
        fila = self._s.get(ProyectoTabla, proyecto_id)
        if fila is None:
            return None
        return Proyecto(
            id=fila.id,
            nombre=fila.nombre,
            miembros=[
                Miembro(usuario=m.usuario, rol=RolMiembro(m.rol)) for m in fila.miembros
            ],
        )

    def guardar(self, proyecto: Proyecto) -> None:
        fila = self._s.get(ProyectoTabla, proyecto.id)
        if fila is None:
            fila = ProyectoTabla(id=proyecto.id, nombre=proyecto.nombre)
            self._s.add(fila)
        else:
            fila.nombre = proyecto.nombre
        self._s.flush()

        existentes = {m.usuario for m in fila.miembros}
        for miembro in proyecto.miembros:
            if miembro.usuario not in existentes:
                self._s.add(
                    MiembroTabla(
                        proyecto_id=proyecto.id,
                        usuario=miembro.usuario,
                        rol=miembro.rol.value,
                    )
                )
        self._s.flush()


class RepositorioTareasSQL:
    def __init__(self, sesion: Session) -> None:
        self._s = sesion

    @staticmethod
    def _a_dominio(fila: TareaTabla) -> Tarea:
        return Tarea(
            id=fila.id,
            proyecto_id=fila.proyecto_id,
            titulo=fila.titulo,
            creada_por=fila.creada_por,
            prioridad=Prioridad(fila.prioridad),
            estado=EstadoTarea(fila.estado),
            responsable=fila.responsable,
            fecha_limite=fila.fecha_limite,
            creada_en=fila.creada_en,
        )

    def obtener(self, tarea_id: str) -> Optional[Tarea]:
        fila = self._s.get(TareaTabla, tarea_id)
        return self._a_dominio(fila) if fila else None

    def guardar(self, tarea: Tarea) -> None:
        fila = self._s.get(TareaTabla, tarea.id)
        if fila is None:
            fila = TareaTabla(id=tarea.id, creada_en=tarea.creada_en)
            self._s.add(fila)
        fila.proyecto_id = tarea.proyecto_id
        fila.titulo = tarea.titulo
        fila.creada_por = tarea.creada_por
        fila.prioridad = tarea.prioridad.value
        fila.estado = tarea.estado.value
        fila.responsable = tarea.responsable
        fila.fecha_limite = tarea.fecha_limite
        self._s.flush()

    def listar_por_proyecto(self, proyecto_id: str) -> list[Tarea]:
        filas = self._s.scalars(
            select(TareaTabla)
            .where(TareaTabla.proyecto_id == proyecto_id)
            .order_by(TareaTabla.creada_en)
        ).all()
        return [self._a_dominio(f) for f in filas]


class RepositorioAuditoriaSQL:
    def __init__(self, sesion: Session) -> None:
        self._s = sesion

    def registrar(
        self, usuario: str, recurso: str, operacion: str, resultado: str
    ) -> None:
        self._s.add(
            AuditoriaTabla(
                usuario=usuario,
                recurso=recurso,
                operacion=operacion,
                resultado=resultado,
                ocurrido_en=datetime.now(timezone.utc),
            )
        )
        self._s.flush()
