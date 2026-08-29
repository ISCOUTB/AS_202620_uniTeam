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

    @property
    def origenes_permitidos(self) -> list[str]:
        """Orígenes que pueden llamar a la API desde un navegador.

        La Aplicación Web se ejecuta en el navegador del usuario, así que la
        relación «Aplicación Web -> API» del C4 nivel 2 es una petición entre
        orígenes distintos y necesita CORS. La lista es explícita: nunca `*`.
        """
        crudo = os.getenv("ORIGENES_PERMITIDOS", "http://localhost:3000")
        return [o.strip() for o in crudo.split(",") if o.strip()]


ajustes = Ajustes()
