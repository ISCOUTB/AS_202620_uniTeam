"""Proyectos: listado, consulta y gestión de miembros.

La pertenencia al proyecto es la unidad de control de acceso del sistema, así
que estas pruebas son continuación directa de ESC-03.
"""
from app.infrastructure.tablas import AuditoriaTabla


def _crear(cliente, lider, nombre, miembros=()):
    r = cliente.post(
        "/proyectos",
        json={"nombre": nombre, "miembros": list(miembros)},
        headers={"X-Usuario": lider},
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_solo_se_listan_los_proyectos_propios(cliente):
    _crear(cliente, "ana", "Proyecto de Ana", ["bruno"])
    _crear(cliente, "carla", "Proyecto de Carla")

    de_ana = cliente.get("/proyectos", headers={"X-Usuario": "ana"}).json()
    de_bruno = cliente.get("/proyectos", headers={"X-Usuario": "bruno"}).json()
    de_carla = cliente.get("/proyectos", headers={"X-Usuario": "carla"}).json()
    de_nadie = cliente.get("/proyectos", headers={"X-Usuario": "intruso"}).json()

    assert [p["nombre"] for p in de_ana] == ["Proyecto de Ana"]
    assert [p["nombre"] for p in de_bruno] == ["Proyecto de Ana"]
    assert [p["nombre"] for p in de_carla] == ["Proyecto de Carla"]
    assert de_nadie == []


def test_el_creador_queda_como_lider_y_los_demas_como_integrantes(cliente):
    proyecto_id = _crear(cliente, "ana", "Arquitectura", ["bruno"])
    detalle = cliente.get(
        f"/proyectos/{proyecto_id}", headers={"X-Usuario": "ana"}
    ).json()
    roles = {m["usuario"]: m["rol"] for m in detalle["miembros"]}
    assert roles == {"ana": "lider", "bruno": "integrante"}


def test_consultar_un_proyecto_ajeno_devuelve_403(cliente):
    proyecto_id = _crear(cliente, "ana", "Arquitectura")
    r = cliente.get(f"/proyectos/{proyecto_id}", headers={"X-Usuario": "intruso"})
    assert r.status_code == 403
    assert "Arquitectura" not in r.text


def test_solo_el_lider_agrega_miembros(cliente, sesion):
    proyecto_id = _crear(cliente, "ana", "Arquitectura", ["bruno"])

    negado = cliente.post(
        f"/proyectos/{proyecto_id}/miembros",
        json={"usuario": "diana"},
        headers={"X-Usuario": "bruno"},
    )
    assert negado.status_code == 403

    registros = (
        sesion.query(AuditoriaTabla)
        .filter(AuditoriaTabla.operacion == "agregar_miembro")
        .all()
    )
    assert [r.usuario for r in registros] == ["bruno"]
    assert registros[0].resultado == "denegado"

    permitido = cliente.post(
        f"/proyectos/{proyecto_id}/miembros",
        json={"usuario": "diana"},
        headers={"X-Usuario": "ana"},
    )
    assert permitido.status_code == 201
    assert "diana" in [m["usuario"] for m in permitido.json()["miembros"]]


def test_no_se_agrega_dos_veces_al_mismo_miembro(cliente):
    proyecto_id = _crear(cliente, "ana", "Arquitectura", ["bruno"])
    r = cliente.post(
        f"/proyectos/{proyecto_id}/miembros",
        json={"usuario": "bruno"},
        headers={"X-Usuario": "ana"},
    )
    assert r.status_code == 409


def test_un_miembro_recien_agregado_ya_ve_el_tablero(cliente):
    """El acceso se deriva de la pertenencia, sin ningún paso adicional."""
    proyecto_id = _crear(cliente, "ana", "Arquitectura")
    cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea existente"},
        headers={"X-Usuario": "ana"},
    )

    antes = cliente.get(
        f"/proyectos/{proyecto_id}/tareas", headers={"X-Usuario": "diana"}
    )
    assert antes.status_code == 403

    cliente.post(
        f"/proyectos/{proyecto_id}/miembros",
        json={"usuario": "diana"},
        headers={"X-Usuario": "ana"},
    )

    despues = cliente.get(
        f"/proyectos/{proyecto_id}/tareas", headers={"X-Usuario": "diana"}
    )
    assert despues.status_code == 200
    assert len(despues.json()) == 1
