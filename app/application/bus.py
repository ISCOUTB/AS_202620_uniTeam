"""Bus de eventos en proceso.

Implementa el estilo orientado a eventos del ADR 0003 sin infraestructura
distribuida: publicar es una llamada síncrona a los consumidores suscritos.
Un consumidor que falla no tumba la operación que originó el evento —el
desacoplamiento es justamente eso—, pero el fallo se registra.
"""
import logging
from collections import defaultdict
from typing import Callable, Type

from app.domain.eventos import EventoDominio

logger = logging.getLogger(__name__)

Consumidor = Callable[[EventoDominio], None]


class BusEventos:
    def __init__(self) -> None:
        self._consumidores: dict[type, list[Consumidor]] = defaultdict(list)

    def suscribir(self, tipo: Type[EventoDominio], consumidor: Consumidor) -> None:
        self._consumidores[tipo].append(consumidor)

    def publicar(self, evento: EventoDominio) -> None:
        for consumidor in self._consumidores[type(evento)]:
            try:
                consumidor(evento)
            except Exception:
                logger.exception(
                    "Consumidor %s falló al procesar %s",
                    getattr(consumidor, "__name__", consumidor),
                    type(evento).__name__,
                )

    def limpiar(self) -> None:
        self._consumidores.clear()
