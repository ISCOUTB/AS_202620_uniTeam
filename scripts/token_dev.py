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


def obtener(emisor: str, usuario: str, cliente: str, redireccion: str) -> str:
    emisor = emisor.rstrip("/")
    with urllib.request.urlopen(f"{emisor}/.well-known/openid-configuration") as r:
        descubrimiento = json.load(r)

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

    class NoSeguir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *_args, **_kwargs):
            return None

    abridor = urllib.request.build_opener(NoSeguir)
    try:
        abridor.open(descubrimiento["authorization_endpoint"], data=cuerpo)
        raise SystemExit("El emisor no redirigió: no se obtuvo código.")
    except urllib.error.HTTPError as respuesta:
        destino = respuesta.headers.get("Location", "")

    parametros = urllib.parse.parse_qs(urllib.parse.urlparse(destino).query)
    codigo = parametros.get("code", [None])[0]
    if not codigo:
        raise SystemExit(f"No hay código en la redirección: {destino}")

    canje = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": codigo,
        "redirect_uri": redireccion,
        "client_id": cliente,
        "code_verifier": verificador,
    }).encode()
    with urllib.request.urlopen(descubrimiento["token_endpoint"], data=canje) as r:
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
