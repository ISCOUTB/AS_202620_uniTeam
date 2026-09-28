"""Punto de entrada de la API de UniTeam.

Corresponde al contenedor «API» del C4 nivel 2. Compone las capas y traduce
los errores del dominio a códigos HTTP.
"""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app import observabilidad
from app.api import rutas_progreso, rutas_proyectos, rutas_tareas
from app.config import ajustes
from app.domain.errores import (
    AccesoDenegado,
    RecursoNoEncontrado,
    TransicionInvalida,
    YaEsMiembro,
)
from app.infrastructure.db import crear_esquema, engine

observabilidad.configurar_registro()
registro = logging.getLogger("uniteam")


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI):
    if ajustes.crear_esquema_al_arrancar:
        crear_esquema()
    registro.info(
        "API en marcha",
        extra={"evento": "arranque", "revision": ajustes.revision, "entorno": ajustes.entorno},
    )
    yield


app = FastAPI(
    title="UniTeam API",
    description="Gestión colaborativa de tareas para equipos universitarios.",
    version="0.2.0",
    lifespan=ciclo_de_vida,
)


# Se añade antes que CORS para quedar por dentro: así mide también las
# peticiones que CORS deja pasar y no las preflight que resuelve él solo.
app.add_middleware(observabilidad.ObservarPeticiones)
# Un tablero de 200 tareas son 65 KB de JSON y 6,6 KB comprimido: el 90 % del
# ancho de banda de la API, que es lo que mide la capa gratuita
# (docs/despliegue/costos.md).
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ajustes.origenes_permitidos,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Request-ID"],
)


@app.exception_handler(AccesoDenegado)
def _acceso_denegado(request: Request, exc: AccesoDenegado) -> JSONResponse:
    # 403 sin cuerpo del recurso: no se confirma siquiera que exista (ESC-03).
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(RecursoNoEncontrado)
def _no_encontrado(request: Request, exc: RecursoNoEncontrado) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(YaEsMiembro)
def _ya_es_miembro(request: Request, exc: YaEsMiembro) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(TransicionInvalida)
def _transicion_invalida(request: Request, exc: TransicionInvalida) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.get("/", tags=["sistema"])
def raiz() -> dict:
    return {"message": "UniTeam API"}


@app.get("/activo", tags=["sistema"])
def activo() -> dict:
    """Vivacidad: el proceso responde. No toca la base de datos."""
    return {"status": "ok"}


@app.get("/health", tags=["sistema"])
def salud(respuesta: Response) -> dict:
    """Disponibilidad: el proceso responde **y** alcanza la base de datos.

    Es la ruta que consulta el proveedor de despliegue para decidir si una
    instancia recibe tráfico (render.yaml, `healthCheckPath`). Devuelve 503 si
    la base de datos no contesta, para que el proveedor no enrute peticiones a
    una API que no podría atenderlas.
    """
    inicio = time.perf_counter()
    try:
        with engine.connect() as conexion:
            conexion.execute(text("SELECT 1"))
        base_de_datos = "ok"
    except Exception:  # cualquier fallo de conexión es «no disponible»
        registro.exception("La base de datos no responde", extra={"evento": "salud"})
        base_de_datos = "caida"
        respuesta.status_code = 503

    return {
        "estado": "ok" if base_de_datos == "ok" else "degradado",
        "base_de_datos": base_de_datos,
        "latencia_bd_ms": round((time.perf_counter() - inicio) * 1000, 2),
        "version": app.version,
        "revision": ajustes.revision,
        "entorno": ajustes.entorno,
    }


@app.get("/metricas", tags=["sistema"], response_class=Response)
def metricas() -> Response:
    """Métricas en formato de exposición de Prometheus."""
    return observabilidad.exponer_metricas()


@app.get("/metricas/esc-01", tags=["sistema"])
def metrica_esc01() -> dict:
    """p95 y p99 del tablero en la ventana reciente, frente al umbral de ESC-01."""
    return observabilidad.ESC01.resumen()


app.include_router(rutas_proyectos.router)
app.include_router(rutas_progreso.router)
app.include_router(rutas_tareas.router)
