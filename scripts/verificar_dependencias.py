"""Comprueba que cada dependencia directa exista en su registro y sea la legítima.

Una dependencia sugerida por un modelo puede no existir, o existir como un
paquete homónimo malicioso («slopsquatting»). Para cada una se consulta el
registro y se muestran los datos con que un humano decide: versión fijada
existente, repositorio de origen y fecha de publicación. Sale con código 1 si
alguna no existe o no tiene versión fijada publicada.

Uso:  python -m scripts.verificar_dependencias
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _json(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=20) as r:  # nosec: URL fija, esquema https
            return json.load(r)
    except Exception:
        return None


def pypi() -> list[tuple]:
    filas = []
    for linea in (RAIZ / "requirements.txt").read_text().splitlines():
        m = re.match(r"^([A-Za-z0-9_.\-]+)(\[[^\]]*\])?==([^\s#]+)", linea.strip())
        if not m:
            continue
        nombre, version = m.group(1), m.group(3)
        d = _json(f"https://pypi.org/pypi/{nombre}/{version}/json")
        if d is None:
            filas.append(("PyPI", nombre, version, "NO EXISTE", "", ""))
            continue
        urls = d["info"].get("project_urls") or {}
        origen = next((v for v in urls.values() if "github.com" in v or "gitlab.com" in v), d["info"].get("home_page") or "—")
        subida = d["urls"][0]["upload_time"][:10] if d["urls"] else "—"
        filas.append(("PyPI", nombre, version, "ok", origen, subida))
    return filas


def npm() -> list[tuple]:
    ruta = RAIZ / "web" / "package.json"
    if not ruta.exists():
        return []
    paquete = json.loads(ruta.read_text())
    filas = []
    for seccion in ("dependencies", "devDependencies"):
        for nombre, rango in paquete.get(seccion, {}).items():
            d = _json(f"https://registry.npmjs.org/{nombre}")
            if d is None:
                filas.append(("npm", nombre, rango, "NO EXISTE", "", ""))
                continue
            repo = d.get("repository") or {}
            origen = repo.get("url", "—") if isinstance(repo, dict) else str(repo)
            tiempos = d.get("time", {})
            fecha = tiempos.get(rango) or tiempos.get(d.get("dist-tags", {}).get("latest", ""), "")
            filas.append(("npm", nombre, rango, "ok", origen, fecha[:10]))
    return filas


def main() -> int:
    filas = pypi() + npm()
    print(f"{'registro':<6} {'paquete':<22} {'versión':<10} {'estado':<10} {'origen':<55} publicado")
    for f in filas:
        print(f"{f[0]:<6} {f[1]:<22} {f[2]:<10} {f[3]:<10} {f[4][:54]:<55} {f[5]}")
    faltan = [f for f in filas if f[3] != "ok"]
    print(f"\n{len(filas)} dependencias directas, {len(faltan)} sin verificar.")
    return 1 if faltan else 0


if __name__ == "__main__":
    sys.exit(main())
