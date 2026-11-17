#Notificaciones de cambios de tareas mediante WebSocket.
import asyncio
import itertools
import logging
import threading
from dataclasses import dataclass

from sqlalchemy.orm import Session


registro = logging.getLogger("uniteam.websocket")


@dataclass(frozen=True)
class Conexion:
    proyecto_id: str
    loop: asyncio.AbstractEventLoop
    cola: asyncio.Queue[dict[str, str]]


class GestorConexiones:
    """Conexiones locales al proceso; cada mensaje solo invalida el tablero."""

    def __init__(self) -> None:
        self._candado = threading.Lock()
        self._ids = itertools.count()
        self._conexiones: dict[int, Conexion] = {}

    async def registrar(self, proyecto_id: str) -> tuple[int, Conexion]:
        conexion = Conexion(
            proyecto_id=proyecto_id,
            loop=asyncio.get_running_loop(),
            cola=asyncio.Queue(maxsize=1),
        )
        with self._candado:
            identificador = next(self._ids)
            self._conexiones[identificador] = conexion
        return identificador, conexion

    def retirar(self, identificador: int) -> None:
        with self._candado:
            self._conexiones.pop(identificador, None)

    def publicar_cambio(self, proyecto_id: str) -> None:
        """Programa notificaciones solo para sockets del proyecto afectado."""
        with self._candado:
            conexiones = [
                conexion
                for conexion in self._conexiones.values()
                if conexion.proyecto_id == proyecto_id
            ]

        mensaje = {"tipo": "tareas_actualizadas", "proyecto_id": proyecto_id}
        for conexion in conexiones:
            try:
                conexion.loop.call_soon_threadsafe(
                    self._encolar, conexion.cola, mensaje
                )
            except RuntimeError:
                registro.warning(
                    "No se pudo notificar un cambio: el bucle WebSocket ya terminó",
                    extra={"evento": "notificacion_descartada", "proyecto_id": proyecto_id},
                )

    @staticmethod
    def _encolar(
        cola: asyncio.Queue[dict[str, str]], mensaje: dict[str, str]
    ) -> None:
        # La notificación es una invalidación, no un registro durable de eventos.
        # Una pendiente basta; al reconectar el cliente vuelve a consultar el tablero.
        if not cola.full():
            cola.put_nowait(mensaje)


gestor_conexiones = GestorConexiones()


def registrar_cambio_confirmado(sesion: Session, proyecto_id: str) -> None:
    """Acumula cambios dentro de la transacción para publicarlos después del commit."""
    sesion.info.setdefault("proyectos_con_cambios", set()).add(proyecto_id)


def publicar_cambios_confirmados(sesion: Session) -> None:
    """Publica cambios ya confirmados y limpia el estado asociado a la sesión."""
    proyectos = sesion.info.pop("proyectos_con_cambios", set())
    for proyecto_id in proyectos:
        gestor_conexiones.publicar_cambio(proyecto_id)
