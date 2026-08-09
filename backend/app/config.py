"""
Configuración central de la aplicación.
Lee variables de entorno desde .env
"""

from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/innova_activos"

    # JWT
    SECRET_KEY: str = "tu_clave_secreta_super_segura_cambiar_en_produccion_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:8080"]'

    # App
    APP_NAME: str = "InnovaActivos API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    @property
    def cors_origins_list(self) -> List[str]:
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            return ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
