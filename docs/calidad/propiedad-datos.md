# Propiedad de datos y auditoría de modularidad — UniTeam

Complementa el [mapa de contextos](mapa-contextos.md). Cada entidad tiene un único
módulo con permiso de **escritura**; cualquier otro contexto que necesite el dato lo obtiene
por consulta síncrona (Identidad y Autorización) o por evento de dominio (los demás casos),
según lo define [ADR-003](../adr/0003-usar-eventos-de-dominio-en-proceso.md).

---

## Tabla módulo → dato → dueño

| Entidad | Módulo dueño (escritura) | Consumidores (solo lectura) | Mecanismo de acceso para consumidores |
| --- | --- | --- | --- |
| Usuario, Credencial | Identidad y Autorización | Proyectos y Equipos, Tareas y Tablero | Consulta síncrona (verificación de identidad/rol) |
| Permiso/Rol global | Identidad y Autorización | Todos | Consulta síncrona |
| Proyecto | Proyectos y Equipos | Tareas y Tablero, Notificaciones | Evento `ProyectoCreado`; consulta síncrona para validar pertenencia |
| Membresía (usuario↔proyecto, rol de proyecto) | Proyectos y Equipos | Identidad y Autorización (para autorizar), Notificaciones | Consulta síncrona + evento `MiembroAgregado`/`MiembroRemovido` |
| Tarea | Tareas y Tablero | Notificaciones, Auditoría | Evento `TareaCreada`, `TareaCambioEstado` |
| Estado de tarea (historial) | Tareas y Tablero | Auditoría | Evento `TareaCambioEstado` |
| Evento de auditoría | Auditoría | Profesor/Universidad (solo lectura vía reporte) | N/A — Auditoría es el único escritor de su propia tabla |
| Notificación | Notificaciones | — | N/A — nadie más necesita leer directo de esta tabla |

*(Completar/corregir esta tabla contra el esquema real de MySQL y los modelos de FastAPI —
esta versión parte del mapa de contextos, no de una inspección línea por línea del código.)*

---

## Violaciones detectadas en el código actual

> Esta sección requiere revisar los routers de FastAPI y los modelos SQLAlchemy/Pydantic
> con el criterio de auditoría y un par de puntos típicos a revisar primero; el laboratorio
> pide llenarla con hallazgos reales.

**Criterio de violación** (según ADR-003): cualquier módulo que lea o escriba directamente
en la tabla/repositorio de otro contexto en vez de usar consulta síncrona autorizada o
evento de dominio.

| # | Módulo que cruza el límite | Dato que toca sin ser dueño | Evidencia (archivo/línea) | Plan de corrección |
| --- | --- | --- | --- | --- |
| 1 | *(revisar)* Router de tareas | *(revisar)* ¿Escribe o consulta tabla de Proyecto/Membresía sin pasar por Proyectos y Equipos? | `app/...` | Exponer una consulta síncrona explícita en Proyectos y Equipos, o suscribirse al evento correspondiente en vez de leer la tabla directo |
| 2 | *(revisar)* Notificaciones | *(revisar)* ¿Lee el estado de Tarea directo de la base en vez de reaccionar al evento `TareaCambioEstado`? | `app/...` | Migrar a consumidor de evento; eliminar el acceso directo |
| 3 | *(revisar)* Auditoría | *(revisar)* ¿Escribe en su propia tabla desde más de un módulo (rompiendo dueño único de escritura)? | `app/...` | Centralizar la escritura de auditoría en un único servicio/publicador |

**Puntos a revisar primero en el código:**

- Cualquier `import` cruzado entre los paquetes de tareas y de proyectos que acceda a
  modelos ORM directamente (en vez de a través de un puerto/servicio del otro contexto).
- Endpoints que devuelven campos de más de un contexto en una sola respuesta sin pasar por
  una capa de composición (esto no es necesariamente una violación, pero hay que verificar
  que no está escribiendo también).
- Cualquier lugar donde el backend haga una escritura de auditoría "de paso" dentro de la
  lógica de otro contexto, en vez de publicar el evento y dejar que Auditoría escriba.
