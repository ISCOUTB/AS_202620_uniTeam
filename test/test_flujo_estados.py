"""El flujo de estados vive en el dominio y solo en el dominio (ADR 0012, ESC-05).

La última prueba es la guardia de la táctica: falla si la Aplicación Web vuelve
a escribir a mano algún estado, que es justo el defecto que hacía que añadir
un estado obligara a tocar dos contenedores.
"""
import re
from pathlib import Path

import pytest

from app.domain.modelos import (
    ESTADO_FINAL,
    ESTADO_INICIAL,
    ETIQUETAS_ESTADO,
    TRANSICIONES,
    EstadoTarea,
)

RAIZ = Path(__file__).resolve().parent.parent


def test_la_api_publica_todos_los_estados_en_el_orden_del_dominio(cliente):
    respuesta = cliente.get("/flujo-estados")
    assert respuesta.status_code == 200
    estados = respuesta.json()["estados"]
    assert [e["id"] for e in estados] == [e.value for e in EstadoTarea]


def test_no_exige_credencial(cliente):
    assert cliente.get("/flujo-estados").status_code == 200


def test_las_transiciones_publicadas_son_las_del_dominio(cliente):
    estados = {e["id"]: e for e in cliente.get("/flujo-estados").json()["estados"]}
    for origen, destinos in TRANSICIONES.items():
        assert estados[origen.value]["siguientes"] == [d.value for d in destinos]


def test_hay_un_estado_inicial_y_uno_final(cliente):
    estados = cliente.get("/flujo-estados").json()["estados"]
    assert [e["id"] for e in estados if e["inicial"]] == [ESTADO_INICIAL.value]
    assert [e["id"] for e in estados if e["final"]] == [ESTADO_FINAL.value]


@pytest.mark.parametrize("estado", list(EstadoTarea))
def test_cada_estado_tiene_etiqueta_y_transiciones(estado):
    """Un estado nuevo sin etiqueta o sin transiciones rompería el tablero."""
    assert ETIQUETAS_ESTADO.get(estado), f"{estado.value} no tiene etiqueta"
    assert estado in TRANSICIONES, f"{estado.value} no tiene transiciones"
    assert all(d in EstadoTarea for d in TRANSICIONES[estado])


def test_todo_estado_es_alcanzable_desde_el_inicial():
    alcanzados, pendientes = {ESTADO_INICIAL}, [ESTADO_INICIAL]
    while pendientes:
        for destino in TRANSICIONES[pendientes.pop()]:
            if destino not in alcanzados:
                alcanzados.add(destino)
                pendientes.append(destino)
    assert alcanzados == set(EstadoTarea)


def test_la_aplicacion_web_no_escribe_estados_a_mano():
    """Guardia de ESC-05: los estados solo existen en el dominio.

    Busca los identificadores de estado en el código de la Aplicación Web. Si
    aparece alguno, añadir un estado volvería a exigir cambiar dos contenedores.
    """
    patron = re.compile(r"\b(" + "|".join(re.escape(e.value) for e in EstadoTarea) + r")\b")
    hallazgos = []
    for carpeta in ("web/app", "web/lib"):
        for fichero in sorted((RAIZ / carpeta).rglob("*")):
            if fichero.suffix not in {".ts", ".tsx", ".css"}:
                continue
            for n, linea in enumerate(fichero.read_text(encoding="utf-8").splitlines(), 1):
                if patron.search(linea):
                    hallazgos.append(f"{fichero.relative_to(RAIZ)}:{n}: {linea.strip()}")
    assert not hallazgos, "Estados escritos a mano en la Aplicación Web:\n" + "\n".join(hallazgos)


# -- ESC-05: el estado «En revisión» -------------------------------------------


def _tarea_en_progreso(cliente, cab):
    proyecto = cliente.post("/proyectos", json={"nombre": "P", "miembros": []}, headers=cab("ana")).json()["id"]
    tarea = cliente.post(f"/proyectos/{proyecto}/tareas", json={"titulo": "Informe"}, headers=cab("ana")).json()["id"]
    ruta = f"/proyectos/{proyecto}/tareas/{tarea}/estado"
    assert cliente.put(ruta, json={"estado": "en_progreso"}, headers=cab("ana")).status_code == 200
    return proyecto, ruta


def test_una_tarea_pasa_por_revision_antes_de_completarse(cliente, cab):
    proyecto, ruta = _tarea_en_progreso(cliente, cab)
    revision = cliente.put(ruta, json={"estado": "en_revision"}, headers=cab("ana"))
    assert revision.status_code == 200 and revision.json()["estado"] == "en_revision"
    assert cliente.put(ruta, json={"estado": "completada"}, headers=cab("ana")).status_code == 200
    progreso = cliente.get(f"/proyectos/{proyecto}/progreso", headers=cab("ana")).json()
    assert progreso["porcentaje_completado"] == 100.0


def test_la_revision_puede_devolver_la_tarea(cliente, cab):
    _, ruta = _tarea_en_progreso(cliente, cab)
    cliente.put(ruta, json={"estado": "en_revision"}, headers=cab("ana"))
    assert cliente.put(ruta, json={"estado": "en_progreso"}, headers=cab("ana")).status_code == 200


def test_completar_sin_revision_sigue_permitido(cliente, cab):
    """Compatibilidad: los clientes que ya pasaban de en_progreso a completada
    no se rompen al añadir el estado (ESC-05: 0 cambios incompatibles)."""
    _, ruta = _tarea_en_progreso(cliente, cab)
    assert cliente.put(ruta, json={"estado": "completada"}, headers=cab("ana")).status_code == 200


def test_no_se_llega_a_revision_desde_pendiente(cliente, cab):
    proyecto = cliente.post("/proyectos", json={"nombre": "P", "miembros": []}, headers=cab("ana")).json()["id"]
    tarea = cliente.post(f"/proyectos/{proyecto}/tareas", json={"titulo": "X"}, headers=cab("ana")).json()["id"]
    respuesta = cliente.put(
        f"/proyectos/{proyecto}/tareas/{tarea}/estado", json={"estado": "en_revision"}, headers=cab("ana")
    )
    assert respuesta.status_code == 409


def test_el_tablero_filtra_por_el_estado_nuevo(cliente, cab):
    proyecto, ruta = _tarea_en_progreso(cliente, cab)
    cliente.put(ruta, json={"estado": "en_revision"}, headers=cab("ana"))
    en_revision = cliente.get(
        f"/proyectos/{proyecto}/tareas", params={"estado": "en_revision"}, headers=cab("ana")
    ).json()
    assert len(en_revision) == 1
