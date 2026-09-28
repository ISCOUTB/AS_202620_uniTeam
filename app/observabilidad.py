"""Señales de operación de la API: registro estructurado y métricas.

Tres señales, cada una con su pregunta:

- **Registro estructurado.** Una línea JSON por evento, con campos y no con
  frases: se filtra por `ruta`, `estado` o `id_peticion` en el visor de logs
  del proveedor sin escribir expresiones regulares.
- **Métricas en formato Prometheus** (`/metricas`). Contadores e histogramas
  que cualquier recolector compatible puede raspar.
- **Resumen de ESC-01** (`/metricas/esc-01`). El p95 del tablero en una
  ventana deslizante, contrastado con el umbral del escenario. Es la métrica
  que liga la operación con la arquitectura: responde «¿se cumple ESC-01
  ahora mismo?» con un número, no con una opinión.

**Qué no se registra.** Ni el cuerpo de las peticiones ni la identidad del
usuario: el correo es un dato personal (restricción L1 de arc42) y los logs
viven en un tercero. Las rutas se registran como plantilla
(`/proyectos/{proyecto_id}/tareas`), no con el identificador concreto, por la
misma razón y para que las métricas no crezcan sin control.
"""
from __future__ import annotations

import json
import logging
import math
import os
import sys
import threading
import time
import uuid
from collections import deque
from datetime import datetime, timezone

from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# -- Registro estructurado ------------------------------------------------

# Atributos que `logging` pone en todo registro. Lo que no esté aquí y llegue
# por `extra=` es un campo nuestro y va a la línea JSON.
_ATRIBUTOS_ESTANDAR = set(
    logging.LogRecord("", 0, "", 0, "", (), None).__dict__
) | {"message", "asctime", "taskName", "color_message"}


class FormatoJSON(logging.Formatter):
    """Una línea JSON por registro, con los campos que se pasen en `extra`."""

    def format(self, registro: logging.LogRecord) -> str:
        linea = {
            "momento": datetime.fromtimestamp(registro.created, timezone.utc)
            .isoformat(timespec="milliseconds"),
            "nivel": registro.levelname,
            "origen": registro.name,
            "mensaje": registro.getMessage(),
        }
        for clave, valor in registro.__dict__.items():
            if clave not in _ATRIBUTOS_ESTANDAR and not clave.startswith("_"):
                linea[clave] = valor
        if registro.exc_info:
            linea["excepcion"] = self.formatException(registro.exc_info)
        return json.dumps(linea, ensure_ascii=False, default=str)


def configurar_registro() -> None:
    """Todo el registro de la API sale en JSON por la salida estándar.

    La salida estándar es donde el proveedor de despliegue recoge los logs;
    escribir a un fichero no serviría en un contenedor con disco efímero.
    """
    manejador = logging.StreamHandler(sys.stdout)
    manejador.setFormatter(FormatoJSON())

    raiz = logging.getLogger()
    raiz.handlers[:] = [manejador]
    raiz.setLevel(os.getenv("NIVEL_LOG", "INFO").upper())

    # Uvicorn trae sus propios manejadores en texto plano. Sus errores pasan
    # al manejador JSON; su registro de accesos se apaga porque el middleware
    # de abajo escribe uno mejor, con duración, ruta y trazabilidad.
    for nombre in ("uvicorn", "uvicorn.error"):
        logging.getLogger(nombre).handlers.clear()
        logging.getLogger(nombre).propagate = True
    logging.getLogger("uvicorn.access").disabled = True


registro_peticiones = logging.getLogger("uniteam.peticion")

# -- Métricas -------------------------------------------------------------

# Registro propio en lugar del global: las pruebas crean la aplicación más de
# una vez y el global rechazaría las métricas duplicadas.
REGISTRO = CollectorRegistry()

# Cubetas alrededor de los umbrales de ESC-01: 2 s (p95) y 4 s (p99).
_CUBETAS = (0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0)

PETICIONES = Counter(
    "uniteam_peticiones_total",
    "Peticiones HTTP atendidas, por método, ruta y código de estado.",
    ["metodo", "ruta", "estado"],
    registry=REGISTRO,
)
DURACION = Histogram(
    "uniteam_peticion_duracion_segundos",
    "Duración de las peticiones HTTP en la API.",
    ["metodo", "ruta"],
    buckets=_CUBETAS,
    registry=REGISTRO,
)
TABLERO = Histogram(
    "uniteam_tablero_latencia_segundos",
    "ESC-01 · Latencia de la consulta del tablero (GET /proyectos/{id}/tareas).",
    buckets=_CUBETAS,
    registry=REGISTRO,
)
ACCESOS_DENEGADOS = Counter(
    "uniteam_accesos_denegados_total",
    "ESC-03 · Accesos denegados por no pertenecer al proyecto, ya auditados.",
    registry=REGISTRO,
)

RUTA_TABLERO = "/proyectos/{proyecto_id}/tareas"
_RUTAS_DE_SONDEO = frozenset({"/health", "/activo"})


def exponer_metricas() -> Response:
    return Response(generate_latest(REGISTRO), media_type="text/plain; version=0.0.4")


class VentanaESC01:
    """Latencias recientes del tablero, para calcular percentiles al vuelo.

    El histograma de Prometheus sirve para un recolector, pero sus percentiles
    se estiman por cubetas. Esta ventana guarda las últimas muestras reales y
    da el p95 exacto sobre ellas, que es lo que el escenario compromete.
    """

    UMBRAL_P95 = 2.0
    UMBRAL_P99 = 4.0

    def __init__(self, tamano: int = 1000) -> None:
        self._muestras: deque[float] = deque(maxlen=tamano)
        self._candado = threading.Lock()

    def observar(self, segundos: float) -> None:
        with self._candado:
            self._muestras.append(segundos)

    def reiniciar(self) -> None:
        with self._candado:
            self._muestras.clear()

    @staticmethod
    def _percentil(ordenadas: list[float], p: float) -> float:
        # Método del rango más cercano: el menor valor que deja por debajo al
        # menos el p % de las muestras. El mismo de scripts/medir_esc01.py.
        indice = math.ceil(p / 100 * len(ordenadas)) - 1
        return ordenadas[min(max(indice, 0), len(ordenadas) - 1)]

    def resumen(self) -> dict:
        with self._candado:
            ordenadas = sorted(self._muestras)

        base = {
            "escenario": "ESC-01",
            "descripcion": "Latencia de la consulta del tablero en la API",
            "umbral_p95_s": self.UMBRAL_P95,
            "umbral_p99_s": self.UMBRAL_P99,
            "ventana": self._muestras.maxlen,
            "muestras": len(ordenadas),
            "alcance": (
                "Tiempo dentro de la API. ESC-01 mide de extremo a extremo; la red "
                "y el navegador se suman a esto y se miden con scripts/medir_esc01.py."
            ),
        }
        if not ordenadas:
            return {**base, "p50_s": None, "p95_s": None, "p99_s": None, "cumple": None}

        p95 = self._percentil(ordenadas, 95)
        p99 = self._percentil(ordenadas, 99)
        return {
            **base,
            "p50_s": round(self._percentil(ordenadas, 50), 4),
            "p95_s": round(p95, 4),
            "p99_s": round(p99, 4),
            "cumple": p95 <= self.UMBRAL_P95 and p99 <= self.UMBRAL_P99,
        }


ESC01 = VentanaESC01()


# -- Middleware -----------------------------------------------------------


class ObservarPeticiones(BaseHTTPMiddleware):
    """Mide, cuenta y registra cada petición en una sola línea."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Se respeta el identificador que traiga un proxy delante; si no hay,
        # se crea. Viaja de vuelta en la respuesta para poder citarlo.
        id_peticion = request.headers.get("x-request-id") or uuid.uuid4().hex
        inicio = time.perf_counter()
        estado = 500
        try:
            respuesta = await call_next(request)
            estado = respuesta.status_code
            respuesta.headers["X-Request-ID"] = id_peticion
            return respuesta
        finally:
            duracion = time.perf_counter() - inicio
            # La plantilla de ruta la fija el enrutador al resolver la
            # petición; si no casó con ninguna ruta, no se usa la URL cruda.
            plantilla = getattr(request.scope.get("route"), "path", "sin_ruta")

            PETICIONES.labels(request.method, plantilla, str(estado)).inc()
            DURACION.labels(request.method, plantilla).observe(duracion)
            if request.method == "GET" and plantilla == RUTA_TABLERO and estado == 200:
                TABLERO.observe(duracion)
                ESC01.observar(duracion)

            if estado >= 500:
                nivel = logging.ERROR
            elif plantilla in _RUTAS_DE_SONDEO and estado < 400:
                # Render consulta /health sin parar y el ping de mantenimiento
                # lo hace cada minuto: miles de líneas al día que no dicen nada.
                # Se siguen contando en las métricas; solo no se registran.
                nivel = logging.DEBUG
            else:
                nivel = logging.INFO
            registro_peticiones.log(
                nivel,
                "%s %s -> %s",
                request.method,
                plantilla,
                estado,
                extra={
                    "evento": "peticion",
                    "id_peticion": id_peticion,
                    "metodo": request.method,
                    "ruta": plantilla,
                    "estado": estado,
                    "duracion_ms": round(duracion * 1000, 2),
                },
            )
