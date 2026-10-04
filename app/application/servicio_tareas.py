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
from app.domain.modelos import EstadoTarea, Prioridad, ResumenProgreso, Tarea, TareaConProyecto


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

    def consultar_tablero(
        self,
        usuario: str,
        proyecto_id: str,
        estado: Optional[EstadoTarea] = None,
        responsable: Optional[str] = None,
        limite: int = 50,
        desplazamiento: int = 0,
    ) -> list[Tarea]:
        """Tablero del proyecto, con filtros y paginación.

        La paginación no es un adorno: ESC-01 compromete la latencia hasta 200
        tareas, y devolver la colección entera sin límite es justamente la
        forma de incumplirlo cuando el proyecto crece.
        """
        self._autorizar(usuario, proyecto_id, "consultar_tablero")
        return self._tareas.listar_por_proyecto(
            proyecto_id,
            estado=estado,
            responsable=responsable,
            limite=limite,
            desplazamiento=desplazamiento,
        )

    def consultar_progreso(self, usuario: str, proyecto_id: str) -> ResumenProgreso:
        """Resumen agregado del avance (RF-06)."""
        self._autorizar(usuario, proyecto_id, "consultar_progreso")
        return self._tareas.resumir_progreso(proyecto_id)

    def _tarea_del_proyecto(self, proyecto_id: str, tarea_id: str) -> Tarea:
        """La tarea, solo si pertenece al proyecto. Sin volver a autorizar:
        quien llama ya lo hizo. Autorizar dos veces eran dos viajes más a la
        base de datos por operación, ~200 ms cada uno en el despliegue."""
        tarea = self._tareas.obtener(tarea_id)
        if tarea is None or tarea.proyecto_id != proyecto_id:
            raise RecursoNoEncontrado("La tarea no existe en este proyecto.")
        return tarea

    def obtener_tarea(self, usuario: str, proyecto_id: str, tarea_id: str) -> Tarea:
        self._autorizar(usuario, proyecto_id, "obtener_tarea")
        return self._tarea_del_proyecto(proyecto_id, tarea_id)

    def asignar_tarea(
        self, usuario: str, proyecto_id: str, tarea_id: str, responsable: str
    ) -> Tarea:
        proyecto = self._autorizar(usuario, proyecto_id, "asignar_tarea")
        if not proyecto.es_miembro(responsable):
            raise AccesoDenegado(
                "No se puede asignar la tarea a alguien ajeno al proyecto."
            )
        tarea = self._tarea_del_proyecto(proyecto_id, tarea_id)
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
        tarea = self._tarea_del_proyecto(proyecto_id, tarea_id)
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

    def editar_tarea(
        self,
        usuario: str,
        proyecto_id: str,
        tarea_id: str,
        titulo: Optional[str] = None,
        prioridad: Optional[Prioridad] = None,
        fecha_limite: Optional[date] = None,
        quitar_fecha_limite: bool = False,
    ) -> Tarea:
        """Cambia título, prioridad o fecha límite. Cualquier miembro puede:
        el tablero es de todo el equipo."""
        self._autorizar(usuario, proyecto_id, "editar_tarea")
        tarea = self._tarea_del_proyecto(proyecto_id, tarea_id)
        cambiados = tarea.editar(titulo, prioridad, fecha_limite, quitar_fecha_limite)
        if cambiados:
            self._tareas.guardar(tarea)
            self._bus.publicar(
                eventos.TareaEditada(
                    tarea_id=tarea_id,
                    proyecto_id=proyecto_id,
                    campos=tuple(cambiados),
                    usuario=usuario,
                )
            )
        return tarea

    def eliminar_tarea(self, usuario: str, proyecto_id: str, tarea_id: str) -> None:
        """Solo quien creó la tarea o el líder del proyecto.

        Un miembro cualquiera puede editar, pero no borrar el trabajo de otro:
        borrar no se deshace. El intento denegado se audita como cualquier
        otro acceso denegado (ESC-03).
        """
        proyecto = self._autorizar(usuario, proyecto_id, "eliminar_tarea")
        tarea = self._tarea_del_proyecto(proyecto_id, tarea_id)
        if not proyecto.puede_eliminar(usuario, tarea):
            self._bus.publicar(
                eventos.AccesoDenegado(
                    usuario=usuario,
                    recurso=f"tarea:{tarea_id}",
                    operacion="eliminar_tarea",
                )
            )
            raise AccesoDenegado(
                "Solo quien creó la tarea o el líder del proyecto puede eliminarla."
            )
        self._tareas.eliminar(tarea_id)
        self._bus.publicar(
            eventos.TareaEliminada(
                tarea_id=tarea_id, proyecto_id=proyecto_id, usuario=usuario
            )
        )

    def mis_tareas(self, usuario: str, incluir_terminadas: bool = False) -> list[TareaConProyecto]:
        """Lo que el usuario tiene asignado en todos sus proyectos.

        No pasa por `_autorizar` porque no apunta a un proyecto concreto: la
        pertenencia la responde Proyectos y Equipos (consulta síncrona, ADR 0003)
        y Tareas solo busca dentro de esos proyectos. Un proyecto ajeno no puede
        aparecer (ESC-03), y Tareas no lee las tablas de Proyectos (ADR 0013).
        """
        proyectos = self._proyectos.listar_por_usuario(usuario)
        if not proyectos:
            return []
        nombres = {p.id: p.nombre for p in proyectos}
        tareas = self._tareas.asignadas_a(usuario, list(nombres), incluir_terminadas)
        return [TareaConProyecto(tarea=t, proyecto_nombre=nombres[t.proyecto_id]) for t in tareas]
