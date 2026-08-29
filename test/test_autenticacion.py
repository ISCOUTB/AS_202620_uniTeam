"""Autenticación con OpenID Connect (ADR 0005).

Comprueban que la API rechaza lo que debe rechazar. Autenticar no es
autorizar: estas pruebas cubren la puerta de entrada, y las de ESC-03 cubren
lo que ocurre una vez dentro.
"""
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from scripts import emisor_dev
from test.conftest import AUDIENCIA, token_de


def _proyecto(cliente, cab):
    return cliente.post(
        "/proyectos",
        json={"nombre": "Arquitectura", "miembros": []},
        headers=cab("ana"),
    )


def test_sin_credencial_la_api_responde_401(cliente):
    respuesta = cliente.get("/proyectos")
    assert respuesta.status_code == 401
    assert respuesta.headers.get("WWW-Authenticate") == "Bearer"


def test_un_esquema_distinto_de_bearer_se_rechaza(cliente):
    respuesta = cliente.get("/proyectos", headers={"Authorization": "Basic YWJjOjEyMw=="})
    assert respuesta.status_code == 401


def test_un_token_con_firma_ajena_se_rechaza(cliente, emisor):
    """Firmado con otra clave: el JWKS del emisor no lo valida."""
    otra = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ahora = int(time.time())
    falso = jwt.encode(
        {
            "iss": emisor,
            "aud": AUDIENCIA,
            "sub": "intruso",
            "email": "intruso",
            "iat": ahora,
            "exp": ahora + 600,
        },
        otra,
        algorithm="RS256",
        headers={"kid": emisor_dev.KID},
    )
    respuesta = cliente.get("/proyectos", headers={"Authorization": f"Bearer {falso}"})
    assert respuesta.status_code == 401


def test_un_token_caducado_se_rechaza(cliente):
    caducado = token_de("ana", minutos=-10)
    respuesta = cliente.get("/proyectos", headers={"Authorization": f"Bearer {caducado}"})
    assert respuesta.status_code == 401
    assert "expired" in respuesta.json()["detail"].lower()


def test_un_token_para_otra_audiencia_se_rechaza(cliente, emisor):
    """Un token válido de otra aplicación no sirve para entrar en esta."""
    ajeno = emisor_dev.firmar(emisor, "otra-aplicacion", "ana")
    respuesta = cliente.get("/proyectos", headers={"Authorization": f"Bearer {ajeno}"})
    assert respuesta.status_code == 401


def test_un_token_de_otro_emisor_se_rechaza(cliente):
    ajeno = emisor_dev.firmar("https://emisor-que-no-es", AUDIENCIA, "ana")
    respuesta = cliente.get("/proyectos", headers={"Authorization": f"Bearer {ajeno}"})
    assert respuesta.status_code == 401


def test_la_identidad_sale_del_token_no_de_lo_que_diga_el_cliente(cliente, cab):
    """El usuario ya no es un dato que el cliente pueda elegir."""
    creado = _proyecto(cliente, cab)
    assert creado.status_code == 201

    # El proyecto pertenece a quien firma el token, no a quien lo pida.
    de_ana = cliente.get("/proyectos", headers=cab("ana")).json()
    de_otro = cliente.get("/proyectos", headers=cab("bruno")).json()
    assert len(de_ana) == 1
    assert de_otro == []


@pytest.mark.parametrize("cabecera", ["Bearer", "Bearer ", "Bearer no-es-un-jwt"])
def test_credenciales_malformadas_se_rechazan(cliente, cabecera):
    respuesta = cliente.get("/proyectos", headers={"Authorization": cabecera})
    assert respuesta.status_code == 401
