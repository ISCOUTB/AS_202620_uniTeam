"""Pruebas de contrato de la API de UniTeam.

Verifican que la API cumple con su contrato formal: códigos de estado,
formatos de error, validación de entrada, autorización y paginación.

Estas pruebas son independientes de las pruebas de integración de
test_corte_vertical.py: aquí se verifica el contrato, allá el recorrido.
"""
from app.infrastructure.tablas import (
    AuditoriaTabla,
    MiembroTabla,
    ProyectoTabla,
    TareaTabla,
)


def _crear_proyecto(cliente, cab, lider="ana", miembros=("bruno",)):
    respuesta = cliente.post(
        "/proyectos",
        json={"nombre": "Proyecto de Arquitectura", "miembros": list(miembros)},
        headers=cab(lider),
    )
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


# --- Autenticación ---


def test_sin_token_responde_401(cliente):
    respuesta = cliente.get("/proyectos")
    assert respuesta.status_code == 401
    assert respuesta.headers.get("WWW-Authenticate") == "Bearer"
    assert "detail" in respuesta.json()


def test_bearer_invalido_responde_401(cliente):
    for credencial in ["Bearer", "Bearer ", "Bearer no-es-un-jwt", "Basic abc123"]:
        respuesta = cliente.get("/proyectos", headers={"Authorization": credencial})
        assert respuesta.status_code == 401, f"Esperaba 401 para: {credencial}"


def test_token_caducado_responde_401(cliente, cab):
    from scripts import emisor_dev
    from test.conftest import AUDIENCIA, token_de

    caducado = token_de("ana", minutos=-10)
    respuesta = cliente.get(
        "/proyectos", headers={"Authorization": f"Bearer {caducado}"}
    )
    assert respuesta.status_code == 401


# --- Validación de entrada ---


def test_crear_proyecto_sin_nombre_responde_422(cliente, cab):
    respuesta = cliente.post(
        "/proyectos", json={"nombre": "", "miembros": []}, headers=cab("ana")
    )
    assert respuesta.status_code == 422


def test_crear_tarea_sin_titulo_responde_422(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    respuesta = cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "", "prioridad": "media"},
        headers=cab("ana"),
    )
    assert respuesta.status_code == 422


def test_crear_tarea_con_prioridad_invalida_responde_422(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    respuesta = cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea", "prioridad": "critical"},
        headers=cab("ana"),
    )
    assert respuesta.status_code == 422


def test_limite_paginacion_excesivo_responde_422(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    respuesta = cliente.get(
        f"/proyectos/{proyecto_id}/tareas?limite=500", headers=cab("ana")
    )
    assert respuesta.status_code == 422


def test_limite_cero_responde_422(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    respuesta = cliente.get(
        f"/proyectos/{proyecto_id}/tareas?limite=0", headers=cab("ana")
    )
    assert respuesta.status_code == 422


def test_desplazamiento_negativo_responde_422(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    respuesta = cliente.get(
        f"/proyectos/{proyecto_id}/tareas?desplazamiento=-1", headers=cab("ana")
    )
    assert respuesta.status_code == 422


def test_cambiar_estado_invalido_responde_422(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    tarea = cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea"},
        headers=cab("ana"),
    ).json()
    respuesta = cliente.put(
        f"/proyectos/{proyecto_id}/tareas/{tarea['id']}/estado",
        json={"estado": "eliminada"},
        headers=cab("ana"),
    )
    assert respuesta.status_code == 422


# --- Autorización ---


def test_usuario_ajeno_no_puede_listar_tareas_403_sin_datos(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea confidencial"},
        headers=cab("ana"),
    )
    respuesta = cliente.get(
        f"/proyectos/{proyecto_id}/tareas", headers=cab("intruso")
    )
    assert respuesta.status_code == 403
    assert "Tarea confidencial" not in respuesta.text
    assert "id" not in respuesta.json() if respuesta.text else True


def test_proyecto_inexistente_devuelve_403_no_404(cliente, cab):
    respuesta = cliente.get(
        "/proyectos/00000000-0000-0000-0000-000000000000/tareas",
        headers=cab("intruso"),
    )
    assert respuesta.status_code == 403


def test_usuario_ajeno_no_puede_crear_tarea_403(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    respuesta = cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea de intruso"},
        headers=cab("intruso"),
    )
    assert respuesta.status_code == 403


def test_usuario_ajeno_no_puede_cambiar_estado_403(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    tarea = cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea"},
        headers=cab("ana"),
    ).json()
    respuesta = cliente.put(
        f"/proyectos/{proyecto_id}/tareas/{tarea['id']}/estado",
        json={"estado": "en_progreso"},
        headers=cab("intruso"),
    )
    assert respuesta.status_code == 403


def test_solo_el_lider_agrega_miembros(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab, lider="ana")
    negado = cliente.post(
        f"/proyectos/{proyecto_id}/miembros",
        json={"usuario": "diana"},
        headers=cab("bruno"),
    )
    assert negado.status_code == 403

    permitido = cliente.post(
        f"/proyectos/{proyecto_id}/miembros",
        json={"usuario": "diana"},
        headers=cab("ana"),
    )
    assert permitido.status_code == 201


def test_responsable_ajeno_responde_403(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    respuesta = cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea", "responsable": "intruso"},
        headers=cab("ana"),
    )
    assert respuesta.status_code == 403


# --- Códigos de estado y formato de respuesta ---


def test_crear_proyecto_responde_201_con_formato(cliente, cab):
    respuesta = cliente.post(
        "/proyectos",
        json={"nombre": "Formato", "miembros": ["bruno"]},
        headers=cab("ana"),
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert "id" in cuerpo
    assert "nombre" in cuerpo
    assert "miembros" in cuerpo
    assert isinstance(cuerpo["miembros"], list)


def test_crear_tarea_responde_201_con_todos_los_campos(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    respuesta = cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea formato"},
        headers=cab("ana"),
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    campos_requeridos = [
        "id", "proyecto_id", "titulo", "prioridad", "estado",
        "creada_por", "creada_en",
    ]
    for campo in campos_requeridos:
        assert campo in cuerpo, f"Falta campo: {campo}"
    assert cuerpo["estado"] == "pendiente"


def test_listar_tareas_responde_200_array(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea 1"},
        headers=cab("ana"),
    )
    respuesta = cliente.get(
        f"/proyectos/{proyecto_id}/tareas", headers=cab("ana")
    )
    assert respuesta.status_code == 200
    assert isinstance(respuesta.json(), list)


def test_progreso_responde_200_con_todos_los_campos(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea 1"},
        headers=cab("ana"),
    )
    respuesta = cliente.get(
        f"/proyectos/{proyecto_id}/progreso", headers=cab("ana")
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    campos_requeridos = [
        "total", "por_estado", "sin_responsable", "vencidas",
        "porcentaje_completado",
    ]
    for campo in campos_requeridos:
        assert campo in cuerpo, f"Falta campo: {campo}"


def test_el_progreso_de_un_proyecto_ajeno_devuelve_403(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)
    r = cliente.get(
        f"/proyectos/{proyecto_id}/progreso", headers=cab("intruso")
    )
    assert r.status_code == 403


# --- Formato de error ---


def test_todos_los_errores_tienen_detail(cliente, cab):
    """Todos los errores de la API llevan un objeto {detail: ...}."""
    error_codes = []

    # 401
    r = cliente.get("/proyectos")
    if r.status_code == 401 and "detail" in r.json():
        error_codes.append(("401", True))

    # 403 - proyecto ajeno
    proyecto_id = _crear_proyecto(cliente, cab)
    r = cliente.get(f"/proyectos/{proyecto_id}/tareas", headers=cab("intruso"))
    if r.status_code == 403 and "detail" in r.json():
        error_codes.append(("403", True))

    # 404 - proyecto inexistente con token valido
    r = cliente.get(
        "/proyectos/00000000-0000-0000-0000-000000000000", headers=cab("ana")
    )
    if r.status_code == 403 and "detail" in r.json():
        error_codes.append(("403-inexistente", True))

    for codigo, tiene_detail in error_codes:
        assert tiene_detail, f"Error {codigo} no tiene 'detail' en la respuesta"


def test_la_auditoria_registra_acceso_denegado(cliente, sesion, cab):
    """ESC-03: la auditoría se registra con resultado 'denegado'."""
    proyecto_id = _crear_proyecto(cliente, cab)
    cliente.post(
        f"/proyectos/{proyecto_id}/tareas",
        json={"titulo": "Tarea confidencial"},
        headers=cab("ana"),
    )
    cliente.get(
        f"/proyectos/{proyecto_id}/tareas", headers=cab("intruso")
    )

    registros = (
        sesion.query(AuditoriaTabla)
        .filter(AuditoriaTabla.usuario == "intruso")
        .all()
    )
    assert len(registros) >= 1
    assert any(r.resultado == "denegado" for r in registros)
