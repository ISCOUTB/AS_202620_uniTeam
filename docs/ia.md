# Inteligencia Artificial

Este documento registra el uso de herramientas de inteligencia artificial generativa durante
el desarrollo de UniTeam, y deja constancia de qué decisiones tomó el equipo.

## Política del equipo

1. **Las decisiones las toma el equipo.** La IA propone, redacta borradores y acelera trabajo
   mecánico; no decide. Toda decisión de alcance, arquitectura o tecnología se registra en la
   sección [Decisiones tomadas por el equipo](#decisiones-tomadas-por-el-equipo) con la fecha
   en que se tomó.
2. **Todo uso de IA se registra.** Cada vez que se usa IA generativa para producir algo que
   entra al repositorio, se anota en la [bitácora de uso de IA](#bitácora-de-uso-de-ia): qué
   se pidió, qué produjo la herramienta y qué revisó o cambió el equipo.
3. **Nada entra sin revisión.** Ningún contenido generado con IA se incorpora al repositorio
   sin que un integrante lo revise y lo apruebe explícitamente.
4. **Todo cambio en la aplicación se registra.** Los cambios funcionales del prototipo se
   anotan en la [bitácora de cambios](#bitácora-de-cambios-en-la-aplicación), indicando si
   hubo asistencia de IA.

Esta política corresponde a la restricción **O4** de
[arc42 §2.2](arc42/arc42-uniteam.md#22-restricciones-organizativas).

## Herramientas utilizadas

| Herramienta | Uso |
|------------|-----|
| ChatGPT | Ideación, análisis y exploración del problema. |
| Claude (Claude Code) | Redacción de borradores de documentación, análisis, revisión y asistencia en desarrollo. |

## Decisiones tomadas por el equipo

Decisiones del equipo, no de la IA. Cada una precede o corrige lo que las herramientas
propusieron.

| ID | Fecha | Decisión | Tomada por | Dónde se refleja |
|----|-------|----------|-----------|------------------|
| D-001 | 2026-08-16 | Acotar el stack a **NestJS o FastAPI** en backend y **Flutter o Next.js** en frontend. Ninguna otra tecnología entra en consideración. | Equipo | Restricción T1 en [arc42 §2.1](arc42/arc42-uniteam.md#21-restricciones-técnicas), [ADR-001](adr/ADR-001-seleccion-de-stack.md) |
| D-002 | 2026-08-16 | **No se desarrollará aplicación móvil.** El prototipo se entrega para navegador web y/o escritorio, y la elección del frontend queda condicionada por eso. | Equipo | Restricción T2 en [arc42 §2.1](arc42/arc42-uniteam.md#21-restricciones-técnicas), sección «Fuera del alcance» del [C4 nivel 1](c4/nivel1-contexto.md) |
| D-003 | 2026-08-16 | Hacer **obligatorio** el registro en este documento de todo uso de IA generativa, de los cambios en la aplicación y de las decisiones del equipo. | Equipo | Este documento; restricción O4 en [arc42 §2.2](arc42/arc42-uniteam.md#22-restricciones-organizativas) |
| D-004 | 2026-08-16 | Aprobar la priorización del árbol de utilidad: seguridad primero, luego rendimiento y usabilidad; disponibilidad y modificabilidad como metas secundarias. Con ella, aceptar las renuncias explícitas —sin alta disponibilidad, permisos por proyecto y no por tarea, y metas de rendimiento acotadas a 200 tareas y 30 usuarios concurrentes—. | Equipo | [Árbol de utilidad](calidad/arbol-utilidad.md), [arc42 §1.2](arc42/arc42-uniteam.md#12-metas-de-calidad) |

## Bitácora de uso de IA

| Fecha | Entrega / actividad | Herramienta | Qué se pidió | Qué produjo la herramienta | Qué hizo el equipo |
|-------|--------------------|------------|-------------|---------------------------|--------------------|
| Semana 1 | Ideación y documentación inicial | ChatGPT, Claude | Explorar ideas, definir el alcance de UniTeam y estructurar la documentación inicial. | Borradores de la ficha del problema, los aspectos declarados y el README. | Definió la idea del proyecto, seleccionó el alcance y revisó los textos antes de publicarlos. |
| 2026-08-16 | Entrega S2 — Interesados y escenarios de calidad | Claude (Claude Code) | Redactar los borradores de arc42 §1–3 y §10, el mapa de interesados, cinco escenarios de calidad de seis partes, el árbol de utilidad, la lista de restricciones y el C4 de contexto, partiendo de la ficha, los aspectos declarados y las decisiones D-001 a D-004. | Los documentos de la entrega S2 con sus enlaces cruzados y los diagramas en Mermaid. | Aportó las decisiones de entrada (D-001, D-002), fijó la política de registro (D-003), revisó la priorización y las medidas numéricas de los escenarios, y aprobó el contenido antes de incorporarlo al repositorio (D-004). |
| Semana 3 | Esqueleto ejecutable y preparación del repositorio | ChatGPT, Claude (Claude Code) | Aportar ideas y orientación para estructurar el esqueleto ejecutable, configurar el arranque del backend, definir una ruta mínima de comprobación, preparar la prueba automatizada y organizar las instrucciones de ejecución en el README. | Sugerencias sobre la estructura mínima del esqueleto, comandos de arranque con FastAPI/Uvicorn, ejemplos para la ruta de comprobación, orientación para la prueba automatizada y correcciones sobre la documentación de ejecución. | El equipo implementó y verificó el esqueleto ejecutable, revisó y corrigió las propuestas de las herramientas, comprobó el arranque del backend y ajustó el README con las instrucciones correspondientes antes de incorporarlas al repositorio. |

## Bitácora de cambios en la aplicación

Aún no hay código del prototipo: el trabajo de las primeras semanas es de análisis y
arquitectura. Los cambios funcionales se registrarán aquí con este formato:

| Fecha | Cambio | Componente | Decisión que lo respalda | ¿Asistencia de IA? |
|-------|--------|-----------|-------------------------|--------------------|
| — | — | — | — | — |
