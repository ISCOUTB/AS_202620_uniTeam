# ADR-015 — Mantener aislado el simulador de mensajeria del taller

- **Estado:** Aceptada para el taller; no incorporar a la aplicacion
- **Fecha:** 2026-10-25
- **Decisores:** Equipo de desarrollo
- **Relacionada:** [ADR-003](0003-usar-eventos-de-dominio-en-proceso.md), [ADR-006](0006-estilo-sincrono-con-eventos-en-proceso.md)

## Contexto

La creacion de una tarea publica `TareaCreada`. Su consumidor actual registra la
auditoria permitida en la misma sesion y transaccion que persiste la tarea. La
operacion de auditoria es real, pero no es candidata a procesamiento asincrono:
responder antes de confirmar esa auditoria abriria una ventana en la que una
tarea podria existir sin su registro requerido. El bus actual tampoco reintenta.

El envio de notificaciones cuando se crea una tarea seria un efecto secundario
razonable para desacoplar temporalmente, pero UniTeam no tiene actualmente un
servicio de notificaciones que justifique incorporarlo. Por ello, este ADR
registra la decision de **no cambiar el flujo de produccion** y construir un
simulador ejecutable, sin dependencias nuevas, que usa el evento `tarea.creada`
como contrato del ejercicio.

## Alternativas

| Alternativa | Ventajas | Costos y limites |
|---|---|---|
| Operacion y consumidor sincronos (actual) | La respuesta espera la persistencia y auditoria; el flujo y la transaccion son sencillos. | La latencia del consumidor se suma a la peticion; el bus actual no reintenta. |
| Cola durable con consumidor asincrono | Desacopla la latencia y permite reintentos, deduplicacion y cola de fallidos. | Consistencia eventual, operacion y monitoreo adicionales; el productor necesita entrega fiable. |
| Simulador SQLite aislado (elegido para este taller) | Permite comprobar contrato, persistencia, backoff, deduplicacion y DLQ localmente, sin tocar la aplicacion ni desplegar un broker. | No es una cola distribuida: admite un consumidor, no resuelve la transaccion tarea-publicacion y no se debe usar para efectos externos. |

## Decision

El taller se implementa en `scripts/taller_mensajeria.py`, y no se integra al
bus, a los servicios, a los consumidores de auditoria ni al despliegue. Simula
una posible notificacion posterior a `TareaCreada`; la auditoria de la tarea y
los intentos de acceso denegado permanecen sincronos.

### Contrato y compatibilidad

El sobre JSON incluye `schema_version`, `message_id`, `event_type`,
`occurred_at`, `correlation_id` y `payload`. La version 1 exige
`event_type=tarea.creada` y `payload.tarea_id`, `proyecto_id` y `creada_por`.
Los consumidores rechazan versiones futuras, tipos de evento desconocidos,
campos obligatorios ausentes y marcas de tiempo sin zona horaria. Se toleran
campos adicionales opcionales; cambiar el significado o retirar un campo
obligatorio requiere una version nueva.

### Entrega, deduplicacion y fallidos

- SQLite conserva los mensajes pendientes, los recibos del consumidor y los
  mensajes fallidos entre instancias si se usa un archivo.
- La entrega se considera **al menos una vez mientras haya intentos disponibles**.
  Despues de tres fallos por defecto, el mensaje pasa a la tabla de fallidos:
  no se promete entrega eventual ni se reintenta automaticamente desde la DLQ.
- El backoff exponencial es `demora_base * 2^(intento-1)`, configurable. El
  simulador usa un reloj inyectable, de modo que las pruebas no esperan.
- `message_id` es la clave de idempotencia del consumidor. El recibo, el efecto
  local de demostracion y el acuse se confirman en la misma transaccion SQLite:
  repetir el evento no duplica la notificacion. Esto solo cubre efectos en esa
  base; un efecto externo no transaccional puede repetirse y debe aceptar una
  clave idempotente propia.
- Los logs registran `message_id`, `correlation_id`, evento, intento y
  proximo reintento. Contadores Prometheus locales registran publicaciones,
  procesamientos, duplicados, reintentos y mensajes fallidos.

SQLite serializa este simulador de un solo consumidor. Un cierre del proceso
durante el efecto local revierte juntos el efecto y el acuse; un cierre despues
del commit conserva ambos. No existe una transaccion atomica entre la base de
datos real de tareas y esta cola: esa brecha impide afirmar que el prototipo es
un outbox de produccion. El efecto no debe incluir una llamada de red dentro de
la transaccion SQLite.

## Consecuencias

- Se verifican duplicados, fallo recuperable, backoff y agotamiento de intentos
  mediante pruebas automatizadas locales.
- No se agregan broker, contenedores, variables de despliegue ni cambios en la
  API.
- Si se incorporan notificaciones reales, reevaluar esta decision y disenar un
  outbox atomico con la creacion de la tarea, un consumidor operable y una
  estrategia de idempotencia para el proveedor externo.

## Ejecucion

Desde la raiz del proyecto:

```powershell
python -m scripts.taller_mensajeria --base-datos taller-mensajeria.db
python -m pytest test/test_taller_mensajeria.py -q
```

La base SQLite del ejemplo es local y esta ignorada por Git (`*.db`). Para
repetir el ejemplo sin conservar estado, omitir `--base-datos`.
