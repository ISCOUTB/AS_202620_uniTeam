"""Prueba del recorrido completo: interfaz -> lógica -> persistencia.

Ejercita el corte vertical de la evidencia S4 y las dos reglas que sostienen
los escenarios de calidad prioritarios.
"""
from app.infrastructure.tablas import AuditoriaTabla, TareaTabla


def _releer(sesion):
    """Cierra la transaccion de lectura antes de consultar la base de datos.

    MySQL trabaja en REPEATABLE READ: sin esto, la sesion de la prueba
    seguiria viendo la instantanea anterior a lo que confirmo la peticion
    HTTP. Con SQLite el fallo no aparece, y por eso se hace explicito.
    """
    sesion.rollback()
    return sesion


def _crear_proyecto(cliente, cab, lider="ana", miembros=("bruno",)):
    respuesta = cliente.post(
        "/proyectos",
        json={"nombre": "Proyecto de Arquitectura", "miembros": list(miembros)},
        headers=cab(lider),
    )
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def test_recorrido_completo_de_una_tarea(cliente, sesion, cab):
    """Crear proyecto, crear tarea, verla en el tablero y moverla de estado.

    Comprueba además que la tarea quedó realmente escrita en la base de datos,
    no solo devuelta por la API.
    """
    proyecto_id = _crear_proyecto(cliente, cab)

    creada = cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={
            "titulo": "Redactar la sección 5 de arc42",
            "prioridad": "alta",
            "responsable": "bruno",
            "fecha_limite": "2026-09-05",
        },
        headers=cab("ana"),
    )
    assert creada.status_code == 201
    tarea = creada.json()
    assert tarea["estado"] == "pendiente"
    assert tarea["responsable"] == "bruno"

    # Persistencia: la fila existe en la base de datos.
    fila = _releer(sesion).get(TareaTabla, tarea["id"])
    assert fila is not None
    assert fila.titulo == "Redactar la sección 5 de arc42"
    assert fila.proyecto_id == proyecto_id

    # Consulta del tablero (RF-06).
    tablero = cliente.get(
        f"/proyectos/{proyecto_id}/tareas", headers=cab("bruno")
    )
    assert tablero.status_code == 200
    assert [t["id"] for t in tablero.json()] == [tarea["id"]]

    # Transición de estado válida (RF-04).
    movida = cliente.put(
        f"/proyectos/{proyecto_id}/tareas/{tarea['id']}/estado",
        json={"estado": "en_progreso"},
        headers=cab("bruno"),
    )
    assert movida.status_code == 200
    assert movida.json()["estado"] == "en_progreso"

    assert _releer(sesion).get(TareaTabla, tarea["id"]).estado == "en_progreso"


def test_transicion_invalida_se_rechaza(cliente, cab):
    """De 'pendiente' no se puede saltar a 'completada'."""
    proyecto_id = _crear_proyecto(cliente, cab)
    tarea = cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea suelta"},
        headers=cab("ana"),
    ).json()

    respuesta = cliente.put(
        f"/proyectos/{proyecto_id}/tareas/{tarea['id']}/estado",
        json={"estado": "completada"},
        headers=cab("ana"),
    )
    assert respuesta.status_code == 409


def test_esc03_usuario_ajeno_no_accede_y_queda_auditado(cliente, sesion, cab):
    """ESC-03: 403, cero datos del recurso y registro de auditoría."""
    proyecto_id = _crear_proyecto(cliente, cab)
    cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea confidencial del equipo"},
        headers=cab("ana"),
    )

    respuesta = cliente.get(
        f"/proyectos/{proyecto_id}/tareas", headers=cab("intruso")
    )

    assert respuesta.status_code == 403
    assert "Tarea confidencial" not in respuesta.text

    registros = (
        _releer(sesion)
        .query(AuditoriaTabla)
        .filter(AuditoriaTabla.usuario == "intruso")
        .all()
    )
    assert len(registros) == 1
    assert registros[0].resultado == "denegado"
    assert registros[0].recurso == f"proyecto:{proyecto_id}"
    assert registros[0].operacion == "consultar_tablero"


def test_esc03_proyecto_inexistente_no_se_distingue_de_uno_ajeno(cliente, cab):
    """Confirmar la existencia de un proyecto ajeno ya sería una fuga."""
    ajeno = cliente.get(
        "/proyectos/00000000-0000-0000-0000-000000000000/tareas",
        headers=cab("intruso"),
    )
    assert ajeno.status_code == 403


def test_no_se_asigna_una_tarea_a_alguien_ajeno_al_proyecto(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    respuesta = cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea mal asignada", "responsable": "intruso"},
        headers=cab("ana"),
    )
    assert respuesta.status_code == 403


def test_las_operaciones_permitidas_tambien_quedan_auditadas(cliente, sesion, cab):
    """La auditoria de lo permitido comparte transaccion con el cambio.

    Sin esta prueba, un fallo del consumidor pasaria inadvertido: el bus aisla
    los errores de los consumidores a proposito, de modo que la peticion habria
    respondido 201 con la auditoria perdida.
    """
    proyecto_id = _crear_proyecto(cliente, cab)
    creada = cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea auditada"},
        headers=cab("ana"),
    )
    assert creada.status_code == 201
    tarea_id = creada.json()["id"]

    registros = (
        _releer(sesion)
        .query(AuditoriaTabla)
        .filter(AuditoriaTabla.recurso == f"tarea:{tarea_id}")
        .all()
    )
    assert [r.resultado for r in registros] == ["permitido"]
    assert registros[0].operacion == "crear_tarea"
    assert registros[0].usuario == "ana"
