import json
import logging
import sqlite3

import pytest

from scripts import taller_mensajeria as taller


def _mensaje(**cambios):
    original = taller.MensajeTareaCreada.crear(
        tarea_id="tarea-1", proyecto_id="proyecto-1", creada_por="ana"
    )
    return taller.MensajeTareaCreada(
        **{
            **original.__dict__,
            **cambios,
        }
    )


def test_contrato_acepta_campos_aditivos_y_rechaza_versiones_incompatibles():
    mensaje = _mensaje()
    documento = json.loads(mensaje.serializar())
    documento["future_optional_field"] = "compatible"

    assert taller.MensajeTareaCreada.deserializar(
        json.dumps(documento)
    ) == mensaje

    documento["schema_version"] = 2
    with pytest.raises(ValueError, match="Version no compatible"):
        taller.MensajeTareaCreada.deserializar(json.dumps(documento))


def test_deduplica_entrega_repetida_sin_repetir_el_efecto(tmp_path, caplog):
    mensaje = _mensaje()
    caplog.set_level(logging.INFO, logger="taller.mensajeria")
    with taller.ColaSQLite(tmp_path / "cola.db") as cola:
        cola.publicar(mensaje)
        cola.publicar(mensaje)
        assert cola.procesar_siguiente(taller.consumir_notificacion_demo)
        assert cola.procesar_siguiente(taller.consumir_notificacion_demo)

        assert cola.estados(mensaje.message_id) == [
            ("entregado", 1),
            ("entregado", 1),
        ]
        assert cola.notificaciones() == [(mensaje.message_id, "tarea-1")]
        registros = [r for r in caplog.records if hasattr(r, "correlation_id")]
        assert {r.correlation_id for r in registros} == {mensaje.correlation_id}
        assert "mensaje_duplicado" in {r.evento for r in registros}


def test_fallo_recuperable_reintenta_con_backoff_y_persiste_entre_instancias(
    tmp_path, caplog
):
    reloj = [100.0]
    ruta = tmp_path / "cola.db"
    mensaje = _mensaje()
    fallar_una_vez = [True]

    def consumidor(evento, conexion: sqlite3.Connection):
        if fallar_una_vez[0]:
            fallar_una_vez[0] = False
            raise RuntimeError("fallo temporal")
        taller.consumir_notificacion_demo(evento, conexion)

    caplog.set_level(logging.INFO, logger="taller.mensajeria")
    with taller.ColaSQLite(
        ruta, demora_base_segundos=5, reloj=lambda: reloj[0]
    ) as cola:
        cola.publicar(mensaje)
        assert cola.procesar_siguiente(consumidor)
        assert cola.estados(mensaje.message_id) == [("pendiente", 1)]
        assert cola.procesar_siguiente(consumidor) is False

    reloj[0] += 5
    with taller.ColaSQLite(
        ruta, demora_base_segundos=5, reloj=lambda: reloj[0]
    ) as cola:
        assert cola.procesar_siguiente(consumidor)
        assert cola.estados(mensaje.message_id) == [("entregado", 2)]
        assert cola.notificaciones() == [(mensaje.message_id, "tarea-1")]

    assert "mensaje_publicado" in {r.evento for r in caplog.records}
    assert "mensaje_reintento" in {r.evento for r in caplog.records}
    assert "mensaje_consumido" in {r.evento for r in caplog.records}
    assert all(
        r.correlation_id == mensaje.correlation_id
        for r in caplog.records
        if hasattr(r, "correlation_id")
    )
    metricas = taller.metricas_prometheus().decode("utf-8")
    assert "taller_mensajes_reintentos_total 1.0" in metricas


def test_agotar_intentos_envia_el_mensaje_a_fallidos(tmp_path):
    reloj = [0.0]
    mensaje = _mensaje()
    with taller.ColaSQLite(
        tmp_path / "cola.db",
        max_intentos=2,
        demora_base_segundos=2,
        reloj=lambda: reloj[0],
    ) as cola:
        def consumidor_fallido(_mensaje, _conexion):
            raise RuntimeError("fallo permanente")

        cola.publicar(mensaje)
        cola.procesar_siguiente(consumidor_fallido)
        reloj[0] += 2
        cola.procesar_siguiente(consumidor_fallido)

        assert cola.estados(mensaje.message_id) == [("fallido", 2)]
        assert cola.fallidos() == [mensaje]
