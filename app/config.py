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

    # -- Proveedor de identidad (ADR 0005) --------------------------------
    @property
    def oidc_emisor(self) -> str:
        return os.getenv("OIDC_EMISOR", "").rstrip("/")

    @property
    def oidc_audiencia(self) -> str:
        return os.getenv("OIDC_AUDIENCIA", "")

    @property
    def oidc_jwks_url(self) -> str:
        """URL del juego de claves. Si no se indica, se descubre del emisor."""
        return os.getenv("OIDC_JWKS_URL", "")

    @property
    def oidc_claim_usuario(self) -> str:
        """Claim del que sale la identidad. Por defecto el correo."""
        return os.getenv("OIDC_CLAIM_USUARIO", "email")

    @property
    def oidc_configurado(self) -> bool:
        return bool(self.oidc_emisor and self.oidc_audiencia)

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
