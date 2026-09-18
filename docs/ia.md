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
| D-001 | 2026-08-16 | Acotar el stack a **NestJS o FastAPI** en backend y **Flutter o Next.js** en frontend. Ninguna otra tecnología entra en consideración. | Equipo | Restricción T1 en [arc42 §2.1](arc42/arc42-uniteam.md#21-restricciones-técnicas), [ADR 0001](adr/0001-acotar-el-stack-a-cuatro-opciones.md) |
| D-002 | 2026-08-16 | **No se desarrollará aplicación móvil.** El prototipo se entrega para navegador web y/o escritorio, y la elección del frontend queda condicionada por eso. | Equipo | Restricción T2 en [arc42 §2.1](arc42/arc42-uniteam.md#21-restricciones-técnicas), sección «Fuera del alcance» del [C4 nivel 1](c4/nivel1-contexto.md) |
| D-003 | 2026-08-16 | Hacer **obligatorio** el registro en este documento de todo uso de IA generativa, de los cambios en la aplicación y de las decisiones del equipo. | Equipo | Este documento; restricción O4 en [arc42 §2.2](arc42/arc42-uniteam.md#22-restricciones-organizativas) |
| D-009 | 2026-09-13 | **Someter el repositorio a análisis estático de seguridad y triar cada hallazgo por escrito.** Se corrige lo que es un defecto y se deja constancia razonada de lo que se acepta o se descarta como falso positivo; ningún hallazgo se cierra en silencio. Se acepta como consecuencia el coste de mantener un cierre de dependencias con huella en el backend. | Equipo | [Triaje de análisis estático](calidad/analisis-estatico.md), [`requirements.lock.txt`](../requirements.lock.txt), trabajo `cierre` de [`ci.yml`](../.github/workflows/ci.yml) |
| D-008 | 2026-08-29 | **Eliminar la cabecera `X-Usuario`** y delegar la autenticación en un proveedor OIDC. Se acepta la dependencia de un tercero a cambio de no almacenar contraseñas. | Equipo | [ADR 0005](adr/0005-delegar-la-autenticacion-en-un-proveedor-oidc.md) |
| D-007 | 2026-08-29 | **Mantener el estilo orientado a eventos** pese a la objeción de la IA, que señaló que la matriz de decisión daba ganador al monolito modular. Se precisa que el despacho es **en proceso**, sin broker. | Equipo | [ADR 0003](adr/0003-usar-eventos-de-dominio-en-proceso.md), [C4 nivel 2](c4/nivel2-contenedores.md), [arc42 §5.2](arc42/arc42-uniteam.md#52-nivel-2--caja-blanca-de-la-api) |
| D-006 | 2026-08-29 | **La persistencia soportada es MySQL.** SQLite queda únicamente como valor por defecto de las pruebas locales, no como entorno de ejecución. | Equipo | [ADR 0004](adr/0004-usar-mysql-como-base-de-datos.md), [`ci.yml`](../.github/workflows/ci.yml) |
| D-005 | 2026-08-29 | **Usar MySQL** como base de datos del prototipo. | Equipo | [ADR 0004](adr/0004-usar-mysql-como-base-de-datos.md), [C4 nivel 2](c4/nivel2-contenedores.md) |
| D-004 | 2026-08-16 | Aprobar la priorización del árbol de utilidad: seguridad primero, luego rendimiento y usabilidad; disponibilidad y modificabilidad como metas secundarias. Con ella, aceptar las renuncias explícitas —sin alta disponibilidad, permisos por proyecto y no por tarea, y metas de rendimiento acotadas a 200 tareas y 30 usuarios concurrentes—. | Equipo | [Árbol de utilidad](calidad/arbol-utilidad.md), [arc42 §1.2](arc42/arc42-uniteam.md#12-metas-de-calidad) |
| D-010 | 2026-09-18 | Mantener el modelo sincrónico para operaciones y consumidores de eventos. Documentar en ADR-006 las condiciones que activarían una migración a consumidores asíncronos. | Equipo | [ADR 0006](adr/0006-estilo-sincrono-con-eventos-en-proceso.md) |

## Bitácora de uso de IA

La columna de lo **rechazado con su motivo** es la que da cuenta del criterio del equipo: la IA
propone más de lo que se acepta.

| Fecha | Entrega / actividad | Herramienta | Qué se pidió | Qué se aceptó | Qué se rechazó y por qué |
|-------|--------------------|------------|-------------|---------------|--------------------------|
| Semana 1 | Ideación y documentación inicial | ChatGPT, Claude | Explorar ideas, definir el alcance de UniTeam y estructurar la documentación inicial. | Borradores de la ficha del problema, los aspectos declarados y el README. | Definió la idea del proyecto, seleccionó el alcance y revisó los textos antes de publicarlos. |
| 2026-08-16 | Entrega S2 — Interesados y escenarios de calidad | Claude (Claude Code) | Redactar los borradores de arc42 §1–3 y §10, el mapa de interesados, cinco escenarios de seis partes, el árbol de utilidad, las restricciones y el C4 de contexto. | Los documentos de la entrega, tras revisar el equipo la priorización y las medidas numéricas (D-004). | Se rechazó incluir el PDF de resumen en el repositorio: es material de entrega para el docente, no documentación del sistema. Quedó en `.gitignore`. |
| 2026-08-29 | Entrega S4 — Corte vertical | Claude (Claude Code) | Implementar el recorrido interfaz-lógica-persistencia sobre MySQL, con prueba de punta a punta, arranque de un comando y CI; redactar arc42 §5 y §6; completar la tabla de aspectos. | El código de `app/`, las pruebas de `test/`, `compose.yaml`, el workflow de CI, el ADR 0004, el C4 nivel 2 y las secciones 5 y 6 de arc42. | **Se rechazó la propuesta de sustituir el estilo orientado a eventos por un monolito modular.** La IA argumentó que la matriz de decisión daba ganador al monolito y que EDA no se sigue de esa evaluación; el equipo mantiene la decisión y precisa que el despacho es en proceso (D-007). **Se rechazó dejar SQLite como motor de ejecución**, que la IA había puesto por defecto: solo se acepta para pruebas locales (D-006). |
| 2026-09-13 | Triaje de los hallazgos de SonarCloud | Claude (Claude Code) | Analizar los hallazgos de seguridad que reportó SonarCloud sobre el repositorio y proponer qué hacer con cada uno. | Las correcciones de los campos opcionales del esquema, el paso a `npm ci --ignore-scripts`, el cierre de dependencias con huella del backend, la comprobación de esquema de URL en el descubrimiento OIDC y la prueba que la cubre. | **Se rechazó tratar las credenciales de `compose.yaml` como un defecto a ocultar.** La herramienta las marca como credenciales incrustadas; son las de un contenedor local que se destruye al terminar y esconderlas en un `.env` rompería el arranque de un comando sin reducir ningún riesgo. Se aceptan por escrito, con la condición de revisarlo si llega a haber despliegue. **Se rechazó también el veredicto de SSRF sobre los scripts de desarrollo**, cuya URL la escribe quien ejecuta el proceso; se añadió la comprobación de esquema igualmente, por barata. |
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
| 2026-08-29 | Listado de proyectos propios, detalle y gestión de miembros con rol de líder. | `app/application/servicio_proyectos.py`, `app/api/rutas_proyectos.py` | [ESC-03](calidad/escenarios-calidad.md#esc-03) | Sí, revisado por el equipo |
| 2026-08-29 | Tablero con filtros y paginación, y resumen de progreso calculado en SQL. | `app/api/rutas_progreso.py`, `app/infrastructure/repositorios.py` | [arc42 §4.3](arc42/arc42-uniteam.md#43-tácticas-arquitectónicas) | Sí, revisado por el equipo |
| 2026-08-29 | Instrumento de medición de ESC-01 y primera línea base del proyecto: p95 de 762 ms frente al umbral de 2 s. | `scripts/medir_esc01.py`, `scripts/token_dev.py`, `docs/calidad/mediciones/` | [ESC-01](calidad/escenarios-calidad.md#esc-01) | Sí, revisado por el equipo |
| 2026-08-29 | Corrección de la tabla de aspectos: afirmaba que ESC-04 y ESC-05 tenían prueba automatizada asociada cuando las pruebas enlazadas cubren otra cosa. | `docs/aspectos.md` | — | Detectado al contrastar la tabla contra las pruebas reales |
| 2026-08-29 | Autenticación con OpenID Connect: flujo de código con PKCE en el navegador y verificación del token contra el JWKS en la API. Se elimina la cabecera `X-Usuario`. | `app/api/seguridad.py`, `web/lib/oidc.ts`, `scripts/emisor_dev.py` | [ADR 0005](adr/0005-delegar-la-autenticacion-en-un-proveedor-oidc.md) | Sí, revisado por el equipo |
| 2026-08-29 | Corrección: la lista de CORS seguía permitiendo `X-Usuario` en vez de `Authorization`, y el navegador no podía llamar a la API. | `app/main.py` | — | Detectado al ejercitar el inicio de sesión en un navegador |
| 2026-08-29 | Aplicación Web en Next.js: proyectos, tablero, progreso y cambio de estado. | `web/` | [ADR 0002](adr/0002-usar-fastapi-y-nextjs.md) | Sí, revisado por el equipo |
| 2026-08-29 | CORS en la API, para que el navegador pueda llamarla desde la Aplicación Web. | `app/main.py`, `app/config.py` | [C4 nivel 2](c4/nivel2-contenedores.md) | Sí |
| 2026-08-29 | Corrección: la identidad del usuario usaba un hook por componente, así que la página no se enteraba de los cambios hechos en la barra superior. Se pasa a un contexto compartido. | `web/lib/usuario.tsx` | — | Detectado al ejercitar la interfaz en un navegador |
| 2026-08-29 | Corrección: la paginación era inestable porque MySQL guarda `DATETIME` con precisión de segundo y el orden empataba. Se añade fracción de segundo y desempate por `id`. | `app/infrastructure/tablas.py`, `app/infrastructure/repositorios.py` | [ESC-01](calidad/escenarios-calidad.md#esc-01) | Detectado al ejecutar las pruebas contra MySQL |
| 2026-09-18 | Contrato de API documentado: `docs/api/contrato.md`, `docs/api/openapi.yaml`, `docs/api/pruebas-de-contrato.md`. Pruebas de contrato en `test/test_contrato.py`. Verificación en CI. | `docs/api/`, `test/test_contrato.py`, `.github/workflows/ci.yml` | — | Sí, revisado por el equipo |
| 2026-09-18 | ADR-006: se mantiene el modelo sincrónico con eventos en proceso. Condiciones para migrar a consumidores asíncronos documentadas. | `docs/adr/0006-estilo-sincrono-con-eventos-en-proceso.md` | — | Equipo |
| 2026-09-13 | Cierre de dependencias del backend con huella SHA-256, e instalación con `--require-hashes --only-binary`. La CI recompila el cierre en cada `push` y falla si no corresponde a `requirements.txt`. | `requirements.lock.txt`, `Dockerfile`, `.github/workflows/ci.yml` | D-009 | Sí, revisado por el equipo |
| 2026-09-13 | `npm ci --ignore-scripts` en lugar de `npm install`, en la imagen de la Aplicación Web y en la CI. | `web/Dockerfile`, `.github/workflows/ci.yml` | D-009 | Sí |
| 2026-09-13 | Corrección: `responsable` y `fecha_limite` de `TareaSalida` eran opcionales sin valor por defecto, lo que en Pydantic v2 las declara obligatorias admitiendo nulo. | `app/api/esquemas.py` | D-009 | Detectado por análisis estático |
| 2026-09-13 | El descubrimiento del emisor OIDC solo acepta URLs `http` y `https`: `urlopen` también habla `file://`. Misma comprobación en los scripts de desarrollo. | `app/api/seguridad.py`, `scripts/` | [ADR 0005](adr/0005-delegar-la-autenticacion-en-un-proveedor-oidc.md) | Detectado por análisis estático |
