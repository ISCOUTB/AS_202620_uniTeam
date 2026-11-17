#Conexiones WebSocket autenticadas para actualizaciones del tablero.
import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import HTTPException

from app.api.seguridad import ConfiguracionInvalida, identidad_del_token
from app.api.tiempo_real import Conexion, gestor_conexiones
from app.application.bus import BusEventos
from app.application.servicio_tareas import ServicioTareas
from app.config import ajustes
from app.infrastructure.db import SesionLocal
from app.infrastructure.repositorios import (
    RepositorioProyectosSQL,
    RepositorioTareasSQL,
)
from app.domain.errores import AccesoDenegado
from app.events.consumidores import registrar_consumidores


registro = logging.getLogger("uniteam.websocket")
router = APIRouter(tags=["tiempo real"])
_TIEMPO_AUTENTICACION_SEGUNDOS = 10
_LONGITUD_MAXIMA_TOKEN = 8192


def _es_miembro(proyecto_id: str, usuario: str) -> bool:
    with SesionLocal() as sesion:
        bus = BusEventos()
        registrar_consumidores(bus, sesion, SesionLocal)
        servicio = ServicioTareas(
            proyectos=RepositorioProyectosSQL(sesion),
            tareas=RepositorioTareasSQL(sesion),
            bus=bus,
        )
        try:
            servicio.verificar_acceso_proyecto(
                usuario, proyecto_id, "conectar_websocket"
            )
        except AccesoDenegado:
            return False
        return True


async def _autenticar(websocket: WebSocket) -> str | None:
    try:
        texto = await asyncio.wait_for(
            websocket.receive_text(), timeout=_TIEMPO_AUTENTICACION_SEGUNDOS
        )
    except asyncio.TimeoutError:
        await websocket.close(code=4408, reason="Tiempo de autenticación agotado")
        return None
    except WebSocketDisconnect:
        return None

    try:
        credencial: Any = json.loads(texto)
    except json.JSONDecodeError:
        await websocket.close(code=4400, reason="Mensaje de autenticación inválido")
        return None

    token = credencial.get("token") if isinstance(credencial, dict) else None
    if (
        not isinstance(credencial, dict)
        or credencial.get("tipo") != "autenticar"
        or not isinstance(token, str)
        or not token
        or len(token) > _LONGITUD_MAXIMA_TOKEN
    ):
        await websocket.close(code=4401, reason="Autenticación requerida")
        return None

    if ajustes.auth_disabled:
        return ajustes.demo_usuario

    try:
        return await run_in_threadpool(identidad_del_token, token)
    except HTTPException:
        await websocket.close(code=4401, reason="Credencial inválida")
        return None
    except ConfiguracionInvalida:
        registro.exception(
            "No se pudo autenticar la conexión WebSocket",
            extra={"evento": "error_autenticacion_websocket"},
        )
        await websocket.close(code=1011, reason="Error de autenticación")
        return None
    except Exception:
        registro.exception(
            "Falló la autenticación de la conexión WebSocket",
            extra={"evento": "error_autenticacion_websocket"},
        )
        await websocket.close(code=1011, reason="Error de autenticación")
        return None


async def _servir_notificaciones(websocket: WebSocket, conexion: Conexion) -> None:
    while True:
        recibir = asyncio.create_task(websocket.receive())
        notificacion = asyncio.create_task(conexion.cola.get())
        tareas = {recibir, notificacion}
        hechas, pendientes = await asyncio.wait(
            tareas, return_when=asyncio.FIRST_COMPLETED
        )
        for tarea in pendientes:
            tarea.cancel()
        if pendientes:
            await asyncio.gather(*pendientes, return_exceptions=True)

        if recibir in hechas:
            mensaje = recibir.result()
            if mensaje["type"] == "websocket.disconnect":
                return
            await websocket.close(code=1008, reason="No se aceptan mensajes")
            return

        await websocket.send_json(notificacion.result())


@router.websocket("/proyectos/{proyecto_id}/eventos")
async def eventos_proyecto(websocket: WebSocket, proyecto_id: str) -> None:
    await websocket.accept()
    origen = websocket.headers.get("origin")
    if origen and origen.rstrip("/") not in ajustes.origenes_permitidos:
        await websocket.close(code=4403, reason="Origen no permitido")
        return

    usuario = await _autenticar(websocket)
    if usuario is None:
        return

    try:
        autorizado = await run_in_threadpool(_es_miembro, proyecto_id, usuario)
    except Exception:
        registro.exception(
            "No se pudo autorizar la conexión WebSocket",
            extra={"evento": "error_autorizacion_websocket"},
        )
        await websocket.close(code=1011, reason="Error de autorización")
        return

    if not autorizado:
        registro.warning(
            "Conexión WebSocket denegada",
            extra={
                "evento": "websocket_denegado",
                "proyecto_id": proyecto_id,
                "usuario": usuario,
            },
        )
        await websocket.close(code=4403, reason="Sin acceso al proyecto")
        return

    identificador, conexion = await gestor_conexiones.registrar(proyecto_id)
    try:
        await websocket.send_json({"tipo": "conectado"})
        await _servir_notificaciones(websocket, conexion)
    except WebSocketDisconnect:
        pass
    finally:
        gestor_conexiones.retirar(identificador)
