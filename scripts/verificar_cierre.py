#!/usr/bin/env python3
"""Comprueba que `requirements.lock.txt` corresponde a `requirements.txt`.

Cada dependencia directa de `requirements.txt` debe aparecer en el cierre con
la misma versión fijada. El resto de la corrección del cierre la garantiza pip
al instalar con `--require-hashes`: en ese modo rechaza cualquier dependencia
transitiva que no esté fijada y con huella en el archivo.

Sustituye a la comprobación anterior, que recompilaba el cierre contra PyPI y
lo comparaba línea a línea. Esa comprobación no era determinista: bastaba con
que una dependencia transitiva publicara una versión nueva —greenlet 3.5.6,
en septiembre de 2026— para que la CI se pusiera roja sin que el repositorio
hubiera cambiado.

Uso:  python scripts/verificar_cierre.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PIN = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]*\])?==([^\s\;]+)")


def _normalizar(nombre: str) -> str:
    """Nombre canónico según PEP 503: `PyJWT` y `pyjwt` son el mismo paquete."""
    return re.sub(r"[-_.]+", "-", nombre).lower()


def _pines(ruta: Path) -> dict[str, str]:
    pines = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        coincidencia = PIN.match(linea.strip())
        if coincidencia:
            pines[_normalizar(coincidencia.group(1))] = coincidencia.group(2)
    return pines


def main() -> int:
    directas = _pines(RAIZ / "requirements.txt")
    cierre = _pines(RAIZ / "requirements.lock.txt")

    problemas = []
    for nombre, version in sorted(directas.items()):
        if nombre not in cierre:
            problemas.append(f"{nombre}=={version} no está en requirements.lock.txt")
        elif cierre[nombre] != version:
            problemas.append(
                f"{nombre}: requirements.txt fija {version}, el cierre fija {cierre[nombre]}"
            )

    if problemas:
        print("El cierre de dependencias no corresponde a requirements.txt:\n")
        for problema in problemas:
            print(f"  - {problema}")
        print(
            "\nRegenéralo con Python 3.11:\n"
            "  pip-compile --generate-hashes --strip-extras "
            "--output-file=requirements.lock.txt requirements.txt"
        )
        return 1

    print(f"Cierre de dependencias: {len(directas)} directas, {len(cierre)} en total, al día.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
