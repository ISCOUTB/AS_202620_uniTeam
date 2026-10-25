"""Simulador local de mensajeria durable para el taller de arquitectura.

No forma parte de la aplicacion UniTeam. SQLite representa una cola con un
solo consumidor y deja visibles los limites de entrega, reintento y dedupe.
"""
from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from prometheus_client import CollectorRegistry, Counter, generate_latest


REGISTRO = CollectorRegistry()
PUBLICADOS = Counter(
    "taller_mensajes_publicados_total",
    "Mensajes aceptados por el productor de demostracion.",
    registry=REGISTRO,
)
PROCESADOS = Counter(
    "taller_mensajes_procesados_total",
    "Entregas aplicadas por el consumidor.",
    registry=REGISTRO,
)
DUPLICADOS = Counter(
    "taller_mensajes_duplicados_total",
    "Entregas omitidas porque el consumidor ya aplico ese mensaje.",
    registry=REGISTRO,
)
REINTENTOS = Counter(
    "taller_mensajes_reintentos_total",
    "Entregas programadas para otro intento.",
    registry=REGISTRO,
)
FALLIDOS = Counter(
    "taller_mensajes_cola_fallidos_total",
    "Mensajes que agotaron sus intentos y llegaron a la cola de fallidos.",
    registry=REGISTRO,
)

logger = logging.getLogger("taller.mensajeria")
TIPO_EVENTO = "tarea.creada"
VERSION_CONTRATO = 1


def _texto_no_vacio(valor: object, campo: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"El campo {campo} debe ser texto no vacio.")
    return valor


@dataclass(frozen=True)
class MensajeTareaCreada:
    """Contrato versionado del evento que publica la creacion de una tarea.

    Los campos adicionales se ignoran al leer; los campos obligatorios y su
    significado no cambian dentro de la version 1.
    """

    message_id: str
    occurred_at: str
    correlation_id: str
    tarea_id: str
    proyecto_id: str
    creada_por: str

    @classmethod
    def crear(
        cls, tarea_id: str, proyecto_id: str, creada_por: str
    ) -> MensajeTareaCreada:
        return cls(
            message_id=str(uuid.uuid4()),
            occurred_at=datetime.now(timezone.utc).isoformat(),
            correlation_id=str(uuid.uuid4()),
            tarea_id=_texto_no_vacio(tarea_id, "tarea_id"),
            proyecto_id=_texto_no_vacio(proyecto_id, "proyecto_id"),
            creada_por=_texto_no_vacio(creada_por, "creada_por"),
        )

    def serializar(self) -> str:
        return json.dumps(
            {
                "schema_version": VERSION_CONTRATO,
                "message_id": self.message_id,
                "event_type": TIPO_EVENTO,
                "occurred_at": self.occurred_at,
                "correlation_id": self.correlation_id,
                "payload": {
                    "tarea_id": self.tarea_id,
                    "proyecto_id": self.proyecto_id,
                    "creada_por": self.creada_por,
                },
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @classmethod
    def deserializar(cls, contenido: str) -> MensajeTareaCreada:
        try:
            documento = json.loads(contenido)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("El mensaje no contiene JSON valido.") from exc
        if not isinstance(documento, dict):
            raise ValueError("El mensaje debe ser un objeto JSON.")
        if type(documento.get("schema_version")) is not int:
            raise ValueError("schema_version debe ser un entero.")
        if documento["schema_version"] != VERSION_CONTRATO:
            raise ValueError(
                f"Version no compatible: {documento['schema_version']}."
            )
        if documento.get("event_type") != TIPO_EVENTO:
            raise ValueError("event_type no compatible.")

        payload = documento.get("payload")
        if not isinstance(payload, dict):
            raise ValueError("payload debe ser un objeto JSON.")
        try:
            occurred_at = datetime.fromisoformat(documento["occurred_at"])
            if occurred_at.tzinfo is None:
                raise ValueError("occurred_at debe incluir zona horaria.")
            return cls(
                message_id=_texto_no_vacio(documento["message_id"], "message_id"),
                occurred_at=occurred_at.astimezone(timezone.utc).isoformat(),
                correlation_id=_texto_no_vacio(
                    documento["correlation_id"], "correlation_id"
                ),
                tarea_id=_texto_no_vacio(payload["tarea_id"], "tarea_id"),
                proyecto_id=_texto_no_vacio(payload["proyecto_id"], "proyecto_id"),
                creada_por=_texto_no_vacio(payload["creada_por"], "creada_por"),
            )
        except (KeyError, TypeError) as exc:
            raise ValueError("Falta un campo obligatorio del contrato.") from exc


Consumidor = Callable[[MensajeTareaCreada, sqlite3.Connection], None]


class ColaSQLite:
    """Cola local durable con un consumidor y reintento exponencial acotado.

    El efecto del consumidor debe participar en la transaccion SQLite que
    confirma la recepcion. No se deben hacer llamadas de red en esa transaccion.
    """

    def __init__(
        self,
        base_datos: str | Path,
        *,
        max_intentos: int = 3,
        demora_base_segundos: float = 1.0,
        reloj: Callable[[], float] = time.time,
    ) -> None:
        if max_intentos < 1:
            raise ValueError("max_intentos debe ser al menos 1.")
        if demora_base_segundos < 0:
            raise ValueError("demora_base_segundos no puede ser negativa.")
        self._reloj = reloj
        self._max_intentos = max_intentos
        self._demora_base = demora_base_segundos
        if str(base_datos) != ":memory:":
            Path(base_datos).parent.mkdir(parents=True, exist_ok=True)
        self._conexion = sqlite3.connect(str(base_datos), timeout=10)
        self._conexion.row_factory = sqlite3.Row
        self._conexion.executescript(
            """
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                contenido TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'pendiente',
                intentos INTEGER NOT NULL DEFAULT 0,
                disponible_en REAL NOT NULL,
                ultimo_error TEXT
            );
            CREATE INDEX IF NOT EXISTS ix_mensajes_disponibles
                ON mensajes(estado, disponible_en, id);
            CREATE TABLE IF NOT EXISTS recibidos (
                message_id TEXT PRIMARY KEY,
                recibido_en REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS notificaciones_demo (
                message_id TEXT PRIMARY KEY,
                tarea_id TEXT NOT NULL,
                proyecto_id TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS mensajes_fallidos (
                id INTEGER PRIMARY KEY,
                message_id TEXT NOT NULL,
                contenido TEXT NOT NULL,
                intentos INTEGER NOT NULL,
                error TEXT NOT NULL,
                fallido_en REAL NOT NULL
            );
            """
        )

    def cerrar(self) -> None:
        self._conexion.close()

    def __enter__(self) -> ColaSQLite:
        return self

    def __exit__(self, *_exc) -> None:
        self.cerrar()

    def publicar(self, mensaje: MensajeTareaCreada) -> int:
        contenido = mensaje.serializar()
        with self._conexion:
            cursor = self._conexion.execute(
                """
                INSERT INTO mensajes
                    (message_id, correlation_id, contenido, disponible_en)
                VALUES (?, ?, ?, ?)
                """,
                (
                    mensaje.message_id,
                    mensaje.correlation_id,
                    contenido,
                    self._reloj(),
                ),
            )
        PUBLICADOS.inc()
        logger.info(
            "Mensaje publicado",
            extra={
                "evento": "mensaje_publicado",
                "message_id": mensaje.message_id,
                "correlation_id": mensaje.correlation_id,
                "event_type": TIPO_EVENTO,
            },
        )
        return int(cursor.lastrowid)

    def procesar_siguiente(self, consumidor: Consumidor) -> bool:
        """Procesa un mensaje listo; retorna False si no hay trabajo disponible."""
        self._conexion.execute("BEGIN IMMEDIATE")
        fila = self._conexion.execute(
            """
            SELECT id, message_id, correlation_id, contenido, intentos
            FROM mensajes
            WHERE estado = 'pendiente' AND disponible_en <= ?
            ORDER BY id
            LIMIT 1
            """,
            (self._reloj(),),
        ).fetchone()
        if fila is None:
            self._conexion.commit()
            return False

        intento = fila["intentos"] + 1
        try:
            mensaje = MensajeTareaCreada.deserializar(fila["contenido"])
            ya_recibido = self._conexion.execute(
                "SELECT 1 FROM recibidos WHERE message_id = ?",
                (mensaje.message_id,),
            ).fetchone()
            if ya_recibido is None:
                consumidor(mensaje, self._conexion)
                self._conexion.execute(
                    "INSERT INTO recibidos (message_id, recibido_en) VALUES (?, ?)",
                    (mensaje.message_id, self._reloj()),
                )
            self._conexion.execute(
                """
                UPDATE mensajes
                SET estado = 'entregado', intentos = ?, ultimo_error = NULL
                WHERE id = ?
                """,
                (intento, fila["id"]),
            )
            self._conexion.commit()
        except Exception as exc:
            self._conexion.rollback()
            error = f"{type(exc).__name__}: {exc}"[:1000]
            fallido = intento >= self._max_intentos
            proximo_intento = self._reloj() + (
                self._demora_base * 2 ** (intento - 1)
            )
            with self._conexion:
                if fallido:
                    self._conexion.execute(
                        """
                        INSERT INTO mensajes_fallidos
                            (id, message_id, contenido, intentos, error, fallido_en)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            fila["id"],
                            fila["message_id"],
                            fila["contenido"],
                            intento,
                            error,
                            self._reloj(),
                        ),
                    )
                    self._conexion.execute(
                        """
                        UPDATE mensajes
                        SET estado = 'fallido', intentos = ?, ultimo_error = ?
                        WHERE id = ?
                        """,
                        (intento, error, fila["id"]),
                    )
                    FALLIDOS.inc()
                else:
                    self._conexion.execute(
                        """
                        UPDATE mensajes
                        SET intentos = ?, disponible_en = ?, ultimo_error = ?
                        WHERE id = ?
                        """,
                        (intento, proximo_intento, error, fila["id"]),
                    )
                    REINTENTOS.inc()
            logger.warning(
                "Fallo al consumir mensaje",
                exc_info=True,
                extra={
                    "evento": "mensaje_fallido" if fallido else "mensaje_reintento",
                    "message_id": fila["message_id"],
                    "correlation_id": fila["correlation_id"],
                    "intento": intento,
                    "proximo_intento_en": None if fallido else proximo_intento,
                },
            )
            return True

        if ya_recibido is not None:
            DUPLICADOS.inc()
            logger.info(
                "Entrega duplicada omitida",
                extra={
                    "evento": "mensaje_duplicado",
                    "message_id": mensaje.message_id,
                    "correlation_id": mensaje.correlation_id,
                },
            )
        else:
            PROCESADOS.inc()
            logger.info(
                "Mensaje consumido",
                extra={
                    "evento": "mensaje_consumido",
                    "message_id": mensaje.message_id,
                    "correlation_id": mensaje.correlation_id,
                    "intento": intento,
                },
            )
        return True

    def estados(self, message_id: str) -> list[tuple[str, int]]:
        filas = self._conexion.execute(
            "SELECT estado, intentos FROM mensajes WHERE message_id = ? ORDER BY id",
            (message_id,),
        ).fetchall()
        return [(fila["estado"], fila["intentos"]) for fila in filas]

    def fallidos(self) -> list[MensajeTareaCreada]:
        filas = self._conexion.execute(
            "SELECT contenido FROM mensajes_fallidos ORDER BY id"
        ).fetchall()
        return [
            MensajeTareaCreada.deserializar(fila["contenido"]) for fila in filas
        ]

    def notificaciones(self) -> list[tuple[str, str]]:
        filas = self._conexion.execute(
            "SELECT message_id, tarea_id FROM notificaciones_demo ORDER BY rowid"
        ).fetchall()
        return [(fila["message_id"], fila["tarea_id"]) for fila in filas]


def consumir_notificacion_demo(
    mensaje: MensajeTareaCreada, conexion: sqlite3.Connection
) -> None:
    """Efecto local de ejemplo: una notificacion por identificador de mensaje."""
    conexion.execute(
        """
        INSERT INTO notificaciones_demo (message_id, tarea_id, proyecto_id)
        VALUES (?, ?, ?)
        """,
        (mensaje.message_id, mensaje.tarea_id, mensaje.proyecto_id),
    )


def metricas_prometheus() -> bytes:
    return generate_latest(REGISTRO)


def _demo(ruta: str) -> None:
    instante = [time.time()]

    def reloj() -> float:
        return instante[0]

    mensaje = MensajeTareaCreada.crear(
        tarea_id="tarea-demo", proyecto_id="proyecto-demo", creada_por="equipo-demo"
    )
    fallar_una_vez = [True]

    def consumidor(
        evento: MensajeTareaCreada, conexion: sqlite3.Connection
    ) -> None:
        if fallar_una_vez[0]:
            fallar_una_vez[0] = False
            raise RuntimeError("fallo recuperable simulado")
        consumir_notificacion_demo(evento, conexion)

    with ColaSQLite(ruta, demora_base_segundos=1, reloj=reloj) as cola:
        cola.publicar(mensaje)
        cola.procesar_siguiente(consumidor)
        instante[0] += 1
        cola.procesar_siguiente(consumidor)
        print(f"Estado del mensaje: {cola.estados(mensaje.message_id)}")
        print(f"Notificaciones: {cola.notificaciones()}")
        print(metricas_prometheus().decode("utf-8"), end="")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(levelname)s %(message)s "
            "message_id=%(message_id)s correlation_id=%(correlation_id)s"
        ),
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-datos",
        default=":memory:",
        help="Ruta SQLite persistente; :memory: si se omite.",
    )
    _demo(parser.parse_args().base_datos)
