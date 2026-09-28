"""Defectos encontrados en la revisión del 2026-09-28, uno por prueba.

Cada prueba reproduce un fallo que existía antes de su corrección: si alguna
vuelve a fallar, el defecto ha regresado.
"""
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from app.config import ajustes
from test.conftest import token_de


def _proyecto(cliente, cab, usuario="ana", miembros=()):
    respuesta = cliente.post(
        "/proyectos",
        json={"nombre": "Arquitectura", "miembros": list(miembros)},
        headers=cab(usuario),
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["id"]


# -- Identidades --------------------------------------------------------------


def test_el_correo_de_un_miembro_no_distingue_mayusculas(cliente, cab):
    """Se añadía «Bruno@UTB.edu.co» y Bruno, que entra como «bruno@utb.edu.co»,
    no veía el proyecto: la pertenencia comparaba cadenas exactas."""
    proyecto = _proyecto(cliente, cab, "ana@utb.edu.co", ["  Bruno@UTB.edu.co "])

    vistos = cliente.get("/proyectos", headers=cab("bruno@utb.edu.co")).json()
    assert [p["id"] for p in vistos] == [proyecto]
    assert "bruno@utb.edu.co" in {m["usuario"] for m in vistos[0]["miembros"]}


def test_la_identidad_del_token_tambien_se_normaliza(cliente, cab):
    proyecto = _proyecto(cliente, cab, "ana@utb.edu.co")
    respuesta = cliente.get(f"/proyectos/{proyecto}", headers=cab("ANA@utb.edu.co"))
    assert respuesta.status_code == 200


# -- Validación ---------------------------------------------------------------


def test_un_miembro_demasiado_largo_se_rechaza_con_422_y_no_con_500(cliente, cab):
    """La columna admite 120 caracteres; la lista de miembros no tenía límite y
    MySQL respondía con un error interno."""
    respuesta = cliente.post(
        "/proyectos",
        json={"nombre": "Arquitectura", "miembros": ["x" * 121]},
        headers=cab("ana"),
    )
    assert respuesta.status_code == 422


@pytest.mark.parametrize("titulo", ["   ", "\t\n"])
def test_un_titulo_en_blanco_se_rechaza(cliente, cab, titulo):
    proyecto = _proyecto(cliente, cab)
    respuesta = cliente.post(
        f"/proyectos/{proyecto}/tareas", json={"titulo": titulo}, headers=cab("ana")
    )
    assert respuesta.status_code == 422


def test_titulo_y_nombre_se_guardan_sin_espacios_sobrantes(cliente, cab):
    creado = cliente.post(
        "/proyectos", json={"nombre": "  Arquitectura  ", "miembros": []}, headers=cab("ana")
    ).json()
    assert creado["nombre"] == "Arquitectura"
    tarea = cliente.post(
        f"/proyectos/{creado['id']}/tareas", json={"titulo": "  Informe  "}, headers=cab("ana")
    ).json()
    assert tarea["titulo"] == "Informe"


# -- Fechas -------------------------------------------------------------------


def test_una_tarea_que_vence_hoy_en_colombia_no_cuenta_como_vencida(cliente, cab, monkeypatch):
    """A partir de las 19:00 en Colombia ya es el día siguiente en UTC, y el
    servidor —en UTC— contaba como vencidas las tareas que vencían ese día."""
    ahora_utc = datetime(2026, 9, 28, 2, 0, tzinfo=timezone.utc)  # 21:00 del 27 en Bogotá
    hoy_en_colombia = ahora_utc.astimezone(ZoneInfo("America/Bogota")).date()
    assert hoy_en_colombia == date(2026, 9, 27)

    monkeypatch.setattr(
        "app.infrastructure.repositorios._ahora_utc", lambda: ahora_utc
    )
    proyecto = _proyecto(cliente, cab)
    cliente.post(
        f"/proyectos/{proyecto}/tareas",
        json={"titulo": "Vence hoy", "fecha_limite": str(hoy_en_colombia)},
        headers=cab("ana"),
    )
    cliente.post(
        f"/proyectos/{proyecto}/tareas",
        json={"titulo": "Venció ayer", "fecha_limite": str(hoy_en_colombia - timedelta(days=1))},
        headers=cab("ana"),
    )

    progreso = cliente.get(f"/proyectos/{proyecto}/progreso", headers=cab("ana")).json()
    assert progreso["vencidas"] == 1
    assert ajustes.zona_horaria == "America/Bogota"


# -- Registro -----------------------------------------------------------------


def test_los_health_checks_correctos_no_llenan_el_registro(cliente, caplog):
    """Render consulta /health continuamente, y un ping de mantenimiento cada
    minuto son 1 440 líneas al día que no dicen nada."""
    import logging

    with caplog.at_level(logging.INFO, logger="uniteam.peticion"):
        cliente.get("/health")
        cliente.get("/activo")
    assert not [r for r in caplog.records if r.name == "uniteam.peticion"]


def test_un_token_de_otro_usuario_no_se_confunde_por_mayusculas(cliente):
    """Normalizar no puede hacer que dos personas distintas coincidan."""
    proyecto = cliente.post(
        "/proyectos",
        json={"nombre": "Privado", "miembros": []},
        headers={"Authorization": f"Bearer {token_de('ana@utb.edu.co')}"},
    ).json()["id"]
    ajeno = cliente.get(
        f"/proyectos/{proyecto}",
        headers={"Authorization": f"Bearer {token_de('ana@otra.edu.co')}"},
    )
    assert ajeno.status_code == 403
