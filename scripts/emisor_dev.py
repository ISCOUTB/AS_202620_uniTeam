#!/usr/bin/env python3
"""Emisor OIDC mínimo, **solo para desarrollo y pruebas**.

UniTeam delega la autenticación en un proveedor de identidad externo (ADR
0005). Para trabajar en local sin depender de una cuenta de Google ni del
proveedor institucional, este módulo levanta un emisor que habla lo justo del
protocolo: descubrimiento, JWKS, autorización con PKCE y canje de código.

**No autentica a nadie.** Cualquiera puede pedir un token con el nombre que
quiera: su única función es firmar tokens verificables para que el resto del
sistema se ejercite tal como lo hará en producción. Nunca debe desplegarse
fuera de un entorno de desarrollo.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

CLAVE = rsa.generate_private_key(public_exponent=65537, key_size=2048)
KID = "emisor-dev"
CODIGOS: dict[str, dict] = {}


def _b64(valor: int) -> str:
    bruto = valor.to_bytes((valor.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(bruto).rstrip(b"=").decode()


def jwks() -> dict:
    numeros = CLAVE.public_key().public_numbers()
    return {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": KID,
                "n": _b64(numeros.n),
                "e": _b64(numeros.e),
            }
        ]
    }


def firmar(emisor: str, audiencia: str, usuario: str, minutos: int = 60) -> str:
    ahora = int(time.time())
    return jwt.encode(
        {
            "iss": emisor,
            "aud": audiencia,
            "sub": usuario,
            "email": usuario,
            "iat": ahora,
            "exp": ahora + minutos * 60,
        },
        CLAVE,
        algorithm="RS256",
        headers={"kid": KID},
    )


def _reto_valido(verificador: str, reto: str) -> bool:
    resumen = hashlib.sha256(verificador.encode()).digest()
    return base64.urlsafe_b64encode(resumen).rstrip(b"=").decode() == reto


class Manejador(BaseHTTPRequestHandler):
    emisor = "http://localhost:9000"

    def log_message(self, *_args):  # silencia el registro por petición
        pass

    def _responder(self, codigo: int, cuerpo: dict | str, tipo="application/json"):
        datos = (
            json.dumps(cuerpo).encode() if isinstance(cuerpo, dict) else cuerpo.encode()
        )
        self.send_response(codigo)
        self.send_header("Content-Type", tipo + "; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(datos)

    def do_OPTIONS(self):
        self._responder(204, "")

    def do_GET(self):
        ruta = urllib.parse.urlparse(self.path)
        parametros = dict(urllib.parse.parse_qsl(ruta.query))

        if ruta.path == "/.well-known/openid-configuration":
            return self._responder(200, {
                "issuer": self.emisor,
                "authorization_endpoint": f"{self.emisor}/authorize",
                "token_endpoint": f"{self.emisor}/token",
                "jwks_uri": f"{self.emisor}/jwks",
                "response_types_supported": ["code"],
                "subject_types_supported": ["public"],
                "id_token_signing_alg_values_supported": ["RS256"],
                "code_challenge_methods_supported": ["S256"],
            })

        if ruta.path == "/jwks":
            return self._responder(200, jwks())

        if ruta.path == "/authorize":
            # Formulario mínimo: quien inicia sesión escribe su nombre.
            return self._responder(200, f"""<!doctype html>
<html lang="es"><meta charset="utf-8"><title>Emisor de desarrollo</title>
<body style="font-family:system-ui;max-width:420px;margin:80px auto">
  <h1 style="font-size:20px">Emisor de desarrollo</h1>
  <p style="color:#666;font-size:14px">Sustituye al proveedor de identidad real.
  No comprueba contraseñas: firma un token con el nombre que indiques.</p>
  <form method="post" action="/authorize">
    <input type="hidden" name="redirect_uri" value="{parametros.get('redirect_uri','')}">
    <input type="hidden" name="state" value="{parametros.get('state','')}">
    <input type="hidden" name="code_challenge" value="{parametros.get('code_challenge','')}">
    <input type="hidden" name="client_id" value="{parametros.get('client_id','')}">
    <label style="display:block;margin-bottom:6px">Usuario</label>
    <input name="usuario" autofocus required style="padding:8px;width:100%">
    <button type="submit" style="margin-top:12px;padding:8px 16px">Entrar</button>
  </form>
</body></html>""", tipo="text/html")

        return self._responder(404, {"error": "not_found"})

    def do_POST(self):
        ruta = urllib.parse.urlparse(self.path)
        largo = int(self.headers.get("Content-Length", 0))
        cuerpo = dict(urllib.parse.parse_qsl(self.rfile.read(largo).decode()))

        if ruta.path == "/authorize":
            codigo = secrets.token_urlsafe(24)
            CODIGOS[codigo] = {
                "usuario": cuerpo.get("usuario", "anonimo"),
                "code_challenge": cuerpo.get("code_challenge", ""),
                "client_id": cuerpo.get("client_id", ""),
            }
            destino = cuerpo.get("redirect_uri", "")
            union = "&" if "?" in destino else "?"
            estado = urllib.parse.quote(cuerpo.get("state", ""))
            self.send_response(303)
            self.send_header("Location", f"{destino}{union}code={codigo}&state={estado}")
            self.end_headers()
            return

        if ruta.path == "/token":
            datos = CODIGOS.pop(cuerpo.get("code", ""), None)
            if datos is None:
                return self._responder(400, {"error": "invalid_grant"})
            if datos["code_challenge"] and not _reto_valido(
                cuerpo.get("code_verifier", ""), datos["code_challenge"]
            ):
                return self._responder(400, {"error": "invalid_grant"})
            token = firmar(self.emisor, datos["client_id"] or "uniteam-web", datos["usuario"])
            return self._responder(200, {
                "access_token": token,
                "id_token": token,
                "token_type": "Bearer",
                "expires_in": 3600,
            })

        return self._responder(404, {"error": "not_found"})


def servir(puerto: int = 9000, emisor: str | None = None) -> ThreadingHTTPServer:
    """Crea el servidor. Con `puerto=0` toma uno libre y ajusta el emisor."""
    servidor = ThreadingHTTPServer(("0.0.0.0", puerto), Manejador)
    real = servidor.server_address[1]
    Manejador.emisor = emisor or f"http://localhost:{real}"
    return servidor


if __name__ == "__main__":
    puerto = int(os.getenv("PUERTO", "9000"))
    emisor = os.getenv("EMISOR", f"http://localhost:{puerto}")
    print(f"Emisor OIDC de desarrollo en {emisor} — no usar en producción")
    servir(puerto, emisor).serve_forever()
