#!/usr/bin/env python3
"""Comprueba los enlaces internos de la documentación.

El contrato del curso trata una celda que no lleva a ninguna parte como un
hueco, así que esto se ejecuta en integración continua. Detecta dos cosas:

1. Enlaces relativos cuyo destino no existe.
2. Markdown malformado del tipo `[archivo.md)`, que el navegador muestra como
   texto plano y que un verificador ingenuo no ve, porque no es un enlace.
"""
import re
import sys
import urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENLACE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
MALFORMADO = re.compile(r"\[[^\]\n]*\.md\)")
EXCLUIDOS = {".venv", ".git", "node_modules"}


def documentos():
    for ruta in RAIZ.rglob("*.md"):
        if not EXCLUIDOS & set(ruta.relative_to(RAIZ).parts):
            yield ruta


def problemas_documento(ruta: Path) -> list[str]:
    texto = ruta.read_text(encoding="utf-8")
    rel = ruta.relative_to(RAIZ)
    problemas = []

    for m in ENLACE.finditer(texto):
        destino = m.group(1).strip("<>")
        if destino.startswith(("http", "mailto", "#")):
            continue
        camino = urllib.parse.unquote(destino.split("#")[0])
        if camino and not (ruta.parent / camino).resolve().exists():
            problemas.append(f"{rel}: destino inexistente -> {destino}")

    for m in MALFORMADO.finditer(texto):
        if "](" not in m.group(0):
            problemas.append(f"{rel}: enlace malformado -> {m.group(0)}")

    return problemas


def main() -> int:
    problemas = []
    for ruta in documentos():
        problemas.extend(problemas_documento(ruta))

    if problemas:
        print(f"{len(problemas)} problema(s) de enlaces:\n")
        for p in problemas:
            print(" ", p)
        return 1

    print("Enlaces de la documentación: correctos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
