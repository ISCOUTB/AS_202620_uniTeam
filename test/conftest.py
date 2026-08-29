"""Configuración de las pruebas.

Usa la base de datos que indique `DATABASE_URL` —en integración continua es
MySQL— y, si no hay ninguna, un SQLite temporal para que `pytest` funcione
recién clonado el repositorio.
"""
import os
import tempfile

if not os.getenv("DATABASE_URL"):
    _fichero = os.path.join(tempfile.mkdtemp(), "prueba.db")
    os.environ["DATABASE_URL"] = f"sqlite:///{_fichero}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.infrastructure.db import SesionLocal, crear_esquema, engine  # noqa: E402
from app.infrastructure.tablas import (  # noqa: E402
    AuditoriaTabla,
    MiembroTabla,
    ProyectoTabla,
    TareaTabla,
)
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def esquema():
    crear_esquema(engine)
    yield


@pytest.fixture(autouse=True)
def base_limpia(esquema):
    with SesionLocal() as sesion:
        for tabla in (AuditoriaTabla, TareaTabla, MiembroTabla, ProyectoTabla):
            sesion.query(tabla).delete()
        sesion.commit()
    yield


@pytest.fixture
def cliente():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sesion():
    with SesionLocal() as s:
        yield s
