"""Crea o actualiza el esquema de la base de datos del despliegue.

El proyecto todavía no usa Alembic: el esquema se declara en SQLAlchemy y esta
operación es idempotente mediante ``create_all``. Dokploy puede ejecutarla como
comando de migración antes de arrancar la API.
"""

from app.infrastructure.db import crear_esquema, engine


if __name__ == "__main__":
    crear_esquema(engine)
    print("Esquema de UniTeam listo.")
