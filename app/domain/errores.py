"""Errores del dominio. No conocen HTTP: la capa de API los traduce."""


class ErrorDominio(Exception):
    """Raíz de los errores propios del dominio."""


class AccesoDenegado(ErrorDominio):
    """El usuario no pertenece al proyecto sobre el que opera (ESC-03)."""


class RecursoNoEncontrado(ErrorDominio):
    """El proyecto o la tarea solicitados no existen."""


class TransicionInvalida(ErrorDominio):
    """El estado destino no es alcanzable desde el estado actual."""
