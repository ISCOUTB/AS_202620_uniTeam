"""Esquemas de entrada y salida de la API (Pydantic).

Los límites de longitud coinciden con las columnas de la base de datos: una
entrada que no cabe se rechaza con 422 aquí, en lugar de llegar a MySQL y
volver como un error interno.
"""
from datetime import date, datetime
from typing import Annotated, Optional

from pydantic import AfterValidator, BaseModel, Field, StringConstraints, model_validator

from app.domain.modelos import EstadoTarea, Prioridad, RolMiembro, normalizar_usuario

# Identidad de un usuario: el correo, sin espacios y en minúsculas.
Usuario = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=120),
    AfterValidator(normalizar_usuario),
]
Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Titulo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]


class CrearProyecto(BaseModel):
    nombre: Nombre
    miembros: list[Usuario] = Field(default_factory=list, max_length=50)


class CrearTarea(BaseModel):
    titulo: Titulo
    prioridad: Prioridad = Prioridad.MEDIA
    responsable: Optional[Usuario] = None
    fecha_limite: Optional[date] = None


class EditarTarea(BaseModel):
    """Edición parcial. Un campo ausente no cambia; `fecha_limite: null` la quita."""

    titulo: Optional[Titulo] = None
    prioridad: Optional[Prioridad] = None
    fecha_limite: Optional[date] = None

    @model_validator(mode="after")
    def _algo_que_cambiar(self) -> "EditarTarea":
        if not self.model_fields_set:
            raise ValueError("Indique al menos un campo: titulo, prioridad o fecha_limite.")
        if "titulo" in self.model_fields_set and self.titulo is None:
            raise ValueError("El título no puede quedar vacío.")
        if "prioridad" in self.model_fields_set and self.prioridad is None:
            raise ValueError("La prioridad no puede quedar vacía.")
        return self

    @property
    def quitar_fecha_limite(self) -> bool:
        return "fecha_limite" in self.model_fields_set and self.fecha_limite is None


class AsignarTarea(BaseModel):
    responsable: Usuario


class CambiarEstado(BaseModel):
    estado: EstadoTarea


class TareaSalida(BaseModel):
    id: str
    proyecto_id: str
    titulo: str
    prioridad: Prioridad
    estado: EstadoTarea
    responsable: Optional[str] = None
    fecha_limite: Optional[date] = None
    creada_por: str
    creada_en: datetime


class ProyectoSalida(BaseModel):
    id: str
    nombre: str
    miembros: list[str]


class AgregarMiembro(BaseModel):
    usuario: Usuario
    rol: RolMiembro = RolMiembro.INTEGRANTE


class MiembroSalida(BaseModel):
    usuario: str
    rol: RolMiembro


class ProyectoDetalle(BaseModel):
    id: str
    nombre: str
    miembros: list[MiembroSalida]


class ProgresoSalida(BaseModel):
    total: int
    por_estado: dict[str, int]
    sin_responsable: int
    vencidas: int
    porcentaje_completado: float


class EstadoFlujo(BaseModel):
    id: str
    etiqueta: str
    inicial: bool
    final: bool
    siguientes: list[str]


class FlujoEstados(BaseModel):
    estados: list[EstadoFlujo]
