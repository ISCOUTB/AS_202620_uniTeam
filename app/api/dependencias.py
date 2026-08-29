"""Dependencias de FastAPI: sesión, identidad y composición de servicios.

La identidad la resuelve `app.api.seguridad` a partir del token que emite el
proveedor de identidad (ADR 0005). La autorización de ESC-03 es posterior e
independiente: estar autenticado no da acceso a un proyecto ajeno.
"""
from typing import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.bus import BusEventos
from app.application.servicio_proyectos import ServicioProyectos
from app.application.servicio_tareas import ServicioTareas
from app.api.seguridad import usuario_actual
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


def obtener_servicio(sesion: Session = Depends(obtener_sesion)) -> ServicioTareas:
    bus = BusEventos()
    registrar_consumidores(bus, sesion, SesionLocal)
    return ServicioTareas(
        proyectos=RepositorioProyectosSQL(sesion),
        tareas=RepositorioTareasSQL(sesion),
        bus=bus,
    )


def obtener_servicio_proyectos(
    sesion: Session = Depends(obtener_sesion),
) -> ServicioProyectos:
    bus = BusEventos()
    registrar_consumidores(bus, sesion, SesionLocal)
    return ServicioProyectos(proyectos=RepositorioProyectosSQL(sesion), bus=bus)
