"""Autenticación mediante OpenID Connect.

La API **no autentica usuarios**: valida el token que emite el proveedor de
identidad y extrae de él la identidad. Es la relación «API → Proveedor de
identidad» del C4 nivel 2, y la decisión está en el ADR 0005.

La verificación es completa: firma contra el JWKS del emisor, emisor
esperado, audiencia esperada y caducidad. Un token que falle cualquiera de
esas comprobaciones se rechaza con 401.
"""
from __future__ import annotations

import json
import threading
import urllib.request
from typing import Optional

import jwt
from fastapi import Header, HTTPException, status
from jwt import PyJWKClient

from app.config import ajustes

_ALGORITMOS = ["RS256"]
_candado = threading.Lock()
_clientes: dict[str, PyJWKClient] = {}


class ConfiguracionInvalida(RuntimeError):
    """Falta configuración obligatoria del proveedor de identidad."""


def _descubrir_jwks(emisor: str) -> str:
    """Obtiene `jwks_uri` del documento de descubrimiento del emisor."""
    url = f"{emisor}/.well-known/openid-configuration"
    with urllib.request.urlopen(url, timeout=10) as respuesta:
        documento = json.load(respuesta)
    jwks_uri = documento.get("jwks_uri")
    if not jwks_uri:
        raise ConfiguracionInvalida(
            f"El emisor {emisor} no publica 'jwks_uri' en su descubrimiento."
        )
    return jwks_uri


def _cliente_jwks() -> PyJWKClient:
    """Cliente de claves del emisor, cacheado entre peticiones."""
    if not ajustes.oidc_configurado:
        raise ConfiguracionInvalida(
            "Faltan OIDC_EMISOR y OIDC_AUDIENCIA: la API no puede autenticar."
        )

    emisor = ajustes.oidc_emisor
    with _candado:
        cliente = _clientes.get(emisor)
        if cliente is None:
            url = ajustes.oidc_jwks_url or _descubrir_jwks(emisor)
            # PyJWKClient cachea las claves y sabe recargarlas si aparece un
            # 'kid' desconocido, que es lo que ocurre cuando el emisor rota.
            cliente = PyJWKClient(url, cache_keys=True, lifespan=600)
            _clientes[emisor] = cliente
        return cliente


def reiniciar_cache() -> None:
    """Olvida las claves cacheadas. Lo usan las pruebas entre emisores."""
    with _candado:
        _clientes.clear()


def identidad_del_token(token: str) -> str:
    """Verifica el token y devuelve la identidad del usuario."""
    try:
        clave = _cliente_jwks().get_signing_key_from_jwt(token).key
        contenido = jwt.decode(
            token,
            clave,
            algorithms=_ALGORITMOS,
            audience=ajustes.oidc_audiencia,
            issuer=ajustes.oidc_emisor,
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
    except ConfiguracionInvalida:
        raise
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {error}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    usuario = contenido.get(ajustes.oidc_claim_usuario) or contenido.get("sub")
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token no identifica a ningún usuario.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return str(usuario)


def usuario_actual(authorization: Optional[str] = Header(default=None)) -> str:
    """Identidad del usuario que hace la petición.

    Sustituye a la cabecera `X-Usuario` que se usó como andamiaje hasta la
    integración del proveedor de identidad.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta la credencial: se espera 'Authorization: Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return identidad_del_token(authorization.split(" ", 1)[1].strip())
