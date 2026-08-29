"""Motor de base de datos y fábrica de sesiones.

MySQL en ejecución (ADR 0004); SQLite cuando `DATABASE_URL` no está definida,
para que las pruebas corran sin levantar servicios.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import ajustes


class Base(DeclarativeBase):
    pass


def crear_engine(url: str | None = None):
    url = url or ajustes.database_url
    opciones = {"pool_pre_ping": True, "future": True}
    if url.startswith("sqlite"):
        opciones["connect_args"] = {"check_same_thread": False}
    return create_engine(url, **opciones)


engine = crear_engine()
SesionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def crear_esquema(motor=None) -> None:
    from app.infrastructure import tablas  # noqa: F401  (registra los modelos)

    Base.metadata.create_all(motor or engine)
