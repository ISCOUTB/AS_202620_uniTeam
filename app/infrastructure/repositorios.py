"""Adaptadores de persistencia: implementan los puertos con SQLAlchemy."""
from datetime import date, datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.config import ajustes
from app.domain.modelos import (
    ESTADO_FINAL,
    EstadoTarea,
    Miembro,
    Prioridad,
    Proyecto,
    ResumenCorto,
    ResumenProgreso,
    RolMiembro,
    Tarea,
)
from app.infrastructure.tablas import (
    AuditoriaTabla,
    MiembroTabla,
    ProyectoTabla,
    TareaTabla,
)


def _ahora_utc() -> datetime:
    return datetime.now(timezone.utc)


def hoy_local() -> date:
    """La fecha de hoy donde están los usuarios, no donde está el servidor.

    El servidor corre en UTC: a partir de las 19:00 en Colombia ya es mañana
    allí, y una tarea que vence hoy contaba como vencida.
    """
    return _ahora_utc().astimezone(ZoneInfo(ajustes.zona_horaria)).date()


class RepositorioProyectosSQL:
    def __init__(self, sesion: Session) -> None:
        self._s = sesion

    def obtener(self, proyecto_id: str) -> Optional[Proyecto]:
        fila = self._s.get(ProyectoTabla, proyecto_id)
        if fila is None:
            return None
        return Proyecto(
            id=fila.id,
            nombre=fila.nombre,
            miembros=[
                Miembro(usuario=m.usuario, rol=RolMiembro(m.rol)) for m in fila.miembros
            ],
        )

    def listar_por_usuario(self, usuario: str) -> list[Proyecto]:
        """Solo los proyectos de los que el usuario es miembro.

        El filtro está en la consulta, no después: así no existe la ruta por
        la que un proyecto ajeno llegue siquiera a memoria (ESC-03).
        """
        filas = self._s.scalars(
            select(ProyectoTabla)
            .join(MiembroTabla, MiembroTabla.proyecto_id == ProyectoTabla.id)
            .where(MiembroTabla.usuario == usuario)
            .order_by(ProyectoTabla.nombre)
        ).all()
        return [
            Proyecto(
                id=f.id,
                nombre=f.nombre,
                miembros=[
                    Miembro(usuario=m.usuario, rol=RolMiembro(m.rol)) for m in f.miembros
                ],
            )
            for f in filas
        ]

    def guardar(self, proyecto: Proyecto) -> None:
        fila = self._s.get(ProyectoTabla, proyecto.id)
        if fila is None:
            fila = ProyectoTabla(id=proyecto.id, nombre=proyecto.nombre)
            self._s.add(fila)
        else:
            fila.nombre = proyecto.nombre
        self._s.flush()

        existentes = {m.usuario for m in fila.miembros}
        for miembro in proyecto.miembros:
            if miembro.usuario not in existentes:
                self._s.add(
                    MiembroTabla(
                        proyecto_id=proyecto.id,
                        usuario=miembro.usuario,
                        rol=miembro.rol.value,
                    )
                )
        self._s.flush()


class RepositorioTareasSQL:
    def __init__(self, sesion: Session) -> None:
        self._s = sesion

    @staticmethod
    def _a_dominio(fila: TareaTabla) -> Tarea:
        return Tarea(
            id=fila.id,
            proyecto_id=fila.proyecto_id,
            titulo=fila.titulo,
            creada_por=fila.creada_por,
            prioridad=Prioridad(fila.prioridad),
            estado=EstadoTarea(fila.estado),
            responsable=fila.responsable,
            fecha_limite=fila.fecha_limite,
            creada_en=fila.creada_en,
        )

    def obtener(self, tarea_id: str) -> Optional[Tarea]:
        fila = self._s.get(TareaTabla, tarea_id)
        return self._a_dominio(fila) if fila else None

    def guardar(self, tarea: Tarea) -> None:
        fila = self._s.get(TareaTabla, tarea.id)
        if fila is None:
            fila = TareaTabla(id=tarea.id, creada_en=tarea.creada_en)
            self._s.add(fila)
        fila.proyecto_id = tarea.proyecto_id
        fila.titulo = tarea.titulo
        fila.creada_por = tarea.creada_por
        fila.prioridad = tarea.prioridad.value
        fila.estado = tarea.estado.value
        fila.responsable = tarea.responsable
        fila.fecha_limite = tarea.fecha_limite
        self._s.flush()

    def eliminar(self, tarea_id: str) -> None:
        fila = self._s.get(TareaTabla, tarea_id)
        if fila is not None:
            self._s.delete(fila)
            self._s.flush()

    def listar_por_proyecto(
        self,
        proyecto_id: str,
        estado: Optional[EstadoTarea] = None,
        responsable: Optional[str] = None,
        limite: int = 50,
        desplazamiento: int = 0,
    ) -> list[Tarea]:
        consulta = select(TareaTabla).where(TareaTabla.proyecto_id == proyecto_id)
        if estado is not None:
            consulta = consulta.where(TareaTabla.estado == estado.value)
        if responsable is not None:
            consulta = consulta.where(TareaTabla.responsable == responsable)
        # El id desempata: ordenar solo por fecha haría inestable la paginación
        # si dos tareas comparten marca de tiempo.
        consulta = (
            consulta.order_by(TareaTabla.creada_en, TareaTabla.id)
            .limit(limite)
            .offset(desplazamiento)
        )
        return [self._a_dominio(f) for f in self._s.scalars(consulta).all()]

    def resumir_proyectos(self, proyecto_ids: list[str]) -> dict[str, ResumenCorto]:
        return resumir_proyectos(self._s, proyecto_ids)

    def asignadas_a(
        self, usuario: str, proyecto_ids: list[str], incluir_terminadas: bool = False
    ) -> list[Tarea]:
        """Tareas cuyo responsable es el usuario dentro de los proyectos indicados.

        La pertenencia **no se averigua aquí**: es dato de Proyectos y Equipos, y
        quien llama (`ServicioTareas.mis_tareas`) la obtiene de su puerto y pasa
        solo proyectos ya autorizados. El filtro sigue en la consulta, así que
        una tarea de un proyecto no autorizado nunca llega a memoria (ESC-03).
        """
        if not proyecto_ids:
            return []
        consulta = select(TareaTabla).where(
            TareaTabla.responsable == usuario, TareaTabla.proyecto_id.in_(proyecto_ids)
        )
        if not incluir_terminadas:
            consulta = consulta.where(TareaTabla.estado != ESTADO_FINAL.value)
        # Primero lo que tiene fecha, de la más cercana a la más lejana.
        consulta = consulta.order_by(
            TareaTabla.fecha_limite.is_(None), TareaTabla.fecha_limite, TareaTabla.creada_en
        ).limit(200)
        return [self._a_dominio(fila) for fila in self._s.scalars(consulta)]

    def resumir_progreso(self, proyecto_id: str) -> ResumenProgreso:
        """Cuenta en la base de datos, sin traer las tareas a memoria."""
        por_estado = dict(
            self._s.execute(
                select(TareaTabla.estado, func.count())
                .where(TareaTabla.proyecto_id == proyecto_id)
                .group_by(TareaTabla.estado)
            ).all()
        )
        sin_responsable = self._s.scalar(
            select(func.count())
            .select_from(TareaTabla)
            .where(
                TareaTabla.proyecto_id == proyecto_id,
                TareaTabla.responsable.is_(None),
            )
        )
        vencidas = self._s.scalar(
            select(func.count())
            .select_from(TareaTabla)
            .where(
                TareaTabla.proyecto_id == proyecto_id,
                TareaTabla.fecha_limite.is_not(None),
                TareaTabla.fecha_limite < hoy_local(),
                TareaTabla.estado != ESTADO_FINAL.value,
            )
        )
        return ResumenProgreso(
            total=sum(por_estado.values()),
            por_estado={str(k): int(v) for k, v in por_estado.items()},
            sin_responsable=int(sin_responsable or 0),
            vencidas=int(vencidas or 0),
        )


def _resumenes_vacios(ids: list[str]) -> dict[str, ResumenCorto]:
    return {i: ResumenCorto() for i in ids}


def resumir_proyectos(sesion: Session, proyecto_ids: list[str]) -> dict[str, ResumenCorto]:
    """Total, terminadas y vencidas de varios proyectos en dos consultas agregadas,
    en vez de una petición de progreso por tarjeta."""
    resumenes = _resumenes_vacios(proyecto_ids)
    if not proyecto_ids:
        return resumenes
    for proyecto_id, estado, cuantas in sesion.execute(
        select(TareaTabla.proyecto_id, TareaTabla.estado, func.count())
        .where(TareaTabla.proyecto_id.in_(proyecto_ids))
        .group_by(TareaTabla.proyecto_id, TareaTabla.estado)
    ):
        resumenes[proyecto_id].total += int(cuantas)
        if estado == ESTADO_FINAL.value:
            resumenes[proyecto_id].terminadas += int(cuantas)
    for proyecto_id, cuantas in sesion.execute(
        select(TareaTabla.proyecto_id, func.count())
        .where(
            TareaTabla.proyecto_id.in_(proyecto_ids),
            TareaTabla.fecha_limite.is_not(None),
            TareaTabla.fecha_limite < hoy_local(),
            TareaTabla.estado != ESTADO_FINAL.value,
        )
        .group_by(TareaTabla.proyecto_id)
    ):
        resumenes[proyecto_id].vencidas = int(cuantas)
    return resumenes


class RepositorioAuditoriaSQL:
    def __init__(self, sesion: Session) -> None:
        self._s = sesion

    def registrar(
        self, usuario: str, recurso: str, operacion: str, resultado: str
    ) -> None:
        self._s.add(
            AuditoriaTabla(
                usuario=usuario,
                recurso=recurso,
                operacion=operacion,
                resultado=resultado,
                ocurrido_en=datetime.now(timezone.utc),
            )
        )
        self._s.flush()
