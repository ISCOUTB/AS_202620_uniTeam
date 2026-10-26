# ADR-016 — Conservar MySQL como fuente de verdad

- **Estado:** Aceptada
- **Fecha:** 2026-10-25
- **Decisores:** Equipo de desarrollo
- **Relacionada:** [ADR-004](0004-usar-mysql-como-base-de-datos.md) eligió el motor; [ADR-009](0009-usar-aiven-for-mysql-como-base-de-datos-gestionada.md) eligió el proveedor gestionado.

## Contexto

UniTeam ya persiste proyectos, membresías, tareas y auditoría en MySQL. No es solo
una preferencia de motor: las operaciones de la API, sus transacciones y la
integridad entre esos datos dependen de un esquema relacional desplegado. Esta es
la decisión de datos más costosa de revertir; eliminar una caché o sustituir un
consumidor en proceso no exigiría migrar la fuente de verdad.

El volumen actual es pequeño, pero la aplicación ya depende de relaciones entre
proyectos, miembros, tareas y auditoría, de claves primarias y de consultas SQL.
El acceso pasa por SQLAlchemy y los repositorios, aunque eso no elimina las
diferencias de esquema, tipos y comportamiento entre motores.

## Alternativas

| Alternativa | Ventajas | Costos y riesgos |
|---|---|---|
| **Conservar MySQL como fuente de verdad (elegida)** | Mantiene el esquema probado en desarrollo, CI y producción; no requiere migrar datos ni cambiar el despliegue. | Se conserva la dependencia de MySQL y del proveedor gestionado actual. |
| Migrar a PostgreSQL u otro motor relacional | Permite reevaluar funciones, proveedor y costos cuando cambien las necesidades. | Requiere transformar y validar el esquema y los datos, comprobar consultas y restricciones, adaptar despliegue y copias, y planificar el corte sin escrituras perdidas. |
| Reemplazar MySQL por un almacén no relacional o un event store | Puede servir a otro modelo de acceso si el producto cambia radicalmente. | Obliga a rediseñar relaciones, consistencia, consultas, auditoría y casos de uso; es una migración mayor que cambiar de proveedor MySQL. |

## Decisión

Se conserva MySQL como fuente autoritativa de proyectos, membresías, tareas y
auditoría. SQLAlchemy y los repositorios siguen siendo la frontera de acceso. No
se añade una segunda fuente de verdad ni se introduce un almacén de caché para
datos de negocio; el criterio vigente de lecturas e invalidación está en
[arc42 §8.2](../arc42/arc42-uniteam.md#82-caché-e-invalidación).

Cambiar de proveedor conservando MySQL es una decisión distinta y de menor
alcance; no implica cambiar el motor. Si aparecen necesidades que justifiquen
otro motor, se debe registrar una nueva decisión y migrar con un plan explícito
de exportación, conversión, validación, corte y recuperación.

## Consecuencias y costo de reversión

- No se altera el flujo ni se migra ningún dato existente.
- Se mantiene una única fuente duradera y las transacciones relacionales que
  respaldan las operaciones de la API.
- Para cambiar de motor habría que migrar todas las tablas y relaciones,
  preservar identificadores y registros de auditoría, adaptar cualquier
  diferencia de SQL o tipos, y ejecutar las pruebas de integración contra el
  destino. Un corte requiere detener escrituras o diseñar una sincronización
  temporal y reconciliar los datos antes de cambiar la conexión.
- También habría que revalidar copias y restauraciones, restricciones y
  comportamiento bajo concurrencia. Por eso no se cambia de motor solo para
  resolver una optimización que puede abordarse en los repositorios.
- El costo es mayor que revertir una caché porque la base contiene el estado
  duradero y está en la ruta de cada operación; un error de migración puede
  perder o alterar datos de negocio y auditoría.

## Trazabilidad

- Motor y esquema: [ADR-004](0004-usar-mysql-como-base-de-datos.md),
  [`db.py`](../../app/infrastructure/db.py) y
  [`tablas.py`](../../app/infrastructure/tablas.py).
- Proveedor y copias: [ADR-009](0009-usar-aiven-for-mysql-como-base-de-datos-gestionada.md).
- Operaciones transaccionales y pruebas: [arc42 §8.1](../arc42/arc42-uniteam.md#81-consistencia-de-los-datos),
  [`dependencias.py`](../../app/api/dependencias.py) y
  [`test_corte_vertical.py`](../../test/test_corte_vertical.py).
- Contenedor: [C4 nivel 2](../c4/nivel2-contenedores.md).
