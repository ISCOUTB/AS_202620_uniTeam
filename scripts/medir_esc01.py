#!/usr/bin/env python3
"""Mide ESC-01: latencia de consulta del tablero.

Reproduce el escenario tal como está escrito: un proyecto con 200 tareas y 30
usuarios concurrentes consultando el tablero, y contrasta el resultado con el
umbral —p95 ≤ 2 s, p99 ≤ 4 s y 0 errores en 100 solicitudes consecutivas—.

Uso:

    python scripts/medir_esc01.py --url http://localhost:8000 --token "$TOKEN"

Sale con código 1 si no se cumple el umbral, para poder encadenarlo.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

UMBRAL_P95 = 2.0
UMBRAL_P99 = 4.0


# Servidores a los que el script puede apuntar: la API local y la desplegada.
# Es un instrumento de medición de UniTeam y no tiene por qué hablar con nada más.
HOSTS_PERMITIDOS = ("localhost", "127.0.0.1", "::1", "uniteam-api.onrender.com")


def _base_http(url: str) -> str:
    """Devuelve la URL base de la API, reconstruida a partir de valores conocidos.

    `urlopen` habla con cualquier servidor, y también `file://` y `ftp://`. La
    URL la escribe quien ejecuta el script, pero el resultado se reconstruye
    desde las constantes de este módulo —esquema y host de una lista cerrada,
    puerto como entero— para que una errata no apunte la medición, y el token
    que la acompaña, a otro sitio.
    """
    partes = urllib.parse.urlsplit(url.strip())
    esquema = next((e for e in ("http", "https") if e == partes.scheme.lower()), None)
    if esquema is None:
        raise SystemExit(f"La URL debe ser http o https: {url}")
    host = next((h for h in HOSTS_PERMITIDOS if h == partes.hostname), None)
    if host is None:
        raise SystemExit(
            f"Host no permitido: {partes.hostname}. Se admite: {', '.join(HOSTS_PERMITIDOS)}"
        )
    if partes.path.strip("/") or partes.query or partes.fragment or partes.username:
        raise SystemExit(f"La URL debe ser solo la base de la API, sin ruta ni credenciales: {url}")
    try:
        puerto = partes.port
    except ValueError:
        raise SystemExit(f"Puerto no válido: {url}") from None
    anfitrion = f"[{host}]" if ":" in host else host
    return f"{esquema}://{anfitrion}" + (f":{int(puerto)}" if puerto else "")


def _id_de_proyecto(valor: object) -> str:
    """Un identificador de proyecto es un UUID; cualquier otra cosa no entra en la ruta.

    Sin esta comprobación, un `--proyecto` como `../../otra-ruta` —o una
    respuesta inesperada de la API— cambiaría el recurso consultado.
    """
    try:
        canonico = str(uuid.UUID(str(valor)))
    except ValueError:
        raise SystemExit(f"Identificador de proyecto no válido: {valor!r}") from None
    return urllib.parse.quote(canonico, safe="")


def _peticion(url: str, token: str, metodo: str = "GET", cuerpo: dict | None = None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    peticion = urllib.request.Request(url, data=datos, method=metodo)
    peticion.add_header("Authorization", f"Bearer {token}")
    peticion.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        return json.load(respuesta)


def preparar(base: str, token: str, tareas: int) -> str:
    """Crea un proyecto con el número de tareas del escenario."""
    proyecto = _peticion(
        f"{base}/proyectos",
        token,
        "POST",
        {"nombre": f"Medición ESC-01 {datetime.now():%Y-%m-%d %H:%M}", "miembros": []},
    )
    id_proyecto = _id_de_proyecto(proyecto["id"])
    for i in range(tareas):
        _peticion(
            f"{base}/proyectos/{id_proyecto}/tareas",
            token,
            "POST",
            {"titulo": f"Tarea sintética {i:03d}", "prioridad": "media"},
        )
    return id_proyecto


def medir(base: str, token: str, proyecto: str, usuarios: int, por_usuario: int):
    """Cada usuario virtual consulta el tablero varias veces."""
    url = f"{base}/proyectos/{_id_de_proyecto(proyecto)}/tareas?limite=200"
    latencias: list[float] = []
    errores = 0

    def usuario_virtual(_n: int):
        propias, fallos = [], 0
        for _ in range(por_usuario):
            inicio = time.perf_counter()
            try:
                _peticion(url, token)
                propias.append(time.perf_counter() - inicio)
            except (urllib.error.URLError, TimeoutError, OSError):
                fallos += 1
        return propias, fallos

    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=usuarios) as pool:
        for propias, fallos in pool.map(usuario_virtual, range(usuarios)):
            latencias.extend(propias)
            errores += fallos
    duracion = time.perf_counter() - inicio

    return latencias, errores, duracion


def percentil(valores: list[float], p: float) -> float:
    if not valores:
        return float("nan")
    # Rango más cercano. La versión anterior usaba round(x + 0.5), que con el
    # redondeo al par de Python caía un rango por encima: sobrestimaba el
    # percentil, en el sentido conservador.
    ordenados = sorted(valores)
    indice = math.ceil(p / 100 * len(ordenados)) - 1
    return ordenados[min(max(indice, 0), len(ordenados) - 1)]


def main() -> int:
    cli = argparse.ArgumentParser(description="Mide el escenario ESC-01.")
    cli.add_argument(
        "--url",
        default="http://localhost:8000",
        help=f"Base de la API; host entre: {', '.join(HOSTS_PERMITIDOS)}",
    )
    cli.add_argument("--token", required=True, help="Token del proveedor de identidad")
    cli.add_argument("--tareas", type=int, default=200)
    cli.add_argument("--usuarios", type=int, default=30)
    cli.add_argument("--peticiones", type=int, default=10, help="por usuario virtual")
    cli.add_argument("--proyecto", help="Reutiliza un proyecto ya sembrado")
    argumentos = cli.parse_args()

    base = _base_http(argumentos.url)

    proyecto = argumentos.proyecto
    if proyecto is not None:
        proyecto = _id_de_proyecto(proyecto)
    else:
        print(f"Sembrando {argumentos.tareas} tareas…", flush=True)
        proyecto = preparar(base, argumentos.token, argumentos.tareas)

    print(
        f"Midiendo: {argumentos.usuarios} usuarios × {argumentos.peticiones} "
        f"peticiones sobre el proyecto {proyecto}",
        flush=True,
    )
    latencias, errores, duracion = medir(
        base, argumentos.token, proyecto, argumentos.usuarios, argumentos.peticiones
    )

    total = len(latencias) + errores
    p95, p99 = percentil(latencias, 95), percentil(latencias, 99)
    cumple = p95 <= UMBRAL_P95 and p99 <= UMBRAL_P99 and errores == 0

    print(f"""
Escenario   ESC-01 — latencia de consulta del tablero
Momento     {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} UTC
Carga       {argumentos.tareas} tareas · {argumentos.usuarios} usuarios concurrentes
Solicitudes {total} ({errores} con error)
Duración    {duracion:.2f} s · {total / duracion:.1f} solicitudes/s

  mediana   {statistics.median(latencias) * 1000:7.1f} ms
  p95       {p95 * 1000:7.1f} ms   (umbral {UMBRAL_P95 * 1000:.0f} ms)
  p99       {p99 * 1000:7.1f} ms   (umbral {UMBRAL_P99 * 1000:.0f} ms)
  máximo    {max(latencias) * 1000:7.1f} ms

Resultado   {'CUMPLE' if cumple else 'NO CUMPLE'} el umbral de ESC-01
""")
    return 0 if cumple else 1


if __name__ == "__main__":
    sys.exit(main())
