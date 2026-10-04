"""Los contextos no leen las tablas de los demás (propiedad de datos, ADR 0013).

«Mis tareas» cruza proyectos, y ahí es donde la erosión es más probable: la
consulta más cómoda une `tareas` con `miembros` y `proyectos` en un solo SQL.
Funciona, pero deja al repositorio de Tareas dependiendo del esquema de otro
contexto. Estas pruebas fallan si eso vuelve a ocurrir.
"""
import ast
from datetime import datetime, timezone
from pathlib import Path

from app.application.servicio_tareas import ServicioTareas
from app.domain.modelos import Miembro, Proyecto, RolMiembro
from app.infrastructure.repositorios import RepositorioTareasSQL
from app.infrastructure.tablas import TareaTabla

RAIZ = Path(__file__).resolve().parent.parent
TABLAS_DE_PROYECTOS = {"ProyectoTabla", "MiembroTabla"}


def _nombres_usados(clase: type) -> set[str]:
    """Nombres a los que hace referencia el código de una clase."""
    fuente = (RAIZ / "app/infrastructure/repositorios.py").read_text()
    for nodo in ast.parse(fuente).body:
        if isinstance(nodo, ast.ClassDef) and nodo.name == clase.__name__:
            return {n.id for n in ast.walk(nodo) if isinstance(n, ast.Name)}
    raise AssertionError(f"No se encontró {clase.__name__}")


def test_el_repositorio_de_tareas_no_toca_las_tablas_de_proyectos():
    """Guardia estructural: Tareas solo lee `TareaTabla`."""
    cruzadas = _nombres_usados(RepositorioTareasSQL) & TABLAS_DE_PROYECTOS
    assert cruzadas == set(), f"Tareas cruza el límite hacia Proyectos: {sorted(cruzadas)}"


class _ProyectosFalso:
    """Puerto de Proyectos y Equipos con un solo proyecto visible."""

    def __init__(self, proyectos):
        self._p = proyectos

    def listar_por_usuario(self, usuario):
        return [p for p in self._p if p.es_miembro(usuario)]


class _TareasEspia:
    def __init__(self):
        self.recibio = None

    def asignadas_a(self, usuario, proyecto_ids, incluir_terminadas=False):
        self.recibio = list(proyecto_ids)
        return []


def test_mis_tareas_pide_a_proyectos_la_pertenencia_y_se_la_pasa_a_tareas():
    """Tareas recibe los proyectos ya autorizados; no los averigua por su cuenta."""
    mio = Proyecto(id="p-mio", nombre="Mío", miembros=[Miembro("bruno", RolMiembro.INTEGRANTE)])
    ajeno = Proyecto(id="p-ajeno", nombre="Ajeno", miembros=[Miembro("carla", RolMiembro.LIDER)])
    tareas = _TareasEspia()
    ServicioTareas(_ProyectosFalso([mio, ajeno]), tareas, bus=None).mis_tareas("bruno")
    assert tareas.recibio == ["p-mio"]


def test_sin_proyectos_no_se_consulta_a_tareas():
    tareas = _TareasEspia()
    assert ServicioTareas(_ProyectosFalso([]), tareas, bus=None).mis_tareas("bruno") == []
    assert tareas.recibio is None


def test_el_repositorio_de_tareas_solo_devuelve_los_proyectos_que_se_le_pasan(sesion):
    """Aunque exista una tarea mía en otro proyecto, no sale si no se autorizó."""
    for pid in ("p1", "p2"):
        sesion.add(
            TareaTabla(
                id=f"t-{pid}", proyecto_id=pid, titulo=pid, creada_por="ana", prioridad="media",
                estado="pendiente", responsable="bruno", creada_en=datetime.now(timezone.utc),
            )
        )
    sesion.commit()
    encontradas = RepositorioTareasSQL(sesion).asignadas_a("bruno", ["p1"])
    assert [t.proyecto_id for t in encontradas] == ["p1"]
