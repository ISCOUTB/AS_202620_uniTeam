"""Señales de operación: health check, logs estructurados y métricas (S8).

Comprueban que las señales que se consultan en el entorno desplegado existen,
dicen la verdad y no filtran datos personales.
"""
import json
import logging

import pytest

from app import observabilidad
from app.main import app


def _proyecto_con_tarea(cliente, cab) -> str:
    proyecto = cliente.post(
        "/proyectos", json={"nombre": "Operación", "miembros": []}, headers=cab("ana")
    ).json()["id"]
    cliente.post(
        f"/proyectos/{proyecto}/tareas", json={"titulo": "Medir"}, headers=cab("ana")
    )
    return proyecto


# -- Health check ---------------------------------------------------------


def test_health_responde_200_cuando_la_base_de_datos_contesta(cliente):
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "ok"
    assert cuerpo["base_de_datos"] == "ok"
    assert {"version", "revision", "entorno", "latencia_bd_ms"} <= cuerpo.keys()


def test_health_no_exige_credencial(cliente):
    """El proveedor de despliegue lo consulta sin token."""
    assert cliente.get("/health").status_code == 200


def test_health_responde_503_si_la_base_de_datos_no_contesta(cliente, monkeypatch):
    class MotorCaido:
        def connect(self):
            raise ConnectionError("sin base de datos")

    monkeypatch.setattr("app.main.engine", MotorCaido())
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 503
    assert respuesta.json()["base_de_datos"] == "caida"


# -- Logs estructurados ---------------------------------------------------


def test_cada_peticion_deja_una_linea_json_con_campos(cliente, cab, caplog):
    proyecto = _proyecto_con_tarea(cliente, cab)
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="uniteam.peticion"):
        respuesta = cliente.get(f"/proyectos/{proyecto}/tareas", headers=cab("ana"))

    registro = next(r for r in caplog.records if r.name == "uniteam.peticion")
    linea = json.loads(observabilidad.FormatoJSON().format(registro))

    assert linea["evento"] == "peticion"
    assert linea["metodo"] == "GET"
    assert linea["estado"] == 200
    assert isinstance(linea["duracion_ms"], float)
    assert linea["id_peticion"] == respuesta.headers["X-Request-ID"]


def test_el_log_registra_la_plantilla_de_ruta_y_no_datos_personales(cliente, cab, caplog):
    """Ni el identificador del proyecto ni el correo del usuario llegan al log."""
    proyecto = _proyecto_con_tarea(cliente, cab)
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="uniteam.peticion"):
        cliente.get(f"/proyectos/{proyecto}/tareas", headers=cab("ana@utb.edu.co"))

    registro = next(r for r in caplog.records if r.name == "uniteam.peticion")
    linea = observabilidad.FormatoJSON().format(registro)

    assert '"ruta": "/proyectos/{proyecto_id}/tareas"' in linea
    assert proyecto not in linea
    assert "ana@utb.edu.co" not in linea


def test_se_respeta_el_identificador_de_peticion_entrante(cliente):
    respuesta = cliente.get("/activo", headers={"X-Request-ID": "traza-123"})
    assert respuesta.headers["X-Request-ID"] == "traza-123"


def test_el_formato_json_incluye_la_excepcion():
    try:
        raise ValueError("fallo de prueba")
    except ValueError:
        registro = logging.LogRecord(
            "uniteam", logging.ERROR, __file__, 1, "algo falló", (), __import__("sys").exc_info()
        )
    linea = json.loads(observabilidad.FormatoJSON().format(registro))
    assert linea["nivel"] == "ERROR"
    assert "ValueError: fallo de prueba" in linea["excepcion"]


# -- Métricas -------------------------------------------------------------


def test_metricas_en_formato_prometheus(cliente):
    cliente.get("/activo")
    respuesta = cliente.get("/metricas")
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("text/plain")
    assert "uniteam_peticiones_total" in respuesta.text
    assert "uniteam_tablero_latencia_segundos" in respuesta.text


def test_la_consulta_del_tablero_alimenta_la_metrica_de_esc01(cliente, cab):
    observabilidad.ESC01.reiniciar()
    proyecto = _proyecto_con_tarea(cliente, cab)
    for _ in range(5):
        assert cliente.get(f"/proyectos/{proyecto}/tareas", headers=cab("ana")).status_code == 200

    resumen = cliente.get("/metricas/esc-01").json()
    assert resumen["escenario"] == "ESC-01"
    assert resumen["muestras"] == 5
    assert resumen["umbral_p95_s"] == 2.0
    assert resumen["p95_s"] is not None
    assert resumen["cumple"] is True


def test_una_consulta_denegada_no_cuenta_como_latencia_del_tablero(cliente, cab):
    """ESC-01 mide respuestas útiles; un 403 rápido lo maquillaría."""
    observabilidad.ESC01.reiniciar()
    proyecto = _proyecto_con_tarea(cliente, cab)
    assert cliente.get(f"/proyectos/{proyecto}/tareas", headers=cab("intruso")).status_code == 403
    assert cliente.get("/metricas/esc-01").json()["muestras"] == 0


def test_sin_muestras_el_resumen_no_afirma_que_se_cumpla(cliente):
    observabilidad.ESC01.reiniciar()
    resumen = cliente.get("/metricas/esc-01").json()
    assert resumen["muestras"] == 0
    assert resumen["cumple"] is None


def test_el_acceso_denegado_incrementa_la_metrica_de_esc03(cliente, cab):
    proyecto = _proyecto_con_tarea(cliente, cab)
    antes = observabilidad.ACCESOS_DENEGADOS._value.get()
    cliente.get(f"/proyectos/{proyecto}/tareas", headers=cab("intruso"))
    assert observabilidad.ACCESOS_DENEGADOS._value.get() == antes + 1


@pytest.mark.parametrize("p, esperado", [(50, 0.5), (95, 0.95), (99, 0.99)])
def test_percentil_por_rango_mas_cercano(p, esperado):
    valores = [i / 100 for i in range(1, 101)]
    assert observabilidad.VentanaESC01._percentil(valores, p) == esperado


def test_las_rutas_de_operacion_estan_publicadas():
    rutas = {getattr(r, "path", None) for r in app.routes}
    assert {"/health", "/activo", "/metricas", "/metricas/esc-01"} <= rutas
