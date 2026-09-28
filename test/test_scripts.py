"""Validación de entradas de las herramientas de `scripts/`.

Hallazgos S8703 (SSRF) y S7044 (recorrido de la ruta de la API) de SonarCloud
sobre `scripts/medir_esc01.py`: ver docs/calidad/analisis-estatico.md.
Ninguna prueba abre conexiones.
"""
import pytest

from scripts import medir_esc01

ID = "0b7e8c1e-4f5a-4c1d-9a55-2d3c1f0e9b7a"


# -- URL base -----------------------------------------------------------------


@pytest.mark.parametrize(
    "url, esperada",
    [
        ("http://localhost:8000", "http://localhost:8000"),
        ("http://localhost:8000/", "http://localhost:8000"),
        ("  HTTP://LocalHost:8001  ", "http://localhost:8001"),
        ("http://127.0.0.1:8000", "http://127.0.0.1:8000"),
        ("http://[::1]:8000", "http://[::1]:8000"),
        ("https://uniteam-api.onrender.com", "https://uniteam-api.onrender.com"),
    ],
)
def test_la_url_de_la_api_se_acepta_y_se_normaliza(url, esperada):
    assert medir_esc01._base_http(url) == esperada


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://localhost/",
        "http://169.254.169.254",  # metadatos de la nube
        "https://ejemplo.com",
        "https://uniteam-api.onrender.com.ejemplo.com",
        "http://localhost@ejemplo.com",
        "http://usuario:clave@localhost:8000",
        "http://localhost:8000/proyectos",
        "http://localhost:8000?x=1",
        "http://localhost:puerto",
        "http://localhost:99999",
    ],
)
def test_una_url_fuera_de_la_lista_se_rechaza(url):
    with pytest.raises(SystemExit):
        medir_esc01._base_http(url)


# -- Identificador de proyecto -------------------------------------------------


def test_un_uuid_entra_en_la_ruta_en_forma_canonica():
    assert medir_esc01._id_de_proyecto(ID) == ID
    assert medir_esc01._id_de_proyecto(ID.upper()) == ID
    assert medir_esc01._id_de_proyecto("{" + ID + "}") == ID


@pytest.mark.parametrize(
    "valor",
    ["../../metricas", f"{ID}/../../otro", f"{ID}?limite=1", "%2e%2e", "", None, 7],
)
def test_un_identificador_que_no_es_uuid_se_rechaza(valor):
    with pytest.raises(SystemExit):
        medir_esc01._id_de_proyecto(valor)


def test_la_medicion_valida_el_proyecto_antes_de_la_primera_peticion(monkeypatch):
    llamadas = []
    monkeypatch.setattr(medir_esc01, "_peticion", lambda *a, **k: llamadas.append(a))
    with pytest.raises(SystemExit):
        medir_esc01.medir("http://localhost:8000", "t", "../metricas", usuarios=1, por_usuario=1)
    assert llamadas == []


def test_la_siembra_valida_el_id_que_devuelve_la_api(monkeypatch):
    urls = []

    def falsa(url, *_a, **_k):
        urls.append(url)
        return {"id": "../../metricas"} if url.endswith("/proyectos") else {}

    monkeypatch.setattr(medir_esc01, "_peticion", falsa)
    with pytest.raises(SystemExit):
        medir_esc01.preparar("http://localhost:8000", "t", tareas=2)
    assert urls == ["http://localhost:8000/proyectos"]
