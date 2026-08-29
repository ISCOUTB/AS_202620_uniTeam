"""Punto de entrada de la API de UniTeam.

Corresponde al contenedor «API» del C4 nivel 2. Compone las capas y traduce
los errores del dominio a códigos HTTP.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import rutas_progreso, rutas_proyectos, rutas_tareas
from app.config import ajustes
from app.domain.errores import (
    AccesoDenegado,
    RecursoNoEncontrado,
    TransicionInvalida,
    YaEsMiembro,
)
from app.infrastructure.db import crear_esquema

@asynccontextmanager
async def ciclo_de_vida(_: FastAPI):
    if ajustes.crear_esquema_al_arrancar:
        crear_esquema()
    yield


app = FastAPI(
    title="UniTeam API",
    description="Gestión colaborativa de tareas para equipos universitarios.",
    version="0.2.0",
    lifespan=ciclo_de_vida,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ajustes.origenes_permitidos,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
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
    return {"status": "ok"}


app.include_router(rutas_proyectos.router)
app.include_router(rutas_progreso.router)
app.include_router(rutas_tareas.router)
