"""Configuración de las pruebas.

Usa la base de datos que indique `DATABASE_URL` —en integración continua es
MySQL— y, si no hay ninguna, un SQLite temporal.

Para la autenticación levanta el emisor OIDC de desarrollo en un hilo. Las
pruebas son herméticas, pero la criptografía es real: los tokens se firman de
verdad y la API los verifica contra el JWKS del emisor, exactamente como hará
con el proveedor institucional.
"""
import os
import tempfile
import threading

if not os.getenv("DATABASE_URL"):
    _fichero = os.path.join(tempfile.mkdtemp(), "prueba.db")
    os.environ["DATABASE_URL"] = f"sqlite:///{_fichero}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from scripts import emisor_dev  # noqa: E402

AUDIENCIA = "uniteam-web"

_servidor = emisor_dev.servir(puerto=0)
_EMISOR = emisor_dev.Manejador.emisor
os.environ["OIDC_EMISOR"] = _EMISOR
os.environ["OIDC_AUDIENCIA"] = AUDIENCIA

from app.api import seguridad  # noqa: E402
from app.infrastructure.db import SesionLocal, crear_esquema, engine  # noqa: E402
from app.infrastructure.tablas import (  # noqa: E402
    AuditoriaTabla,
    MiembroTabla,
    ProyectoTabla,
    TareaTabla,
)
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def emisor():
    hilo = threading.Thread(target=_servidor.serve_forever, daemon=True)
    hilo.start()
    yield _EMISOR
    _servidor.shutdown()
    seguridad.reiniciar_cache()


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


def token_de(usuario: str, **extra) -> str:
    """Token firmado por el emisor de desarrollo para ese usuario."""
    return emisor_dev.firmar(_EMISOR, AUDIENCIA, usuario, **extra)


@pytest.fixture
def cab():
    """Cabeceras de autenticación para un usuario: `cab("ana")`."""

    def construir(usuario: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token_de(usuario)}"}

    return construir
