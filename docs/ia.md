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
| D-001 | 2026-08-16 | Acotar el stack a **NestJS o FastAPI** en backend y **Flutter o Next.js** en frontend. Ninguna otra tecnología entra en consideración. | Equipo | Restricción T1 en [arc42 §2.1](arc42/arc42-uniteam.md#21-restricciones-técnicas), [0001-acotar-el-stack-a-cuatro-opciones.md) |
| D-002 | 2026-08-16 | **No se desarrollará aplicación móvil.** El prototipo se entrega para navegador web y/o escritorio, y la elección del frontend queda condicionada por eso. | Equipo | Restricción T2 en [arc42 §2.1](arc42/arc42-uniteam.md#21-restricciones-técnicas), sección «Fuera del alcance» del [C4 nivel 1](c4/nivel1-contexto.md) |
| D-003 | 2026-08-16 | Hacer **obligatorio** el registro en este documento de todo uso de IA generativa, de los cambios en la aplicación y de las decisiones del equipo. | Equipo | Este documento; restricción O4 en [arc42 §2.2](arc42/arc42-uniteam.md#22-restricciones-organizativas) |
| D-007 | 2026-08-29 | **Mantener el estilo orientado a eventos** pese a la objeción de la IA, que señaló que la matriz de decisión daba ganador al monolito modular. Se precisa que el despacho es **en proceso**, sin broker. | Equipo | [ADR 0003](adr/0003-usar-eventos-de-dominio-en-proceso.md), [C4 nivel 2](c4/nivel2-contenedores.md), [arc42 §5.2](arc42/arc42-uniteam.md#52-nivel-2--caja-blanca-de-la-api) |
| D-006 | 2026-08-29 | **La persistencia soportada es MySQL.** SQLite queda únicamente como valor por defecto de las pruebas locales, no como entorno de ejecución. | Equipo | [ADR 0004](adr/0004-usar-mysql-como-base-de-datos.md), [`ci.yml`](../.github/workflows/ci.yml) |
| D-005 | 2026-08-29 | **Usar MySQL** como base de datos del prototipo. | Equipo | [ADR 0004](adr/0004-usar-mysql-como-base-de-datos.md), [C4 nivel 2](c4/nivel2-contenedores.md) |
| D-004 | 2026-08-16 | Aprobar la priorización del árbol de utilidad: seguridad primero, luego rendimiento y usabilidad; disponibilidad y modificabilidad como metas secundarias. Con ella, aceptar las renuncias explícitas —sin alta disponibilidad, permisos por proyecto y no por tarea, y metas de rendimiento acotadas a 200 tareas y 30 usuarios concurrentes—. | Equipo | [Árbol de utilidad](calidad/arbol-utilidad.md), [arc42 §1.2](arc42/arc42-uniteam.md#12-metas-de-calidad) |

## Bitácora de uso de IA

La columna de lo **rechazado con su motivo** es la que da cuenta del criterio del equipo: la IA
propone más de lo que se acepta.

| Fecha | Entrega / actividad | Herramienta | Qué se pidió | Qué se aceptó | Qué se rechazó y por qué |
|-------|--------------------|------------|-------------|---------------|--------------------------|
| Semana 1 | Ideación y documentación inicial | ChatGPT, Claude | Explorar ideas, definir el alcance de UniTeam y estructurar la documentación inicial. | Borradores de la ficha del problema, los aspectos declarados y el README. | Definió la idea del proyecto, seleccionó el alcance y revisó los textos antes de publicarlos. |
| 2026-08-16 | Entrega S2 — Interesados y escenarios de calidad | Claude (Claude Code) | Redactar los borradores de arc42 §1–3 y §10, el mapa de interesados, cinco escenarios de seis partes, el árbol de utilidad, las restricciones y el C4 de contexto. | Los documentos de la entrega, tras revisar el equipo la priorización y las medidas numéricas (D-004). | Se rechazó incluir el PDF de resumen en el repositorio: es material de entrega para el docente, no documentación del sistema. Quedó en `.gitignore`. |
| 2026-08-29 | Entrega S4 — Corte vertical | Claude (Claude Code) | Implementar el recorrido interfaz-lógica-persistencia sobre MySQL, con prueba de punta a punta, arranque de un comando y CI; redactar arc42 §5 y §6; completar la tabla de aspectos. | El código de `app/`, las pruebas de `test/`, `compose.yaml`, el workflow de CI, el ADR 0004, el C4 nivel 2 y las secciones 5 y 6 de arc42. | **Se rechazó la propuesta de sustituir el estilo orientado a eventos por un monolito modular.** La IA argumentó que la matriz de decisión daba ganador al monolito y que EDA no se sigue de esa evaluación; el equipo mantiene la decisión y precisa que el despacho es en proceso (D-007). **Se rechazó dejar SQLite como motor de ejecución**, que la IA había puesto por defecto: solo se acepta para pruebas locales (D-006). |
| Semana 3 | Esqueleto ejecutable y preparación del repositorio | ChatGPT, Claude (Claude Code) | Aportar ideas y orientación para estructurar el esqueleto ejecutable, configurar el arranque del backend, definir una ruta mínima de comprobación, preparar la prueba automatizada y organizar las instrucciones de ejecución en el README. | Sugerencias sobre la estructura mínima del esqueleto, comandos de arranque con FastAPI/Uvicorn, ejemplos para la ruta de comprobación, orientación para la prueba automatizada y correcciones sobre la documentación de ejecución. | El equipo implementó y verificó el esqueleto ejecutable, revisó y corrigió las propuestas de las herramientas, comprobó el arranque del backend y ajustó el README con las instrucciones correspondientes antes de incorporarlas al repositorio. |

## Bitácora de cambios en la aplicación

| Fecha | Cambio | Componente | Decisión que lo respalda | ¿Asistencia de IA? |
|-------|--------|-----------|-------------------------|--------------------|
| 2026-08-23 | Esqueleto ejecutable con un endpoint y su prueba en verde. | `app/main.py` | [ADR 0002](adr/0002-usar-fastapi-y-nextjs.md) | Sí |
| 2026-08-29 | Corte vertical: proyectos y tareas con autorización por pertenencia, flujo de estados y auditoría. | `app/domain/`, `app/application/`, `app/api/` | [ADR 0003](adr/0003-usar-eventos-de-dominio-en-proceso.md) | Sí, revisado por el equipo |
| 2026-08-29 | Persistencia en MySQL mediante SQLAlchemy. | `app/infrastructure/` | [ADR 0004](adr/0004-usar-mysql-como-base-de-datos.md) | Sí, revisado por el equipo |
| 2026-08-29 | Arranque con un comando (`docker compose up`) e integración continua contra MySQL. | `compose.yaml`, `Dockerfile`, `.github/workflows/ci.yml` | [ADR 0004](adr/0004-usar-mysql-como-base-de-datos.md) | Sí |
| 2026-08-29 | Corrección: la auditoría del acceso denegado se perdía en el *rollback* de la petición, y la de las operaciones permitidas fallaba en silencio por contención de bloqueo. | `app/events/consumidores.py` | [ESC-03](calidad/escenarios-calidad.md#esc-03) | Detectado al ejecutar las pruebas contra MySQL |
| 2026-08-29 | Corrección: soporte para Python 3.14 (PEP 649) y tipo correcto en `fecha_limite`. | `requirements.txt`, `app/infrastructure/tablas.py` | — | Detectado por un integrante al ejecutar las pruebas |
