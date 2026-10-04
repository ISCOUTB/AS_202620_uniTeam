# ADR-014 — No incorporar un componente generativo en el sistema

- **Estado:** Propuesta — pasa a *Aceptada* cuando el equipo la apruebe y anote la fecha en [D-026](../ia.md#decisiones-tomadas-por-el-equipo)
- **Fecha:** 2026-10-04
- **Decisores:** Equipo de desarrollo (I-04)
- **Escenarios:** [ESC-01](../calidad/escenarios-calidad.md#esc-01) · [ESC-03](../calidad/escenarios-calidad.md#esc-03)
- **Relacionada:** [D-011](../ia.md#decisiones-tomadas-por-el-equipo) (0 USD y sin tarjeta), [ADR-003](0003-usar-eventos-de-dominio-en-proceso.md)

## Contexto

La IA generativa se usó para **construir** UniTeam (ver [`docs/ia.md`](../ia.md)). La pregunta de este ADR
es otra: si el **sistema** incorporará un componente generativo que corra en producción (un asistente que
resuma el progreso, sugiera prioridades o redacte tareas). En la revisión del 2026-09-28 se descartó
proponerlo «por no haber escenario de calidad que lo pida».

## Decisión

**No se incorpora ningún componente generativo.** Razones, cada una contra una restricción vigente del repositorio:

1. **No hay un escenario que lo exija.** Ninguno de ESC-01 a ESC-05 pide una capacidad generativa; los aspectos A-01 a A-12 se cumplen con lógica determinista.
2. **Costo (D-011).** El límite es 0 USD al mes y cada pieza utilizable sin tarjeta. Un modelo alojado por un tercero se factura por uso, o su capa gratuita exige cuenta con tarjeta o impone cupos. *No se estimó un costo por operación porque no hay operación diseñada que estimar.*
3. **Seguridad (ESC-03, L1).** El contenido de un proyecto —títulos, responsables, fechas— es dato de un equipo. Enviarlo a un tercero abre una ruta de salida de datos que el escenario de mayor prioridad del sistema no contempla ni mide.
4. **Latencia (ESC-01).** Una llamada a un modelo externo comparte el presupuesto de 2 s del tablero. *No se midió*; es una razón de diseño, no un resultado.

## Alternativas descartadas

- **Asistente de resumen del progreso.** El resumen ya existe, calculado en SQL (A-06, ESC-01 medido). Un modelo añadiría riesgo sin valor demostrado.
- **Modelo local de código abierto.** Cumple 0 USD y evita la salida de datos, pero el despliegue gratuito de la API (Render Free) no tiene memoria ni CPU para servirlo (ADR-008).

## Condiciones para reabrirlo

Se reabre solo si aparece un **escenario de calidad** que lo requiera. Antes de aceptar cualquier componente generativo deberá existir: un conjunto de evaluación con casos y resultados, la estimación de costo por operación y la medición de latencia, y una revisión de ESC-03 sobre qué datos salen del sistema.

## Reversión

No aplica: no se construye nada.

## Trazabilidad

[`docs/ia.md`](../ia.md) · [D-011](../ia.md#decisiones-tomadas-por-el-equipo) · [ADR-008](0008-desplegar-la-api-como-contenedor-en-render.md) · [`escenarios-calidad.md`](../calidad/escenarios-calidad.md)
