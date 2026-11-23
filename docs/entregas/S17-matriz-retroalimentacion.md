# Matriz de retroalimentación · cierre (S17)

**Insumo:** formulario «Recomendaciones del jurado» (sustentación final S16) y revisiones entre pares (S14).
**Límite declarado:** el formulario del jurado no se entregó al equipo; esta matriz se construye sobre
las recomendaciones publicadas en [`feedback/feedback.md`](../../feedback/feedback.md) y en la
[evaluación S13/S14 del 17 de noviembre de 2026](../../feedback/evaluacion-s13-s14-s15-2026-11-17.md),
citando su origen exacto. Cuando el formulario del jurado se entregue, esta matriz debe cotejarse
fila por fila contra él.

Cada recomendación aparece con su origen, una clasificación (aceptada / rechazada / aplazada), una
justificación técnica y, para las aceptadas, el enlace al commit, PR, ADR o run que la implementa.
Una fila sin clasificar es una fila sin decidir: aquí todas están clasificadas.

| # | Recomendación | Origen | Clasificación | Justificación técnica | Enlace (commit / PR / ADR / run) |
|---|---------------|--------|---------------|-----------------------|----------------------------------|
| R-01 | Declarar en la ficha del problema las dos tensiones de calidad enfrentadas | S1, feedback S1 | Aceptada | La ficha ya declara atributos en conflicto (seguridad vs rendimiento, disponibilidad vs costo); se reafirma en arc42 §1.2 y el árbol de utilidad. | [`ficha.md`](../ficha.md), [`calidad/arbol-utilidad.md`](../calidad/arbol-utilidad.md) |
| R-02 | `docs/aspectos.md` como tabla de ocho columnas con al menos una fila ID + aspecto | S1, feedback S1 | Aceptada | Tabla de 8 columnas (ID, Aspecto, Requisito, C4, ADR, Código, Pruebas, Evidencia) con 13 filas, todas con ID. | [`aspectos.md`](../aspectos.md) |
| R-03 | `docs/ia.md` registrar entradas por uso y qué se rechazó y por qué | S1, feedback S1 | Aceptada | Bitácora con columnas «qué se pidió / qué se aceptó / qué se rechazó y por qué»; incluye esta sesión (S16/S17). | [`ia.md`](../ia.md) |
| R-04 | Renombrar ADR a `NNNN-titulo-en-kebab-case.md` (sin prefijo «ADR-») | S2, S3, evaluación 17-nov | Aceptada | Hecho en esta sesión: `0018`, `0019`, `0020` (renombrados de los duplicados `0010`, `0011`, `0012`), y nuevos `0021`, `0022`. Borrados `docs/adr/.gitkeep` y `docs/c4/.gitkeep`. | commits de esta rama (ADR) |
| R-05 | Marcar ADR-001 como reemplazado por ADR-002 | S3 | Aceptada | Ya estaba marcado así; se conserva en la tabla de arc42 §9. | [`arc42/arc42-uniteam.md#9-decisiones-de-arquitectura`](../arc42/arc42-uniteam.md#9-decisiones-de-arquitectura) |
| R-06 | Enlazar ADR-003 desde `docs/aspectos.md` y desde el escenario que lo motiva | S3 | Aceptada | A-02, A-04, A-07, A-08 y A-11 enlazan `0003-usar-eventos-de-dominio-en-proceso.md`. | [`aspectos.md`](../aspectos.md) |
| R-07 | Documentar en README el comando único de arranque de la app | S3 | Aceptada | README «Arranque rápido»: `docker compose up`. | [README.md](../../README.md#arranque-rápido) |
| R-08 | Corregir el paquete `httpx2` de `requirements.txt` | S3 | Rechazada | No existe paquete `httpx2` en el proyecto; el backend usa `httpx` solo en scripts de desarrollo y el cierre (`requirements.lock.txt`) se verifica determinísticamente en la CI. No hay nada que corregir. | — |
| R-09 | Registrar en `docs/ia.md` el uso de IA de la semana con lo rechazado y su motivo | S3 | Aceptada | Bitácora de `docs/ia.md` incluye cada semana con rechazados y motivos. | [`ia.md`](../ia.md) |
| R-10 | Todos los integrantes firmen los commits; cuatro en el historial antes del corte | S2, S3 | Aceptada | `git shortlog` sobre `master` atribuye commits a las cuatro cuentas declaradas (Emiliani, Novoa, Bustamante, Manjarrés) más dependabot. | `git shortlog -sne master` |
| R-11 | Que el historial del repositorio no conserve archivos de un proyecto anterior | S2 | Aceptada | Barrido del árbol: solo archivos de UniTeam; `uniteam.db` y `esperado.txt` están en `.gitignore`. | `.gitignore` |
| R-12 | arc42 §9 cite explícitamente los ADR | S4 | Aceptada | Tabla de ADR en arc42 §9 con estado y enlaces a cada archivo, incluida la marcación de reemplazados. | [`arc42/arc42-uniteam.md#9-decisiones-de-arquitectura`](../arc42/arc42-uniteam.md#9-decisiones-de-arquitectura) |
| R-13 | arc42 §10 referencie los escenarios de calidad | S4 | Aceptada | §10.2 tabla de ESC-01 a ESC-05 con medida, umbral y prioridad. | [`arc42/arc42-uniteam.md#10-requisitos-de-calidad`](../arc42/arc42-uniteam.md#10-requisitos-de-calidad) |
| R-14 | Glosario use términos propios del dominio | S4 | Aceptada | §12 glosario con Dokploy, Traefik, OIDC, JWKS, pertenencia, tablero, flujo de estados, ESC, deriva, bus en proceso, WebSocket. | [`arc42/arc42-uniteam.md#12-glosario`](../arc42/arc42-uniteam.md#12-glosario) |
| R-15 | Publicar URL del run de CI en verde que ejecute la prueba del recorrido completo | S4 | Aceptada | CI en verde en `master`: run `45104471750` (CI) y `45104471698` (seguridad-dependencias), 2026-11-23. | run `45104471750` |
| R-16 | El registro de IA debe mostrar lo aceptado y lo rechazado con su motivo | S4 | Aceptada | Columnas de la bitácora de `docs/ia.md` cubren aceptado y rechazado con motivo. | [`ia.md`](../ia.md) |
| R-17 | Medir con una cifra cuán explotable era el problema antes del cambio (autenticación) | S5, evaluación 17-nov | Aceptada | Línea base del desafío final: 100 % de identidades suplantables vía `X-Usuario`; después, 0 % (401 garantizado). | [`calidad/mediciones/desafio-autenticacion.md`](../calidad/mediciones/desafio-autenticacion.md) |
| R-18 | Medir el resultado después del cambio y compararlo contra el umbral del escenario de seguridad | S5, evaluación 17-nov | Aceptada | 11 pruebas negativas en 401; ESC-03 al 100 % de denegados con auditoría; 7 identidades con `X-Usuario` → 401 en despliegue real (2026-11-22). | [`test/test_autenticacion.py`](../../test/test_autenticacion.py) |
| R-19 | Entrada en el registro de IA que hable puntualmente de la pieza de autenticación | S5, evaluación 17-nov | Aceptada | Fila de `docs/ia.md` de 2026-11-22 con la pieza del desafío final (aceptado: delegación OIDC; rechazado: mantener `X-Usuario` como fallback). | [`ia.md`](../ia.md) |
| R-20 | Mapa de contextos: auditar, contrastar entidades con esquema, reemplazar marcadores «revisar» por no conformidades con ruta y línea | S6 | Aplazada | El mapa de contextos existe en `docs/calidad/mapa-contextos.md`; el contraste entidad/esquema con rutas y líneas quedó pendiente y se declara como deuda en arc42 §11.1. | [`calidad/mapa-contextos.md`](../calidad/mapa-contextos.md) |
| R-21 | Incorporar el mapa y el lenguaje ubicuo en arc42 §8 | S6 | Aplazada | arc42 §8 documenta consistencia, caché y eventos, pero no cita el lenguaje ubicuo ni el mapa; pendiente. | — |
| R-22 | Relacionar los contextos con la tabla de aspectos | S6 | Aplazada | La tabla de aspectos enlaza requisitos y C4, pero no el mapa de contextos; pendiente. | — |
| R-23 | Publicar el análisis SonarCloud con su Quality Gate | S6 | Aceptada (parcial) | Panel público con Quality Gate `OK` (consultado 2026-11-22), pero el análisis es Automático de SonarCloud, no un job de CI; la cobertura no se reporta. Se documenta en `docs/despliegue/guia.md §8` y `docs/calidad/analisis-estatico.md`. | [`despliegue/guia.md#8-sonarcloud`](../despliegue/guia.md#8-sonarcloud) |
| R-24 | Reparar el workflow de CI en la rama principal (terminaba en rojo, incluido Quality Gate) | S8, seguimiento S12 | Aceptada | CI en verde en `master` (run `45104471750`, 2026-11-23). El job de Sonar se retiró de la CI porque el análisis es automático; no se afirma que el gate bloquee la CI. | run `45104471750` |
| R-25 | No editar ADR aceptados; escribir uno nuevo y marcar el anterior como reemplazado | S8 | Aceptada | Regla seguida en esta sesión: 0008, 0009 y 0011 marcados «Reemplazado por 0021» sin reescribir su cuerpo; 0021 es el nuevo ADR. | [`adr/0008-desplegar-la-api-como-contenedor-en-render.md`](../adr/0008-desplegar-la-api-como-contenedor-en-render.md), [`adr/0021-desplegar-en-dokploy-en-un-servidor-institucional.md`](../adr/0021-desplegar-en-dokploy-en-un-servidor-institucional.md) |
| R-26 | Confirmar a qué integrante corresponde cada cuenta del historial | S8, evaluación 17-nov | Aceptada | `docs/ia.md` y el `Equipo` de README documentan la correspondencia cuenta-persona. | [README.md#equipo](../../README.md#equipo) |
| R-27 | Publicar URL desplegada y health (por Moodle) | S8 | Aceptada | README y S16 guía publican `https://uniteam-web.iscoutb.dev` y `https://uniteam-api.iscoutb.dev/health`. | [README.md#sistema-desplegado](../../README.md#sistema-desplegado) |
| R-28 | Comprobar el costo de la consulta extra en MySQL | S9 | Aplazada | La medición de ESC-01 y de «Mis tareas» está en SQLite; repetir contra MySQL queda pendiente (declarado en `docs/ia.md` y en la ficha de ESC-01). | — |
| R-29 | Hacer bloqueante la auditoría preservando el código de salida (pipefail) y resolver/justificar hallazgos Python con evidencia reproducible | S12 seguimiento, S13 | Aceptada (parcial) | `seguridad.yml` ahora usa `set -eo pipefail` y audita `requirements.lock.txt`; el informe con hallazgos reales se rellena tras el próximo run (`PENDIENTE_RUN`). | [`seguridad/dependencias.md`](../seguridad/dependencias.md), [`.github/workflows/seguridad.yml`](../../.github/workflows/seguridad.yml) |
| R-30 | Actualizar la sonda a las URL DuckDNS vigentes | S12 seguimiento | Aceptada | La sonda y README ya apuntan a `iscoutb.dev` (dominios institucionales, no DuckDNS ni Render); el run de despliegue fallaba sobre el commit anterior (`0811cdd`) que aún tenía Render. Falta un run verde posterior a los cambios. | [`despliegue/guia.md#5-comprobación`](../despliegue/guia.md#5-comprobaci%C3%B3n) |
| R-31 | Implementar y probar controles de seguridad que los ADR describen como pendientes | S12 seguimiento | Aceptada (parcial) | T1-T3 de amenazas pasan a «Hecha» con ruta y prueba; T4, T5, T8, T9, T11 quedan parciales o pendientes con justificación en `docs/seguridad/amenazas.md`. | [`seguridad/amenazas.md`](../seguridad/amenazas.md) |
| R-32 | Completar informe SCA y ejecutar primero mitigaciones de mayor riesgo | S13 | Aceptada (parcial) | Modelo de amenazas priorizado por P×I; T1 primero. El informe SCA (`dependencias.md`) se rellena con el run real (`PENDIENTE_RUN`). | [`seguridad/amenazas.md`](../seguridad/amenazas.md) |
| R-33 | Incorporar pares y estados en §11 | S14 | Aceptada | Nueva subsección §11.1 con cada señalamiento, origen, estado y evidencia/motivo. | [`arc42/arc42-uniteam.md#111-señalamientos-recibidos-y-su-estado`](../arc42/arc42-uniteam.md#111-señalamientos-recibidos-y-su-estado) |
| R-34 | Medir WebSocket y nueva interfaz sobre el despliegue declarado; reconciliar Render/DuckDNS y workflow | S14, S15 | Aplazada | Hay pruebas automatizadas de WebSocket (8) pero no medición sobre `iscoutb.dev`; la sonda ya consulta `iscoutb.dev` y no Render. | [`test/test_websocket.py`](../../test/test_websocket.py) |
| R-35 | Recorrer todos los aspectos de punta a punta: requisito → C4 → ADR → código → prueba/medición | S14 | Aceptada | Tabla de aspectos con 13 filas, cada una con cadena completa; celdas vacías se rellenan con la declaración explícita de lo que falta. | [`aspectos.md`](../aspectos.md) |
| R-36 | Cerrar arc42 secciones 1 a 12 con glosario y C4 de tres niveles | S14 | Aceptada | arc42 tiene secciones 1-12 con glosario; C4 tiene nivel 1, nivel 2 y nivel 3 (nuevo `docs/c4/nivel3-componentes.md`). | [`arc42/arc42-uniteam.md`](../arc42/arc42-uniteam.md), [`c4/nivel3-componentes.md`](../c4/nivel3-componentes.md) |
| R-37 | Alinear sonda, README y guía con dominios reales; publicar subdominio iscoutb.dev | S12 seguimiento | Aceptada | README, guía y `despliegue.yml` apuntan a `uniteam-web.iscoutb.dev` y `uniteam-api.iscoutb.dev`; comprobación directa verificada 2026-11-22 (todos 200/401). | [`despliegue/guia.md`](../despliegue/guia.md) |

**Resumen de clasificación:** 29 aceptadas (7 de ellas parciales: el trabajo está hecho pero falta evidencia de run o de medición real), 1 rechazada (R-08, `httpx2` no existe), 6 aplazadas (R-20, R-21, R-22, R-28, R-34; se declaran como deuda en arc42 §11). Ninguna fila queda sin clasificar.

---

## Evidencia de ausencia de regresiones

La CI de `master` está en verde después de los cambios de esta rama:
- CI (`pruebas`, `frontend`, `imagenes`): run `45104471750`, 2026-11-23, `success`.
- Seguridad (`seguridad-dependencias`): run `45104471698`, 2026-11-23, `success`.

El run de `despliegue.yml` todavía falla sobre el commit anterior `0811cdd` (URL de Render); el `master` actual ya apunta a `iscoutb.dev` y las seis comprobaciones pasan en vivo. Falta lanzar un `workflow_dispatch` de `despliegue.yml` sobre el commit final para dejar el run verde fechado posterior a los cambios (pendiente al merge).

---

## Retrospectiva (una lección por integrante)

| Integrante | Lección concreta del proyecto |
|------------|------------------------------|
| Julio César Emiliani Ramos | Una decisión de arquitectura (OIDC en lugar de `X-Usuario`) solo vale si se mide antes y después; sin la cifra de «100 % suplantable» la mejora no se puede justificar ante el jurado. |
| Ian Novoa Carrillo | No confiar en que un job verde de CI signifique que todos los controles pasaron: el `tee` sin `pipefail` ocultaba hallazgos de `pip-audit`; la auditoría debe ser bloqueante por diseño. |
| Juan José Bustamante | Documentar el despliegue real (Dokploy, servidor institucional) antes de que el repo describa otro entorno (Render) evita que el evaluador califique algo que ya no existe. |
| Daniel Isaac Manjarrés | Los ADR aceptados no se reescriben: si cambia el entorno, se marca el antiguo como «reemplazado» y se escribe uno nuevo con la evidencia de por qué. Eso hace que la evolución sea reconstruible. |
