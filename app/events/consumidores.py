"""Consumidores de eventos de dominio.

Hay dos formas de auditar, y la diferencia importa:

- **Acceso denegado.** La peticion termina con `rollback`, asi que el registro
  no puede compartir su transaccion: se escribe en una sesion propia que se
  confirma de inmediato. Es lo que exige ESC-03.
- **Operacion permitida.** El registro pertenece a la misma unidad de trabajo
  que el cambio que audita, y comparte su sesion. Ademas de ser consistente,
  evita que dos conexiones compitan por el bloqueo de escritura.
"""
from typing import Callable

from sqlalchemy.orm import Session

from app import observabilidad
from app.application.bus import BusEventos
from app.domain import eventos
from app.infrastructure.repositorios import RepositorioAuditoriaSQL


def registrar_consumidores(
    bus: BusEventos,
    sesion: Session,
    sesion_factory: Callable[[], Session],
) -> None:
    def auditar_acceso_denegado(evento: eventos.AccesoDenegado) -> None:
        with sesion_factory() as propia:
            RepositorioAuditoriaSQL(propia).registrar(
                usuario=evento.usuario,
                recurso=evento.recurso,
                operacion=evento.operacion,
                resultado="denegado",
            )
            propia.commit()
        # Se cuenta después de confirmar: la métrica no puede decir que hubo
        # un acceso denegado auditado si la auditoría no llegó a escribirse.
        observabilidad.ACCESOS_DENEGADOS.inc()

    def auditar_tarea_creada(evento: eventos.TareaCreada) -> None:
        RepositorioAuditoriaSQL(sesion).registrar(
            usuario=evento.usuario,
            recurso=f"tarea:{evento.tarea_id}",
            operacion="crear_tarea",
            resultado="permitido",
        )

    def auditar_estado_cambiado(evento: eventos.EstadoCambiado) -> None:
        RepositorioAuditoriaSQL(sesion).registrar(
            usuario=evento.usuario,
            recurso=f"tarea:{evento.tarea_id}",
            operacion="cambiar_estado",
            resultado="permitido",
        )

    def auditar(operacion: str):
        """Consumidor que audita una operación permitida sobre una tarea."""

        def consumidor(evento) -> None:
            RepositorioAuditoriaSQL(sesion).registrar(
                usuario=evento.usuario,
                recurso=f"tarea:{evento.tarea_id}",
                operacion=operacion,
                resultado="permitido",
            )

        return consumidor

    bus.suscribir(eventos.AccesoDenegado, auditar_acceso_denegado)
    bus.suscribir(eventos.TareaCreada, auditar_tarea_creada)
    bus.suscribir(eventos.EstadoCambiado, auditar_estado_cambiado)
    # La asignación publicaba su evento pero nadie lo auditaba.
    bus.suscribir(eventos.TareaAsignada, auditar("asignar_tarea"))
    bus.suscribir(eventos.TareaEditada, auditar("editar_tarea"))
    bus.suscribir(eventos.TareaEliminada, auditar("eliminar_tarea"))
