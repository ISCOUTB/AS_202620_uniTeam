# Evidencia S13 · Modelado de amenazas y plan de mitigación

El estado de arquitectura se contrasta con [C4 nivel 1](../c4/nivel1-contexto.md) y
[C4 nivel 2](../c4/nivel2-contenedores.md). La tabla STRIDE, el criterio `P × I`, responsables,
estados y razones de aceptación están en [arc42 §11](../arc42/11-modelado-de-amenazas.md); la
arquitectura de seguridad está en [arc42 §8.4](../arc42/08-arquitectura-de-seguridad.md).

## Dependencias: ejecución y decisión sobre hallazgos

**Pipeline incorporado:** [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml), job
`dependencias`. Escanea las dependencias Python de producción con `pip-audit` y todo el árbol web
con `npm audit --audit-level=high`.

| Escaneo local del 2026-11-01 | Hallazgos iniciales | Decisión aplicada | Resultado tras la mitigación |
|---|---|---|---|
| `pip-audit -r requirements.prod.txt` | 46 registros de avisos en `cryptography==43.0.3`, `PyJWT==2.10.1` y `Starlette==0.38.6` (transitiva de FastAPI). | Actualizar FastAPI a `0.162.0` (Starlette `1.10.0`), `cryptography` a `50.0.2` y PyJWT a `2.15.1`; regenerar `requirements.lock.txt` con hashes. | `No known vulnerabilities found`. |
| `npm audit --omit=dev` | 3 avisos en el árbol de producción: 1 crítico y 2 altos; Next.js `14.2.35`, PostCSS y `source-map-js` estaban afectados. | Actualizar Next.js a `15.5.28`, forzar PostCSS `8.5.32` mediante `overrides` y actualizar `source-map-js` a `1.2.2`; mantener React 18 y la exportación estática. | `found 0 vulnerabilities`. |

La comprobación inicial de todo `requirements.lock.txt` con `pip-audit` no pudo resolver `uvloop`
en Windows porque ese paquete no soporta esa plataforma. Por eso el resultado Python que se
reporta arriba se ejecutó sobre `requirements.prod.txt`; el job de CI también limita `pip-audit`
a ese manifiesto de producción. No se presenta el análisis estático del código como análisis de
dependencias.

**Ejecución de GitHub disponible para el commit base:** [CI run 40250971708](https://github.com/ISCOUTB/AS_202620_uniTeam/actions/runs/40250971708), concluido `success` para el hash indicado arriba. Ese run es anterior a la incorporación del job `dependencias` y **no contiene** un análisis de dependencias. El job nuevo no tiene URL de ejecución todavía; aparecerá cuando el equipo publique su commit y GitHub ejecute la CI. No se publicó ni se disparó ningún run desde esta revisión.

## Privacidad y datos personales

El modelo confirma tratamiento de datos personales, no una ausencia de ellos: el correo/identificador
OIDC se persiste como `MiembroTabla.usuario`, `TareaTabla.creada_por` y
`TareaTabla.responsable`; `AuditoriaTabla.usuario` registra actor, recurso, operación, resultado y
fecha. Proyectos y tareas guardan además nombres y texto de trabajo asociados a esos integrantes.
La evidencia de campos, finalidades y base prevista está en
[arc42 §8.4](../arc42/08-arquitectura-de-seguridad.md#privacidad-y-base-del-tratamiento).

La base prevista es la autorización previa, expresa e informada del titular que exige la
restricción L1 del proyecto, limitada a coordinación
académica, autenticación, asignación y auditoría. El repositorio no muestra captura de
consentimiento, aviso de privacidad ni política de retención/supresión; se deja como limitación
explícita, no como cumplimiento legal verificado. El identificador del proveedor se usa para
identificar al integrante; UniTeam no almacena contraseñas.

## Componente generativo

No hay un componente generativo en producción. La decisión está registrada en
[ADR-014](../adr/0014-no-incorporar-un-componente-generativo.md); los riesgos de prompt, fuga a
un modelo y envenenamiento de contexto no aplican al sistema actual. Deben incorporarse al modelo
antes de revertir esa decisión.

## Barrido de secretos

El barrido de patrones sobre los archivos versionados no encontró candidatos a claves privadas,
tokens conocidos ni asignaciones de secretos/contraseñas. `.env.example` es el único archivo de
entorno versionado; no se encontró un `.env` real en el índice. Este resultado es un barrido de
patrones local, no una certificación de un escáner dedicado.

El `CONTRATO.md` transversal referido por la ficha no está en este checkout; solo existe
[`docs/api/contrato.md`](../api/contrato.md), que es el contrato de API. Por ello no se pudo leer
ni completar la matriz transversal exigida por aquel documento. La matriz S13 de esta ficha sí se
completa abajo.

## Matriz de cumplimiento S13

| Criterio de evaluación | Evidencia técnica esperada | Estado | Observaciones |
|---|---|---|---|
| Tabla de amenazas anclada en elementos del C4 del equipo | STRIDE con contenedor/flujo C4 por fila | Cumple | [Registro STRIDE](../arc42/11-modelado-de-amenazas.md#registro-stride), contrastado con C4 niveles 1 y 2. |
| Priorización por probabilidad e impacto | P, I, producto y orden resultante | Cumple | Escala 1–3 y orden descendente por `P × I`; se explican desempates. |
| Mitigación asignada a cada amenaza, con dueño y estado | Responsable y estado por fila | Cumple | Responsables por función; cada mitigación figura hecha, pendiente o aceptada como riesgo. |
| El plan ataca primero lo priorizado | Correspondencia entre prioridad y trabajo realizado | Cumple | Se corrigieron primero los avisos críticos/altos de dependencias y se dejó el escaneo como puerta de CI; los riesgos altos pendientes quedan explícitos. |
| Análisis de dependencias ejecutado en el pipeline | Línea del workflow y URL del run | No cumple todavía | El job está en [`ci.yml`](../../.github/workflows/ci.yml), pero el run enlazado arriba corresponde al commit anterior y no incluye el job. Falta el run del commit con estos cambios. |
| Hallazgos del análisis revisados y decididos | Hallazgos y decisión por paquete | Cumple | Los hallazgos iniciales se actualizaron; escaneos locales posteriores reportan 0 vulnerabilidades conocidas. |
| Sección de privacidad con datos personales tratados y su base | Datos y base contrastados con el modelo | Cumple | El modelo y las tablas confirman correo/identificadores y actividad. Se identifica autorización informada como base prevista; su captura y retención siguen pendientes. |
| Riesgos del componente generativo, si el sistema lo incorpora | Prompt, fuga y envenenamiento | Cumple (no aplica) | No existe componente generativo; ADR-014 lo descarta. |
| arc42 sección 8 con la arquitectura de seguridad | `docs/arc42/08*` | Cumple | [`08-arquitectura-de-seguridad.md`](../arc42/08-arquitectura-de-seguridad.md), enlazado desde arc42 §8. |
| arc42 sección 11 con las amenazas aceptadas y su motivo | `docs/arc42/11*` | Cumple | [`11-modelado-de-amenazas.md`](../arc42/11-modelado-de-amenazas.md) distingue riesgos aceptados y sus razones. |
| ADR de las mitigaciones que cambian la estructura | ADR aplicable | Cumple | No se adoptó un cambio estructural. ADR-005 registra la decisión vigente de OIDC y el compromiso de almacenamiento de sesión; un BFF/outbox futuro exigirá ADR antes de implementarse. |

