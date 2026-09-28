"""Edición, eliminación y reasignación de tareas.

Editar lo puede cualquier miembro; eliminar, solo quien creó la tarea o el
líder. Todo queda auditado, también la asignación, que antes no lo estaba.
"""
from app.infrastructure.tablas import AuditoriaTabla


def _proyecto(cliente, cab):
    return cliente.post(
        "/proyectos", json={"nombre": "Arquitectura", "miembros": ["bruno", "carla"]}, headers=cab("ana")
    ).json()["id"]


def _tarea(cliente, cab, proyecto, autor="ana", **extra):
    respuesta = cliente.post(
        f"/proyectos/{proyecto}/tareas",
        json={"titulo": "Redactar la sección 7", "fecha_limite": "2026-11-30", **extra},
        headers=cab(autor),
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["id"]


def _operaciones(sesion, operacion):
    sesion.rollback()  # MySQL: REPEATABLE READ; hay que ver lo confirmado después
    return sesion.query(AuditoriaTabla).filter_by(operacion=operacion).all()


# -- Edición ------------------------------------------------------------------


def test_un_miembro_edita_titulo_y_prioridad(cliente, cab):
    proyecto = _proyecto(cliente, cab)
    tarea = _tarea(cliente, cab, proyecto)
    respuesta = cliente.patch(
        f"/proyectos/{proyecto}/tareas/{tarea}",
        json={"titulo": "Redactar la sección 8", "prioridad": "alta"},
        headers=cab("bruno"),
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["titulo"] == "Redactar la sección 8"
    assert cuerpo["prioridad"] == "alta"
    assert cuerpo["fecha_limite"] == "2026-11-30", "un campo ausente no se toca"


def test_fecha_limite_null_la_quita(cliente, cab):
    proyecto = _proyecto(cliente, cab)
    tarea = _tarea(cliente, cab, proyecto)
    respuesta = cliente.patch(
        f"/proyectos/{proyecto}/tareas/{tarea}", json={"fecha_limite": None}, headers=cab("ana")
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["fecha_limite"] is None


def test_una_edicion_vacia_se_rechaza(cliente, cab):
    proyecto = _proyecto(cliente, cab)
    tarea = _tarea(cliente, cab, proyecto)
    for cuerpo in ({}, {"titulo": None}, {"titulo": "   "}, {"prioridad": None}):
        respuesta = cliente.patch(
            f"/proyectos/{proyecto}/tareas/{tarea}", json=cuerpo, headers=cab("ana")
        )
        assert respuesta.status_code == 422, cuerpo


def test_un_ajeno_no_edita_y_queda_auditado(cliente, cab, sesion):
    proyecto = _proyecto(cliente, cab)
    tarea = _tarea(cliente, cab, proyecto)
    respuesta = cliente.patch(
        f"/proyectos/{proyecto}/tareas/{tarea}", json={"titulo": "Mío"}, headers=cab("intruso")
    )
    assert respuesta.status_code == 403
    assert "titulo" not in respuesta.json()
    assert _operaciones(sesion, "editar_tarea")[0].resultado == "denegado"


def test_la_edicion_se_audita(cliente, cab, sesion):
    proyecto = _proyecto(cliente, cab)
    tarea = _tarea(cliente, cab, proyecto)
    cliente.patch(f"/proyectos/{proyecto}/tareas/{tarea}", json={"prioridad": "baja"}, headers=cab("bruno"))
    registros = _operaciones(sesion, "editar_tarea")
    assert [(r.usuario, r.resultado) for r in registros] == [("bruno", "permitido")]


def test_editar_sin_cambios_no_audita(cliente, cab, sesion):
    proyecto = _proyecto(cliente, cab)
    tarea = _tarea(cliente, cab, proyecto)
    cliente.patch(f"/proyectos/{proyecto}/tareas/{tarea}", json={"prioridad": "media"}, headers=cab("ana"))
    assert _operaciones(sesion, "editar_tarea") == []


# -- Eliminación --------------------------------------------------------------


def test_quien_creo_la_tarea_la_elimina(cliente, cab):
    proyecto = _proyecto(cliente, cab)
    tarea = _tarea(cliente, cab, proyecto, autor="bruno")
    respuesta = cliente.delete(f"/proyectos/{proyecto}/tareas/{tarea}", headers=cab("bruno"))
    assert respuesta.status_code == 204
    assert cliente.get(f"/proyectos/{proyecto}/tareas/{tarea}", headers=cab("bruno")).status_code == 404


def test_el_lider_elimina_la_tarea_de_otro(cliente, cab):
    proyecto = _proyecto(cliente, cab)
    tarea = _tarea(cliente, cab, proyecto, autor="bruno")
    assert cliente.delete(f"/proyectos/{proyecto}/tareas/{tarea}", headers=cab("ana")).status_code == 204


def test_otro_miembro_no_elimina_y_queda_auditado(cliente, cab, sesion):
    proyecto = _proyecto(cliente, cab)
    tarea = _tarea(cliente, cab, proyecto, autor="bruno")
    respuesta = cliente.delete(f"/proyectos/{proyecto}/tareas/{tarea}", headers=cab("carla"))
    assert respuesta.status_code == 403
    assert cliente.get(f"/proyectos/{proyecto}/tareas/{tarea}", headers=cab("carla")).status_code == 200
    registros = _operaciones(sesion, "eliminar_tarea")
    assert [(r.usuario, r.resultado) for r in registros] == [("carla", "denegado")]


def test_la_eliminacion_se_audita_y_actualiza_el_progreso(cliente, cab, sesion):
    proyecto = _proyecto(cliente, cab)
    tarea = _tarea(cliente, cab, proyecto)
    _tarea(cliente, cab, proyecto)
    cliente.delete(f"/proyectos/{proyecto}/tareas/{tarea}", headers=cab("ana"))
    assert cliente.get(f"/proyectos/{proyecto}/progreso", headers=cab("ana")).json()["total"] == 1
    assert [r.resultado for r in _operaciones(sesion, "eliminar_tarea")] == ["permitido"]


def test_eliminar_una_tarea_de_otro_proyecto_responde_404(cliente, cab):
    proyecto = _proyecto(cliente, cab)
    otro = cliente.post("/proyectos", json={"nombre": "Otro", "miembros": []}, headers=cab("ana")).json()["id"]
    tarea = _tarea(cliente, cab, otro)
    assert cliente.delete(f"/proyectos/{proyecto}/tareas/{tarea}", headers=cab("ana")).status_code == 404


# -- Asignación ---------------------------------------------------------------


def test_la_asignacion_queda_auditada(cliente, cab, sesion):
    proyecto = _proyecto(cliente, cab)
    tarea = _tarea(cliente, cab, proyecto)
    respuesta = cliente.put(
        f"/proyectos/{proyecto}/tareas/{tarea}/responsable",
        json={"responsable": "  Carla "},
        headers=cab("ana"),
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["responsable"] == "carla"
    assert [r.usuario for r in _operaciones(sesion, "asignar_tarea")] == ["ana"]


def test_filtrar_por_responsable_no_distingue_mayusculas(cliente, cab):
    proyecto = _proyecto(cliente, cab)
    _tarea(cliente, cab, proyecto, responsable="bruno")
    _tarea(cliente, cab, proyecto)
    tareas = cliente.get(
        f"/proyectos/{proyecto}/tareas", params={"responsable": "BRUNO"}, headers=cab("ana")
    ).json()
    assert len(tareas) == 1


def test_el_navegador_puede_editar_y_eliminar_desde_el_sitio(cliente):
    """El preflight de CORS debe admitir PATCH y DELETE desde el origen del
    sitio; sin PATCH en la lista, el navegador bloqueaba la edición."""
    for metodo in ("PATCH", "DELETE"):
        respuesta = cliente.options(
            "/proyectos/x/tareas/y",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": metodo,
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )
        assert respuesta.status_code == 200, metodo
        assert metodo in respuesta.headers["access-control-allow-methods"]
