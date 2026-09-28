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
