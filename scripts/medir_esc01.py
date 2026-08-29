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
import statistics
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

UMBRAL_P95 = 2.0
UMBRAL_P99 = 4.0


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
    for i in range(tareas):
        _peticion(
            f"{base}/proyectos/{proyecto['id']}/tareas",
            token,
            "POST",
            {"titulo": f"Tarea sintética {i:03d}", "prioridad": "media"},
        )
    return proyecto["id"]


def medir(base: str, token: str, proyecto: str, usuarios: int, por_usuario: int):
    """Cada usuario virtual consulta el tablero varias veces."""
    url = f"{base}/proyectos/{proyecto}/tareas?limite=200"
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
    ordenados = sorted(valores)
    indice = min(int(round(p / 100 * len(ordenados) + 0.5)) - 1, len(ordenados) - 1)
    return ordenados[max(indice, 0)]


def main() -> int:
    cli = argparse.ArgumentParser(description="Mide el escenario ESC-01.")
    cli.add_argument("--url", default="http://localhost:8000")
    cli.add_argument("--token", required=True, help="Token del proveedor de identidad")
    cli.add_argument("--tareas", type=int, default=200)
    cli.add_argument("--usuarios", type=int, default=30)
    cli.add_argument("--peticiones", type=int, default=10, help="por usuario virtual")
    cli.add_argument("--proyecto", help="Reutiliza un proyecto ya sembrado")
    argumentos = cli.parse_args()

    base = argumentos.url.rstrip("/")

    proyecto = argumentos.proyecto
    if proyecto is None:
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
