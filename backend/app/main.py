"""
InnovaActivos API – Punto de entrada principal.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Importar todos los modelos para que SQLAlchemy los registre
from app.models import *  # noqa: F401, F403

from app.routers import (
    auth,
    departamentos,
    usuarios,
    ubicaciones,
    categorias,
    activos,
    documentos,
    traslados,
    movimientos,
    inventario,
    sincronizacion,
    notificaciones,
    reportes,
    integraciones,
    mantenimiento,
    predicciones,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "API REST para la gestión integral de activos fijos de InnovaActivos. "
        "Cubre autenticación JWT, CRUD de activos, traslados, inventario físico, "
        "sincronización offline, mantenimiento, reportes y predicciones IA."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ─── CORS ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Registrar routers ───
app.include_router(auth.router)
app.include_router(departamentos.router)
app.include_router(usuarios.router)
app.include_router(ubicaciones.router)
app.include_router(categorias.router)
app.include_router(activos.router)
app.include_router(documentos.router)
app.include_router(traslados.router)
app.include_router(movimientos.router)
app.include_router(inventario.router)
app.include_router(sincronizacion.router)
app.include_router(notificaciones.router)
app.include_router(reportes.router)
app.include_router(integraciones.router)
app.include_router(mantenimiento.router)
app.include_router(predicciones.router)


@app.get("/", tags=["Health"])
def health_check():
    """Verificación de salud del servicio."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health", tags=["Health"])
def health():
    """Endpoint de health check para monitoreo."""
    return {"status": "healthy"}
