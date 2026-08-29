"""Casos de uso de la gestión de tareas.

Aquí vive la regla que sostiene ESC-03: **toda** operación sobre un proyecto
comprueba la pertenencia del usuario antes de ejecutarse, y esa comprobación
es síncrona. Los eventos se publican después.
"""
import uuid
from datetime import date
from typing import Optional

from app.application.bus import BusEventos
from app.application.puertos import RepositorioProyectos, RepositorioTareas
from app.domain import eventos
from app.domain.errores import AccesoDenegado, RecursoNoEncontrado
from app.domain.modelos import EstadoTarea, Prioridad, Tarea


class ServicioTareas:
    def __init__(
        self,
        proyectos: RepositorioProyectos,
        tareas: RepositorioTareas,
        bus: BusEventos,
    ) -> None:
        self._proyectos = proyectos
        self._tareas = tareas
        self._bus = bus

    # -- autorización ----------------------------------------------------
    def _autorizar(self, usuario: str, proyecto_id: str, operacion: str):
        """Devuelve el proyecto si el usuario es miembro; si no, deniega.

        No distingue «no existe» de «no eres miembro» en el error que sale al
        exterior: confirmar la existencia de un proyecto ajeno ya es una fuga
        (ESC-03).
        """
        proyecto = self._proyectos.obtener(proyecto_id)
        if proyecto is None or not proyecto.es_miembro(usuario):
            self._bus.publicar(
                eventos.AccesoDenegado(
                    usuario=usuario,
                    recurso=f"proyecto:{proyecto_id}",
                    operacion=operacion,
                )
            )
            raise AccesoDenegado(
                "No tiene acceso a este proyecto o el proyecto no existe."
            )
        return proyecto

    # -- casos de uso ----------------------------------------------------
    def crear_tarea(
        self,
        usuario: str,
        proyecto_id: str,
        titulo: str,
        prioridad: Prioridad = Prioridad.MEDIA,
        responsable: Optional[str] = None,
        fecha_limite: Optional[date] = None,
    ) -> Tarea:
        proyecto = self._autorizar(usuario, proyecto_id, "crear_tarea")

        if responsable is not None and not proyecto.es_miembro(responsable):
            raise AccesoDenegado(
                "No se puede asignar la tarea a alguien ajeno al proyecto."
            )

        tarea = Tarea(
            id=str(uuid.uuid4()),
            proyecto_id=proyecto_id,
            titulo=titulo,
            creada_por=usuario,
            prioridad=prioridad,
            responsable=responsable,
            fecha_limite=fecha_limite,
        )
        self._tareas.guardar(tarea)
        self._bus.publicar(
            eventos.TareaCreada(
                tarea_id=tarea.id, proyecto_id=proyecto_id, usuario=usuario
            )
        )
        return tarea

    def consultar_tablero(self, usuario: str, proyecto_id: str) -> list[Tarea]:
        self._autorizar(usuario, proyecto_id, "consultar_tablero")
        return self._tareas.listar_por_proyecto(proyecto_id)

    def obtener_tarea(self, usuario: str, proyecto_id: str, tarea_id: str) -> Tarea:
        self._autorizar(usuario, proyecto_id, "obtener_tarea")
        tarea = self._tareas.obtener(tarea_id)
        if tarea is None or tarea.proyecto_id != proyecto_id:
            raise RecursoNoEncontrado("La tarea no existe en este proyecto.")
        return tarea

    def asignar_tarea(
        self, usuario: str, proyecto_id: str, tarea_id: str, responsable: str
    ) -> Tarea:
        proyecto = self._autorizar(usuario, proyecto_id, "asignar_tarea")
        if not proyecto.es_miembro(responsable):
            raise AccesoDenegado(
                "No se puede asignar la tarea a alguien ajeno al proyecto."
            )
        tarea = self.obtener_tarea(usuario, proyecto_id, tarea_id)
        tarea.asignar(responsable)
        self._tareas.guardar(tarea)
        self._bus.publicar(
            eventos.TareaAsignada(
                tarea_id=tarea_id,
                proyecto_id=proyecto_id,
                responsable=responsable,
                usuario=usuario,
            )
        )
        return tarea

    def cambiar_estado(
        self, usuario: str, proyecto_id: str, tarea_id: str, nuevo: EstadoTarea
    ) -> Tarea:
        self._autorizar(usuario, proyecto_id, "cambiar_estado")
        tarea = self.obtener_tarea(usuario, proyecto_id, tarea_id)
        tarea.cambiar_estado(nuevo)
        self._tareas.guardar(tarea)
        self._bus.publicar(
            eventos.EstadoCambiado(
                tarea_id=tarea_id,
                proyecto_id=proyecto_id,
                estado=nuevo.value,
                usuario=usuario,
            )
        )
        return tarea
