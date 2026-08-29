"""Casos de uso de proyectos: creación, consulta y gestión de miembros.

La pertenencia al proyecto es la unidad de control de acceso del sistema
(ESC-03), así que quién puede modificar la lista de miembros es una decisión
de seguridad, no de comodidad: solo el líder.
"""
import uuid
from typing import Optional

from app.application.bus import BusEventos
from app.application.puertos import RepositorioProyectos
from app.domain import eventos
from app.domain.errores import AccesoDenegado
from app.domain.modelos import Miembro, Proyecto, RolMiembro


class ServicioProyectos:
    def __init__(self, proyectos: RepositorioProyectos, bus: BusEventos) -> None:
        self._proyectos = proyectos
        self._bus = bus

    def crear(self, usuario: str, nombre: str, miembros: list[str]) -> Proyecto:
        """Crea un proyecto. Quien lo crea queda como líder."""
        integrantes = [Miembro(usuario=usuario, rol=RolMiembro.LIDER)]
        integrantes += [
            Miembro(usuario=u) for u in dict.fromkeys(miembros) if u != usuario
        ]
        proyecto = Proyecto(id=str(uuid.uuid4()), nombre=nombre, miembros=integrantes)
        self._proyectos.guardar(proyecto)
        return proyecto

    def listar_mios(self, usuario: str) -> list[Proyecto]:
        """Proyectos de los que el usuario es miembro. Nunca devuelve ajenos."""
        return self._proyectos.listar_por_usuario(usuario)

    def obtener(self, usuario: str, proyecto_id: str) -> Proyecto:
        return self._autorizar(usuario, proyecto_id, "obtener_proyecto")

    def agregar_miembro(
        self, usuario: str, proyecto_id: str, nuevo: str, rol: Optional[RolMiembro] = None
    ) -> Proyecto:
        proyecto = self._autorizar(usuario, proyecto_id, "agregar_miembro")
        if not proyecto.es_lider(usuario):
            self._bus.publicar(
                eventos.AccesoDenegado(
                    usuario=usuario,
                    recurso=f"proyecto:{proyecto_id}",
                    operacion="agregar_miembro",
                )
            )
            raise AccesoDenegado("Solo el líder del proyecto puede agregar miembros.")

        proyecto.agregar_miembro(nuevo, rol or RolMiembro.INTEGRANTE)
        self._proyectos.guardar(proyecto)
        return proyecto

    def _autorizar(self, usuario: str, proyecto_id: str, operacion: str) -> Proyecto:
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
