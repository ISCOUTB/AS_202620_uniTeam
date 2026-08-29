"""Dependencias de FastAPI: sesión, identidad y composición de servicios.

**Identidad provisional.** El usuario se toma de la cabecera `X-Usuario`
mientras no se integra el proveedor de identidad (OIDC) del C4 nivel 2. La
autorización que ejercita ESC-03 sí es real: comprueba la pertenencia al
proyecto contra la base de datos.
"""
from typing import Iterator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.application.bus import BusEventos
from app.application.servicio_tareas import ServicioTareas
from app.events.consumidores import registrar_consumidores
from app.infrastructure.db import SesionLocal
from app.infrastructure.repositorios import (
    RepositorioProyectosSQL,
    RepositorioTareasSQL,
)


def obtener_sesion() -> Iterator[Session]:
    sesion = SesionLocal()
    try:
        yield sesion
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    finally:
        sesion.close()


def usuario_actual(x_usuario: str = Header(..., alias="X-Usuario")) -> str:
    return x_usuario


def obtener_servicio(sesion: Session = Depends(obtener_sesion)) -> ServicioTareas:
    bus = BusEventos()
    registrar_consumidores(bus, sesion, SesionLocal)
    return ServicioTareas(
        proyectos=RepositorioProyectosSQL(sesion),
        tareas=RepositorioTareasSQL(sesion),
        bus=bus,
    )
