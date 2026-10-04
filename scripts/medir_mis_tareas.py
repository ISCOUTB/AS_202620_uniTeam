"""Mide la latencia de `GET /mis-tareas` en proceso, sobre la base que indique DATABASE_URL.

Escenario asociado: ESC-01 (rendimiento con 200 tareas). Siembra un usuario con
200 tareas asignadas repartidas en 20 proyectos y mide N peticiones seguidas.
Es una medición **comparativa** del código (antes/después de un cambio), no la
medición de ESC-01 de extremo a extremo que hace `medir_esc01.py`.

Uso:  python -m scripts.medir_mis_tareas [--peticiones 300]
"""
import argparse
import math
import os
import statistics
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone

if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(tempfile.mkdtemp(), 'medir.db')}"

from scripts import emisor_dev  # noqa: E402

_servidor = emisor_dev.servir(puerto=0)
_EMISOR = emisor_dev.Manejador.emisor
os.environ["OIDC_EMISOR"] = _EMISOR
os.environ["OIDC_AUDIENCIA"] = "uniteam-web"
threading.Thread(target=_servidor.serve_forever, daemon=True).start()

from fastapi.testclient import TestClient  # noqa: E402

from app.infrastructure.db import SesionLocal, crear_esquema, engine  # noqa: E402
from app.infrastructure.tablas import MiembroTabla, ProyectoTabla, TareaTabla  # noqa: E402
from app.main import app  # noqa: E402


def sembrar(usuario: str, proyectos: int = 20, por_proyecto: int = 10) -> None:
    crear_esquema(engine)
    with SesionLocal() as s:
        for i in range(proyectos):
            pid = str(uuid.uuid4())
            s.add(ProyectoTabla(id=pid, nombre=f"Proyecto {i:02d}"))
            s.add(MiembroTabla(proyecto_id=pid, usuario=usuario, rol="integrante"))
            s.add(MiembroTabla(proyecto_id=pid, usuario="otra@utb.edu.co", rol="lider"))
            for j in range(por_proyecto):
                s.add(TareaTabla(
                    id=str(uuid.uuid4()), proyecto_id=pid, titulo=f"T{i}-{j}", creada_por="otra@utb.edu.co",
                    prioridad="media", estado="pendiente", responsable=usuario,
                    creada_en=datetime.now(timezone.utc),
                ))
        s.commit()


def percentil(valores: list[float], p: float) -> float:
    ordenados = sorted(valores)
    rango = max(1, math.ceil(round(p * len(ordenados), 9)))  # rango más cercano
    return ordenados[min(rango, len(ordenados)) - 1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--peticiones", type=int, default=300)
    n = ap.parse_args().peticiones
    usuario = "bruno@utb.edu.co"
    sembrar(usuario)
    cab = {"Authorization": f"Bearer {emisor_dev.firmar(_EMISOR, 'uniteam-web', usuario)}"}
    with TestClient(app) as c:
        for _ in range(10):  # calentamiento
            c.get("/mis-tareas", headers=cab)
        tiempos = []
        for _ in range(n):
            t0 = time.perf_counter()
            r = c.get("/mis-tareas", headers=cab)
            tiempos.append((time.perf_counter() - t0) * 1000)
            assert r.status_code == 200 and len(r.json()) == 200
    print(f"BD: {os.environ['DATABASE_URL'].split(':')[0]} | n={n} | tareas devueltas=200")
    print(f"mediana={statistics.median(tiempos):.1f} ms  p95={percentil(tiempos, .95):.1f} ms  "
          f"p99={percentil(tiempos, .99):.1f} ms  max={max(tiempos):.1f} ms")


if __name__ == "__main__":
    main()
