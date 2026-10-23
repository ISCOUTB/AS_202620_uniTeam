#!/usr/bin/env python3
"""Obtiene un token del emisor de desarrollo, para usar la API con curl.

Ejecuta el mismo flujo que la aplicación web —código de autorización con
PKCE—, de modo que el token es indistinguible del que obtiene el navegador.

    TOKEN=$(python scripts/token_dev.py ana@utb.edu.co)
    curl localhost:8000/proyectos -H "Authorization: Bearer $TOKEN"

Solo sirve contra el emisor de desarrollo. Con el proveedor real, el token se
obtiene iniciando sesión en la aplicación web.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import secrets
import sys
import urllib.parse
import urllib.request


def _b64(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode()


def _base_http(url: str) -> str:
    """Normaliza la URL base y la acepta solo si es HTTP o HTTPS.

    `urlopen` también habla `file://` y `ftp://`. La URL la escribe quien
    ejecuta el script, no un usuario del sistema, pero comprobar el esquema
    cuesta tres líneas y evita que una errata se convierta en una lectura de
    disco.
    """
    partes = urllib.parse.urlsplit(url)
    if partes.scheme.lower() not in ("http", "https") or not partes.netloc:
        raise SystemExit(f"La URL debe ser http o https: {url}")
    if partes.username or partes.password or partes.query or partes.fragment:
        raise SystemExit("La URL del emisor no puede incluir credenciales, consulta ni fragmento.")
    return url.rstrip("/")


def _validar_endpoint(url: str, emisor: str, nombre: str) -> str:
    """Acepta endpoints OIDC solo en el mismo origen del emisor configurado."""
    partes = urllib.parse.urlsplit(url)
    base = urllib.parse.urlsplit(emisor)
    origen = (partes.scheme.lower(), partes.hostname, partes.port)
    origen_base = (base.scheme.lower(), base.hostname, base.port)
    if (origen != origen_base or not partes.netloc or partes.username
            or partes.password or partes.query or partes.fragment):
        raise SystemExit(f"El {nombre} debe pertenecer al mismo origen que el emisor.")
    return url


def obtener(emisor: str, usuario: str, cliente: str, redireccion: str) -> str:
    emisor = _base_http(emisor)
    class NoSeguir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *_args, **_kwargs):
            return None

    abridor = urllib.request.build_opener(NoSeguir)
    with abridor.open(f"{emisor}/.well-known/openid-configuration", timeout=10) as r:
        descubrimiento = json.load(r)
    try:
        endpoint_autorizacion = _validar_endpoint(
            descubrimiento["authorization_endpoint"], emisor, "authorization_endpoint"
        )
        endpoint_token = _validar_endpoint(
            descubrimiento["token_endpoint"], emisor, "token_endpoint"
        )
    except (KeyError, TypeError) as error:
        raise SystemExit("El descubrimiento OIDC no contiene endpoints válidos.") from error

    verificador = _b64(secrets.token_bytes(32))
    reto = _b64(hashlib.sha256(verificador.encode()).digest())
    estado = _b64(secrets.token_bytes(16))

    # El emisor de desarrollo responde al formulario con una redirección 303
    # que lleva el código; no la seguimos, solo la leemos.
    cuerpo = urllib.parse.urlencode({
        "usuario": usuario,
        "redirect_uri": redireccion,
        "state": estado,
        "code_challenge": reto,
        "client_id": cliente,
    }).encode()

    try:
        abridor.open(endpoint_autorizacion, data=cuerpo, timeout=10)
        raise SystemExit("El emisor no redirigió: no se obtuvo código.")
    except urllib.error.HTTPError as respuesta:
        destino = respuesta.headers.get("Location", "")

    parametros = urllib.parse.parse_qs(urllib.parse.urlparse(destino).query)
    codigo = parametros.get("code", [None])[0]
    if not codigo:
        raise SystemExit("El emisor no devolvió un código de autorización válido.")

    canje = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": codigo,
        "redirect_uri": redireccion,
        "client_id": cliente,
        "code_verifier": verificador,
    }).encode()
    with abridor.open(endpoint_token, data=canje, timeout=10) as r:
        return json.load(r)["access_token"]


def main() -> int:
    cli = argparse.ArgumentParser(description="Token del emisor de desarrollo.")
    cli.add_argument("usuario", help="Identidad que llevará el token")
    cli.add_argument("--emisor", default="http://localhost:9000")
    cli.add_argument("--cliente", default="uniteam-web")
    cli.add_argument("--redireccion", default="http://localhost:3000/callback")
    argumentos = cli.parse_args()
    print(obtener(argumentos.emisor, argumentos.usuario, argumentos.cliente,
                  argumentos.redireccion))
    return 0


if __name__ == "__main__":
    sys.exit(main())
