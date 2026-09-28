# ADR-011 — Mantener la API despierta con un sondeo externo

- **Estado:** Aceptada
- **Fecha:** 2026-09-28
- **Decisores:** Equipo de desarrollo (I-04)
- **Pieza:** API — contenedor «API» del [C4 nivel 2](../c4/nivel2-contenedores.md)
- **Reemplaza en parte:** [ADR-008](0008-desplegar-la-api-como-contenedor-en-render.md), en su consecuencia «se descartó mantener la instancia despierta con peticiones periódicas». El resto del ADR-008 sigue vigente.

## Contexto

La API corre en el plan gratuito de Render, que la duerme tras 15 minutos sin tráfico y tarda
alrededor de un minuto en despertarla ([ADR-008](0008-desplegar-la-api-como-contenedor-en-render.md)).
Con el sistema ya desplegado y en uso, eso deja de ser teórico: la primera persona que abre
UniTeam tras un rato de inactividad espera un minuto, y [ESC-01](../calidad/escenarios-calidad.md#esc-01)
—tablero en ≤ 2 s en el p95— se incumple justo en la primera impresión. Además, la base de datos
gratuita de Aiven se apaga si pasa demasiado tiempo sin conexiones
([ADR-009](0009-usar-aiven-for-mysql-como-base-de-datos-gestionada.md)).

Al redactar el ADR-008 el equipo descartó mantener la API despierta con peticiones periódicas.
Con el sistema en uso real, el equipo revisa esa decisión.

## Alternativas

| | A. Sondeo externo a `/health` (**elegida**) | B. Plan Starter de Render | C. Aceptar el arranque en frío (decisión anterior) |
|---|---|---|---|
| Qué es | Un servicio de cron gratuito (cron-job.org) consulta `GET /health` con la frecuencia que se configure | Instancia de pago que no se duerme | No hacer nada |
| ESC-01 en la primera visita | Se cumple dentro de la franja sondeada | Se cumple siempre | No se cumple |
| Base de datos | `/health` hace `SELECT 1`: Aiven tampoco se apaga | Hace falta otra solución | Puede apagarse |
| Costo | 0 USD | 7 USD/mes | 0 USD |
| Tarjeta | No | Sí | No |

**Por qué se descarta B.** Viola la restricción T5: 0 USD y sin tarjeta.
**Por qué se descarta C.** Deja la peor experiencia justo en la primera visita del día, que es la
que decide si el equipo sigue usando la herramienta. Es lo que [ESC-02](../calidad/escenarios-calidad.md#esc-02)
y ESC-01 intentan proteger.

## Decisión

Un trabajo en **cron-job.org** consulta `https://uniteam-api.onrender.com/health` **cada
minuto**. Se consulta `/health` y no `/activo` porque `/health` también toca la base de datos, y
así mantiene despierto a Aiven.

**Franja recomendada: de 06:00 a 23:59, hora de Colombia.** No por la frecuencia —despierta es
despierta, sondee cada minuto o cada diez—, sino por las horas de instancia:

| Configuración | Horas al mes (31 días) | Margen sobre las 750 h gratuitas |
|---------------|------------------------|----------------------------------|
| Las 24 h | 744 h | **6 h**, que se van en los solapes de los despliegues |
| 06:00–23:59 | ~560 h, más las colas de 15 min tras cada sondeo | ~180 h |

Con el sondeo 24 h, **si la API agotara las 750 h, Render la suspendería hasta el mes
siguiente**. Eso es mucho peor que un arranque en frío. La franja elimina ese riesgo sin perder
nada: fuera de ella no hay usuarios.

## Consecuencias

- **ESC-01 se cumple en la primera visita** dentro de la franja. La métrica `/metricas/esc-01`
  no mezcla los sondeos: solo cuenta las consultas del tablero.
- **Registro limpio.** Un sondeo por minuto son 1 440 peticiones al día. Las respuestas
  correctas de `/health` y `/activo` ya no se escriben a nivel INFO (`app/observabilidad.py`),
  aunque siguen contando en `/metricas`.
- **Dependencia de un tercero más** (cron-job.org). Si falla, se vuelve a la situación del
  ADR-008: arranque en frío, sin pérdida de datos ni de funcionalidad.
- **Condiciones de uso.** El plan gratuito de Render existe para proyectos que se duermen. Un
  sondeo permanente va contra el espíritu de ese plan, aunque el equipo no encontró una
  prohibición expresa. Es otra razón para limitarlo a la franja de uso real.
- **Costo:** sigue en 0 USD. Actualizado en la [estimación de costo](../despliegue/costos.md).

## Reversión

Desactivar el trabajo en cron-job.org. Efecto inmediato, sin tocar el código ni el despliegue.

## Trazabilidad

[`app/main.py`](../../app/main.py) (`/health`) · [`app/observabilidad.py`](../../app/observabilidad.py) ·
[guía de despliegue](../despliegue/guia.md#mantener-la-api-despierta) · [ESC-01](../calidad/escenarios-calidad.md#esc-01)
