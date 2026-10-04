# ADR-013 — Tareas no lee las tablas de Proyectos: la pertenencia se pide por el puerto

- **Estado:** Propuesta — pasa a *Aceptada* cuando el equipo la apruebe y anote la fecha en [D-025](../ia.md#decisiones-tomadas-por-el-equipo)
- **Fecha:** 2026-10-04
- **Decisores:** Equipo de desarrollo (I-04)
- **Escenarios:** [ESC-03](../calidad/escenarios-calidad.md#esc-03) (seguridad) · [ESC-01](../calidad/escenarios-calidad.md#esc-01) (rendimiento)
- **Relacionada:** [ADR-003](0003-usar-eventos-de-dominio-en-proceso.md), [propiedad de datos](../calidad/propiedad-datos.md)

## Contexto

La auditoría de propiedad de datos ([hallazgo 1](../calidad/propiedad-datos.md#violaciones-detectadas-en-el-código-actual))
encontró que `RepositorioTareasSQL.asignadas_a`, que sirve «Mis tareas» (A-12), unía en un solo SQL
`TareaTabla` con `MiembroTabla` y `ProyectoTabla`. Esas dos tablas son de **Proyectos y Equipos**.
La consulta funcionaba y respetaba ESC-03, pero dejaba al contexto de Tareas dependiendo del
esquema de otro: renombrar una columna de `miembros` rompería «Mis tareas» sin que ningún módulo de
Proyectos lo supiera. Es el tipo de erosión que ADR-003 quería evitar, y la introdujo código generado
con apoyo de IA en la sesión del 2026-09-28 (ver [bitácora de IA](../ia.md#bitácora-de-uso-de-ia)).

## Alternativas

| | A. Pedir la pertenencia al puerto de Proyectos (**propuesta**) | B. Dejar el `JOIN` y documentarlo | C. Copiar la membresía a una tabla de Tareas por eventos |
|---|---|---|---|
| Cómo | `ServicioTareas.mis_tareas` llama a `listar_por_usuario` y pasa a Tareas solo los proyectos autorizados | Nada cambia | Tareas mantiene su propia proyección de miembros |
| Respeta la propiedad de datos | Sí | No | Sí |
| ESC-03 | Síncrono, antes de buscar tareas (como exige ADR-003) | Igual | Depende de que el evento haya llegado: ventana de inconsistencia |
| Costo | Una consulta más por petición | Ninguno | Tabla nueva, migración y consumidores |
| Reversión | Fácil | — | Costosa |

**Por qué se descarta B.** Es la erosión que se quiere cerrar; documentarla la normaliza.
**Por qué se descarta C.** La autorización no puede llegar por evento con retraso
([mapa de contextos](../calidad/mapa-contextos.md#relaciones-entre-contextos)), y exige una migración en una base ya desplegada.

## Decisión

Tareas **solo lee `TareaTabla`**. La pertenencia es una consulta síncrona a Proyectos y Equipos
(`RepositorioProyectos.listar_por_usuario`); el nombre del proyecto también sale de ahí, y el servicio
compone la vista. El puerto `RepositorioTareas.asignadas_a` pasa a recibir `proyecto_ids` y a devolver `Tarea`.

**Guardia.** `test_el_repositorio_de_tareas_no_toca_las_tablas_de_proyectos`
([`test/test_limites_contexto.py`](../../test/test_limites_contexto.py)) recorre el AST de
`RepositorioTareasSQL` y falla si aparece `ProyectoTabla` o `MiembroTabla`. Antes del cambio fallaba
con ambas; ahora pasa.

## Consecuencias

- Una consulta adicional por petición a `/mis-tareas`. Medida: +1,2 ms de mediana en SQLite
  ([ficha](../calidad/mediciones/mis-tareas-limite-contexto.md)); no medida sobre MySQL.
- `listar_por_usuario` carga los miembros de cada proyecto aunque aquí solo se necesiten id y nombre.
  Si la medición sobre MySQL lo muestra caro, se añade un método de lectura mínima al puerto, sin
  tocar a Tareas.
- Quien añada una consulta de Tareas que necesite datos de Proyectos tiene dos caminos: el puerto, o un evento.

## Reversión

Volver a unir las tablas en `asignadas_a`. No hay datos que migrar.

## Trazabilidad

[`servicio_tareas.py`](../../app/application/servicio_tareas.py) (`mis_tareas`) ·
[`repositorios.py`](../../app/infrastructure/repositorios.py) (`asignadas_a`) ·
[`puertos.py`](../../app/application/puertos.py) · [`test_limites_contexto.py`](../../test/test_limites_contexto.py) ·
[`test_vistas.py`](../../test/test_vistas.py)
