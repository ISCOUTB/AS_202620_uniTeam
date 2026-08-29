"""Puertos: lo que la capa de aplicación necesita de la persistencia.

Declararlos aquí permite que los casos de uso no dependan de SQLAlchemy.
"""
from typing import Optional, Protocol

from app.domain.modelos import Proyecto, Tarea


class RepositorioProyectos(Protocol):
    def obtener(self, proyecto_id: str) -> Optional[Proyecto]: ...
    def guardar(self, proyecto: Proyecto) -> None: ...


class RepositorioTareas(Protocol):
    def obtener(self, tarea_id: str) -> Optional[Tarea]: ...
    def guardar(self, tarea: Tarea) -> None: ...
    def listar_por_proyecto(self, proyecto_id: str) -> list[Tarea]: ...


class RepositorioAuditoria(Protocol):
    def registrar(self, usuario: str, recurso: str, operacion: str, resultado: str) -> None: ...
