"""Vistas que cruzan proyectos: «Mis tareas» y el avance en la lista de proyectos.

Cruzar proyectos es exactamente donde una fuga entre equipos (ESC-03) sería
más fácil: por eso hay una prueba que inserta a propósito un caso que la API no
permite crear y comprueba que no aparece.
"""
from datetime import datetime, timedelta, timezone

from app.infrastructure.repositorios import hoy_local
from app.infrastructure.tablas import TareaTabla


def _proyecto(cliente, cab, nombre, lider="ana", miembros=("bruno",)):
    return cliente.post(
        "/proyectos", json={"nombre": nombre, "miembros": list(miembros)}, headers=cab(lider)
    ).json()["id"]


def _tarea(cliente, cab, proyecto, titulo, autor="ana", **extra):
    return cliente.post(
        f"/proyectos/{proyecto}/tareas", json={"titulo": titulo, **extra}, headers=cab(autor)
    ).json()["id"]


# -- Mis tareas ---------------------------------------------------------------


def test_mis_tareas_reune_lo_asignado_en_todos_mis_proyectos(cliente, cab):
    a = _proyecto(cliente, cab, "Arquitectura")
    b = _proyecto(cliente, cab, "Bases de datos")
    _tarea(cliente, cab, a, "Informe", responsable="bruno")
    _tarea(cliente, cab, b, "Modelo ER", responsable="bruno")
    _tarea(cliente, cab, a, "De Ana", responsable="ana")

    mias = cliente.get("/mis-tareas", headers=cab("bruno")).json()
    assert sorted(t["titulo"] for t in mias) == ["Informe", "Modelo ER"]
    assert {t["proyecto_nombre"] for t in mias} == {"Arquitectura", "Bases de datos"}


def test_mis_tareas_ordena_por_fecha_y_deja_las_sin_fecha_al_final(cliente, cab):
    p = _proyecto(cliente, cab, "P")
    hoy = hoy_local()
    _tarea(cliente, cab, p, "Sin fecha", responsable="ana")
    _tarea(cliente, cab, p, "Lejana", responsable="ana", fecha_limite=str(hoy + timedelta(days=9)))
    _tarea(cliente, cab, p, "Cercana", responsable="ana", fecha_limite=str(hoy + timedelta(days=1)))
    titulos = [t["titulo"] for t in cliente.get("/mis-tareas", headers=cab("ana")).json()]
    assert titulos == ["Cercana", "Lejana", "Sin fecha"]


def test_mis_tareas_oculta_las_terminadas_salvo_que_se_pidan(cliente, cab):
    p = _proyecto(cliente, cab, "P")
    tarea = _tarea(cliente, cab, p, "Hecha", responsable="ana")
    ruta = f"/proyectos/{p}/tareas/{tarea}/estado"
    cliente.put(ruta, json={"estado": "en_progreso"}, headers=cab("ana"))
    cliente.put(ruta, json={"estado": "completada"}, headers=cab("ana"))

    assert cliente.get("/mis-tareas", headers=cab("ana")).json() == []
    todas = cliente.get("/mis-tareas", params={"incluir_terminadas": "true"}, headers=cab("ana")).json()
    assert [t["titulo"] for t in todas] == ["Hecha"]


def test_mis_tareas_nunca_muestra_un_proyecto_ajeno(cliente, cab, sesion):
    """Una tarea con mi nombre como responsable en un proyecto del que no soy
    miembro no puede crearse por la API; se inserta a mano para comprobar que,
    si existiera, no se filtraría (ESC-03)."""
    ajeno = _proyecto(cliente, cab, "Ajeno", lider="carla", miembros=())
    sesion.add(
        TareaTabla(
            id="tarea-colada",
            proyecto_id=ajeno,
            titulo="No debería verse",
            creada_por="carla",
            prioridad="alta",
            estado="pendiente",
            responsable="bruno",
            creada_en=datetime.now(timezone.utc),
        )
    )
    sesion.commit()
    assert cliente.get("/mis-tareas", headers=cab("bruno")).json() == []


def test_mis_tareas_exige_credencial(cliente):
    assert cliente.get("/mis-tareas").status_code == 401


# -- Avance en la lista de proyectos -----------------------------------------


def test_la_lista_de_proyectos_trae_el_avance_de_cada_uno(cliente, cab):
    p = _proyecto(cliente, cab, "Arquitectura")
    vacio = _proyecto(cliente, cab, "Vacío")
    ayer = str(hoy_local() - timedelta(days=1))
    _tarea(cliente, cab, p, "Vencida", fecha_limite=ayer)
    hecha = _tarea(cliente, cab, p, "Hecha", fecha_limite=ayer)
    _tarea(cliente, cab, p, "Normal")
    ruta = f"/proyectos/{p}/tareas/{hecha}/estado"
    cliente.put(ruta, json={"estado": "en_progreso"}, headers=cab("ana"))
    cliente.put(ruta, json={"estado": "completada"}, headers=cab("ana"))

    proyectos = {x["id"]: x for x in cliente.get("/proyectos", headers=cab("ana")).json()}
    assert proyectos[p]["resumen"] == {"total": 3, "terminadas": 1, "vencidas": 1}
    assert proyectos[vacio]["resumen"] == {"total": 0, "terminadas": 0, "vencidas": 0}
    assert {"id", "nombre", "miembros"} <= proyectos[p].keys(), "los campos de siempre siguen ahí"
