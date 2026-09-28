# ADR-012 — Publicar el flujo de estados desde el dominio

- **Estado:** Aceptada
- **Fecha:** 2026-09-28
- **Decisores:** Equipo de desarrollo (I-04)
- **Escenario:** [ESC-05 — Modificabilidad: extensión del flujo de estados](../calidad/escenarios-calidad.md#esc-05)
- **Relacionada:** [ADR-003](0003-usar-eventos-de-dominio-en-proceso.md), [ADR-006](0006-estilo-sincrono-con-eventos-en-proceso.md)

## Contexto

ESC-05 compromete que añadir un estado de tarea —«En revisión»— toque **como mucho 2
componentes**, cueste **como mucho un día-persona**, no rompa la API y deje la suite en verde.

El dominio ya concentraba las transiciones en una sola tabla (`TRANSICIONES`). Pero la
Aplicación Web las **copiaba**: el tipo de los estados, la tabla de transiciones, las etiquetas,
el orden de las columnas y los colores estaban escritos a mano en seis lugares de
`web/`. Antes de este cambio, añadir un estado exigía tocar el dominio, el cliente de la API, el
tablero, la tarjeta y la hoja de estilos: **dos contenedores y cinco archivos**, con el riesgo
añadido de que las dos copias divergieran sin que ninguna prueba lo detectara.

## Alternativas

| | A. La API publica el flujo (**elegida**) | B. Generar el cliente desde el contrato OpenAPI | C. Mantener la copia en el frontend |
|---|---|---|---|
| Qué es | `GET /flujo-estados` devuelve estados, etiquetas, orden, inicial, final y transiciones; la Aplicación Web lo consume | Un generador produce los tipos de TypeScript a partir de `openapi.yaml` | Nada cambia |
| Añadir un estado | Solo el dominio | Dominio, contrato y regenerar el cliente: sigue tocando el frontend | Dominio y cinco archivos del frontend |
| Divergencia entre copias | Imposible: hay una sola | Detectable al regenerar | Silenciosa |
| Costo | Un endpoint y un módulo en el cliente | Una herramienta más en la cadena de construcción | Ninguno |

**Por qué se descarta B.** Evita la divergencia de *tipos*, pero no la de *comportamiento*:
etiquetas, orden y colores seguirían escritos en el frontend. Y añade una dependencia de
construcción para un problema que un endpoint resuelve.
**Por qué se descarta C.** Es la situación que incumple ESC-05.

## Decisión

El dominio declara el flujo completo en un solo bloque de `app/domain/modelos.py`:
`EstadoTarea` (cuyo orden es el de las columnas), `TRANSICIONES`, `ETIQUETAS_ESTADO`,
`ESTADO_INICIAL` y `ESTADO_FINAL`. La API lo publica en `GET /flujo-estados`, sin credencial
porque no contiene datos de nadie. La Aplicación Web lo lee una vez por carga
(`web/lib/flujo.ts`) y dibuja columnas, etiquetas, flechas y colores a partir de él.

Es la táctica de modificabilidad que Bass, Clements y Kazman llaman **aplazar la vinculación**:
qué estados existen se decide en tiempo de ejecución, no al compilar el frontend.

**Guardia.** `test_la_aplicacion_web_no_escribe_estados_a_mano`
([`test/test_flujo_estados.py`](../../test/test_flujo_estados.py)) recorre `web/app` y
`web/lib` y falla si aparece cualquier identificador de estado. Antes de este cambio encontraba
14 apariciones; ahora, ninguna. Si alguien vuelve a copiar el flujo, la CI se pone en rojo.

## Consecuencias

- **Añadir un estado debería tocar un solo componente**, el dominio de la API, más su contrato
  y sus pruebas. Se comprueba al ejecutar el estímulo de ESC-05 en un commit aparte, cuya
  medición se enlaza desde el [propio escenario](../calidad/escenarios-calidad.md#esc-05).
- Una petición más al abrir un tablero, sin credencial y sin base de datos: no afecta a la
  latencia de ESC-01, que mide la consulta de tareas.
- El número de columnas del tablero depende de los datos. La hoja de estilos lo resuelve con una
  variable (`--columnas`) y desplazamiento horizontal si no caben.
- Los colores por estado son por **tipo** —inicial, intermedio, final—, no por nombre. Un estado
  nuevo recibe el color de los intermedios sin configurar nada.

## Reversión

Volver a escribir el flujo en `web/lib/api.ts`. No hay datos que migrar: el endpoint es de solo
lectura.

## Trazabilidad

[`app/domain/modelos.py`](../../app/domain/modelos.py) · [`app/api/rutas_flujo.py`](../../app/api/rutas_flujo.py) ·
[`web/lib/flujo.ts`](../../web/lib/flujo.ts) · [`test/test_flujo_estados.py`](../../test/test_flujo_estados.py) ·
[ESC-05](../calidad/escenarios-calidad.md#esc-05)
