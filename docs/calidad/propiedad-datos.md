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

> Auditoría del 2026-10-04 sobre `app/`, con apoyo de IA y revisión del equipo pendiente
> ([bitácora](../ia.md#bitácora-de-uso-de-ia)). Método: lectura de las importaciones y de las consultas
> de cada repositorio, y búsqueda de referencias a tablas de otro contexto.

**Criterio de violación** (según ADR-003): cualquier módulo que lea o escriba directamente
en la tabla/repositorio de otro contexto en vez de usar consulta síncrona autorizada o
evento de dominio.

| # | Módulo que cruza el límite | Dato que toca sin ser dueño | Evidencia | Plan de corrección / estado |
| --- | --- | --- | --- | --- |
| 1 | Tareas y Tablero (`RepositorioTareasSQL.asignadas_a`, vista «Mis tareas») | Membresía y nombre de Proyecto: unía `TareaTabla` con `MiembroTabla` y `ProyectoTabla` | `app/infrastructure/repositorios.py`, método `asignadas_a` (antes del commit de esta entrega) | **Corregida.** La pertenencia se pide por el puerto de Proyectos ([ADR-013](../adr/0013-tareas-no-lee-las-tablas-de-proyectos.md)); guardia en `test_limites_contexto.py` |
| 2 | Notificaciones | — | No hay código: el contexto está en el [mapa](mapa-contextos.md) pero no se ha implementado, y nadie lee el estado de Tarea fuera de Tareas | **No aplica todavía.** Se revisa al implementarlo |
| 3 | Auditoría | Su propia tabla | La escritura pasa solo por `RepositorioAuditoriaSQL`, invocado únicamente desde `app/events/consumidores.py` | **Sin violación.** Un solo escritor |
| 4 | Proyectos y Equipos (`ServicioProyectos`) | Conteos de Tareas para el avance de cada proyecto | `servicio_proyectos.py:48`, vía `RepositorioTareas.resumir_proyectos` | **Observada, no corregida.** Es lectura por puerto, no por tablas, y encaja como consulta síncrona; queda anotada porque Proyectos depende del puerto de Tareas y Tareas del de Proyectos |

La detección del hallazgo 1 fue por lectura del repositorio durante la auditoría; la prueba
`test_el_repositorio_de_tareas_no_toca_las_tablas_de_proyectos` la convierte en detección automática en la CI.

**Puntos a revisar primero en el código:**

- Cualquier `import` cruzado entre los paquetes de tareas y de proyectos que acceda a
  modelos ORM directamente (en vez de a través de un puerto/servicio del otro contexto).
- Endpoints que devuelven campos de más de un contexto en una sola respuesta sin pasar por
  una capa de composición (esto no es necesariamente una violación, pero hay que verificar
  que no está escribiendo también).
- Cualquier lugar donde el backend haga una escritura de auditoría "de paso" dentro de la
  lógica de otro contexto, en vez de publicar el evento y dejar que Auditoría escriba.
