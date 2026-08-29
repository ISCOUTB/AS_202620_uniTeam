"""Configuración del sistema, leída del entorno.

La URL por defecto usa SQLite para que `pytest` funcione recién clonado el
repositorio, sin levantar servicios. El despliegue y el arranque con Docker
usan MySQL (ver ADR 0004).
"""
import os


class Ajustes:
    @property
    def database_url(self) -> str:
        return os.getenv("DATABASE_URL", "sqlite:///./uniteam.db")

    @property
    def crear_esquema_al_arrancar(self) -> bool:
        return os.getenv("CREAR_ESQUEMA", "1") == "1"


ajustes = Ajustes()
