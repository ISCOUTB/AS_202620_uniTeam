# ADR-006 — Mantener el modelo sincrónico con eventos en proceso

- **Estado:** Aceptada
- **Fecha:** 2026-09-18
- **Decisores:** Equipo de desarrollo (I-04)
- **Suplementa:** [ADR-003 — Estilo orientado a eventos](0003-usar-eventos-de-dominio-en-proceso.md)

## Contexto

[ADR-003](0003-usar-eventos-de-dominio-en-proceso.md) seleccionó la arquitectura orientada a eventos como estilo principal, pero especificó que el despacho es **en proceso**: no hay broker ni cola externa. Esto deja abierta la pregunta sobre si las operaciones individuales y los consumidores de eventos deben ejecutarse de forma **síncrona** o **asíncrona**.

El sistema actual opera así:

- Las operaciones del usuario (crear proyecto, crear tarea, cambiar estado, consultar progreso) son **síncronas**: el handler HTTP llama al servicio, el servicio llama al repositorio, y la respuesta vuelve al cliente antes de que termine la operación.
- Los eventos de dominio se publican **después** de que la operación se ejecutó, y los consumidores se ejecutan **síncronamente** dentro de la misma llamada (`app/application/bus.py:26-35`).
- La auditoría de acceso denegado usa una **sesión propia** con commit inmediato (`app/events/consumidores.py:26-34`), porque la petición termina en rollback y el registro se perdería si compartiera la transacción.

## Alternativas evaluadas

### A. Todo síncrono (modelo actual)

Toda operación —incluidos los consumidores de eventos— se ejecuta en el hilo de la petición HTTP antes de devolver la respuesta.

| A favor | En contra |
|---------|-----------|
| Simplicidad total: no hay concurrencia que gestionar | La latencia del consumidor se suma a la latencia de la petición |
| Fácil de depurar: el flujo es lineal | Sin paralelismo real entre consumidores |
| Compatible con infraestructura gratuita (T3) | Si un consumidor lento bloquea los hilos del servidor |
| Transacciones atómicas para operaciones y auditoría | No escala horizontalmente sin cambios |

### B. Operaciones síncronas + consumidores asíncronos (thread pool)

Las operaciones del usuario siguen siendo síncronas, pero los consumidores de eventos se ejecutan en un pool de hilos separado.

| A favor | En contra |
|---------|-----------|
| La petición responde antes de que termine la auditoría | Complejidad de concurrencia: race conditions, deadlocks |
| La auditoría no bloquea la respuesta | La pérdida de un evento se vuelve posible si el pool falla |
| Mejor uso de hilos del servidor | Requiere mecanismo de reintento o cola en memoria |
| | No hay ganancia real con un solo proceso de Uvicorn |

### C. Todo asíncrono (asyncio de FastAPI)

Toda la cadena —handler, servicio, repositorio, consumidor— usa `async/await`.

| A favor | En contra |
|---------|-----------|
| Máximo throughput con pocas conexiones | Requiere reescribir los repositorios SQLAlchemy (sincrónicos) |
| Nativo de FastAPI y de la base de datos async | El 90% del código actual no cambia de nada |
| | Complejidad de `async` con sesiones de base de datos |
| | Riesgo de bugs de concurrency con SQLAlchemy sync |

## Decisión

**Se mantiene el modelo síncrono** para todas las operaciones y consumidores, conforme al estado actual del prototipo.

### Qué se mantiene síncrono

| Componente | Justificación |
|------------|---------------|
| Handlers HTTP (`app/api/`) | La respuesta debe contener el resultado de la operación |
| Casos de uso (`app/application/`) | Transacción atómica: operación + publicación de evento |
| Repositorios (`app/infrastructure/`) | SQLAlchemy síncrono; el equipo ya lo domina |
| Consumidores de eventos (`app/events/`) | Pocos consumidores (3); la latencia añadida es despreciable |
| Auditoría de acceso denegado | Ya usa sesión propia; síncrona es consistente |

### Qué NO cambia (aún)

- El bus de eventos (`app/application/bus.py`) sigue publicando síncronamente.
- Los consumidores siguen ejecutándose en el hilo de la petición.
- No hay reintento automático ante fallos de consumidor (el fallo se loguea).

### Condiciones para revisar esta decisión

Esta decisión se reevaluará cuando se cumpla **cualquiera** de estas condiciones:

| Condición | Por qué |
|-----------|---------|
| El p95 de ESC-01 supera los 2 s **y** se identifica que el consumidor es el cuello de botella | La latencia del consumidor se suma a la respuesta |
| El número de consumidores de eventos supera 5 | El coste de fallo de cada consumidor se multiplica |
| Se despiega en múltiples workers de Uvicorn sin compartir estado | Los eventos publicados por un worker no llegan a los consumidores de otros |
| Se requiere guarantees de entrega (al menos una vez) | El modelo actual no tiene reintento ni persistencia de eventos |

### Marco de migración futura

Si alguna condición se cumple, la migración será **por consumidor**, no global:

1. Identificar el consumidor que necesita ser asíncrono.
2. Mover su lógica a un hilo del pool (`concurrent.futures.ThreadPoolExecutor`).
3. Mantener el resto de consumidores síncronos.
4. Verificar que ESC-03 (auditoría) no pierde registros.
5. Medir ESC-01 antes y después.

## Consecuencias

### Positivas

- **Simplicidad**: el código es lineal y fácil de entender para un equipo de dedicación parcial (O1).
- **Predecibilidad**: la latencia de respuesta es la suma conocida de las operaciones; no hay surprise de ejecución asíncrona.
- **Consistencia**: las operaciones y su auditoría comparten transacción; no hay ventana donde la operación se confirma pero la auditoría falla (para operaciones permitidas).
- **Compatible con ESC-03**: la auditoría de acceso denegado persiste antes de que la petición termine, porque el consumidor corre antes del rollback.

### Negativas

- **Latencia acumulada**: si un consumidor es lento, la respuesta al usuario tarda más. Hoy el único consumidor es auditoría, que es rápido.
- **Sin paralelismo**: si hay múltiples consumidores, cada uno se ejecuta secuencialmente.
- **No escala a múltiples workers**: los eventos publicados por una instancia solo son consumidos por la misma instancia.

## Trazabilidad

| Eslabón | Dónde |
|---------|-------|
| Escenario de calidad | [ESC-01](../calidad/escenarios-calidad.md#esc-01) — condición de reevaluación |
| Escenario de calidad | [ESC-04](../calidad/escenarios-calidad.md#esc-04) — un consumidor falla no tumba la petición |
| ADR | [ADR-003](0003-usar-eventos-de-dominio-en-proceso.md) — EDA en proceso |
| Código | `app/application/bus.py` — publicación síncrona |
| Código | `app/events/consumidores.py` — consumidores síncronos |
| Código | `app/events/bus.py` — despacho en proceso |
| Pruebas | `test/test_corte_vertical.py` — verifica que la auditoría persiste |
