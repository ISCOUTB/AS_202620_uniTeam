# Evidencia S8 — estado actualizado

Revisión del repositorio y del entorno público para contrastar la matriz preliminar recibida.
La auditoría anterior calificaba `73d714c` (2026-09-21); el último commit público observado es
`f25a646` y la revisión del entorno desplegado es `f053ac255fe1`. Esta actualización no cambia
ni atribuye la calificación docente.

## Criterios S8

| Criterio | Estado actual | Evidencia / pendiente |
|---|---|---|
| URL accesible fuera de la universidad | Cumple | [Aplicación web](https://uniteam-web.onrender.com/) carga desde Internet; [API](https://uniteam-api.onrender.com/health) accesible. |
| Health check consultable | Cumple, pero con arranque en frío observado | El 2026-09-27 22:40 Colombia Render mostró la API despertando; después `/health` devolvió 200 en 0,75 s, `base_de_datos=ok`, revisión `f053ac255fe1` (199,63 ms hasta BD). |
| Infraestructura como código | Cumple | [`render.yaml`](../../render.yaml), Dockerfiles y [`compose.yaml`](../../compose.yaml). |
| Recreación siguiendo el README | Cumple | `docker compose up`; procedimientos de producción en la [guía](../despliegue/guia.md). |
| Pipeline en verde | Pendiente de publicar los cambios locales | Último run público observado, [`CI #24`](https://github.com/ISCOUTB/AS_202620_uniTeam/actions/runs/36369024410), verde en `f25a646`. El cambio local hace obligatorio `SONAR_TOKEN`; necesita un nuevo run después de publicarse. |
| Logs estructurados | Cumple en código y pruebas | [`app/observabilidad.py`](../../app/observabilidad.py) emite JSON con plantilla de ruta, estado, duración e ID de petición; sin cuerpo ni correo. |
| Métrica consultable ligada a un escenario | Parcial: ruta pública, ventana sin muestras | [`/metricas/esc-01`](https://uniteam-api.onrender.com/metricas/esc-01) devuelve el escenario y sus umbrales; el 2026-09-27 22:40 Colombia respondió 200 pero `muestras=0`, p95/p99 `null`. Hace falta una consulta autenticada del tablero y repetir la lectura. |
| Secretos protegidos | Parcial: falta confirmar el secreto de CI | `.env.example` separa configuración local y Render almacena variables/Secret File. El workflow requiere `SONAR_TOKEN`, pero su presencia en GitHub no se pudo verificar desde esta sesión; no se inspeccionaron valores secretos. |
| Estimación de costo | Cumple | [Costos](../despliegue/costos.md): volumen, consumo, capas gratuitas, costos alternativos y puntos de ruptura. |
| arc42 §7, una caja por pieza | Cumple | [Vista de despliegue](../arc42/arc42-uniteam.md#7-vista-de-despliegue) incluye web, API, BD, identidad y declara ficheros/trabajos como no usados. |
| arc42 §2, límite y tarjeta | Cumple | T5 fija 0 USD/mes y uso sin tarjeta; cuentas Render, Aiven y Auth0 registradas sin tarjeta en la [guía](../despliegue/guia.md#1-cuentas). |
| ADR por decisión de plataforma | Cumple | ADR-007 a ADR-011 separan sitio, API, BD, identidad y sondeo; registran alternativas, capa gratuita y consecuencias de costo. |

## Criterios transversales

| Criterio | Estado actual | Evidencia / pendiente |
|---|---|---|
| Repositorio público de la organización | Cumple | `ISCOUTB/AS_202620_uniTeam`. |
| Estructura documental mínima | Cumple | arc42, C4, ADR, calidad, API y despliegue están versionados. |
| Estado calificado identificable | Cumple para el último estado público | Rama `master`, commit `f25a646`; el cambio local aún no tiene commit. |
| Convención de nombres y ADR aceptados | Cumple | ADR numerados; las decisiones aceptadas no se reescribieron en esta actualización. |
| Registro de IA de la semana | Cumple como borrador versionado | [`docs/ia.md`](../ia.md) registra el trabajo actual; la revisión/aprobación del equipo queda pendiente. |
| CI, SonarCloud y Quality Gate | Parcial | El run público reporta éxito, pero sus logs no son visibles sin sesión; no se confirmó que el scanner ejecutara. El workflow local falla si falta el token. Marcar los checks requeridos en `master` requiere permisos de administrador. |
| Sin secretos de producción en el repositorio | Cumple según revisión previa | Las credenciales de despliegue están en Render/GitHub; los valores de Compose son solo locales. No se repitió un escaneo del historial en esta actualización. |
| Contribución de todos los integrantes | Cumple: las cuatro cuentas tienen commits visibles en `master` | Ian Novoa (`iansx`): [77c66f5](https://github.com/ISCOUTB/AS_202620_uniTeam/commit/77c66f55f9693cc4802fb32ec006fd81c9812515); Julio César (`super-gremlin`): [f25a646](https://github.com/ISCOUTB/AS_202620_uniTeam/commit/f25a646a9c41748c8e4edb0eba359c075837995e); Juan Bustamante (`Paradox2700`): [73d714c](https://github.com/ISCOUTB/AS_202620_uniTeam/commit/73d714ce49ee2085275755091d00f7688f4dee26); Daniel Manjarres (`DaniGamer0907`): [992b72b](https://github.com/ISCOUTB/AS_202620_uniTeam/commit/992b72b8d42cb9db3b1ba15773782d54bf9170ee). Las correspondencias las confirmó un integrante; no se dedujeron por similitud. |

## Taller aplicado

Hay un [plan reproducible para comparar la API](../despliegue/comparacion-api.md) en Render
Free y en el servidor del laboratorio. El equipo escoge rollback con recuperación de `/health`
en menos de 5 minutos, bajo el límite de 0 USD/sin tarjeta; T6 y ESC-01 son controles
complementarios. El laboratorio no se declara accesible desde Internet y la ejecución comparativa
sigue pendiente.

## Verificaciones ejecutadas

- `145` pruebas backend: pasan en el entorno local.
- `npm run build`: compilación estática y comprobación de tipos correctas.
- `scripts/verificar_enlaces.py` y `scripts/verificar_contrato.py`: correctos.
- La web y `/health` se consultaron desde fuera de la red universitaria; `/metricas/esc-01`
  respondió, pero sin muestras al momento de la comprobación.
- `npm ci` reportó dos vulnerabilidades en dependencias web (una alta y una crítica); quedan
  fuera del alcance de S8 y requieren triage separado.

## Acciones para cerrar los parciales

1. Revisar el historial de cron-job.org y ejecutar la prueba comparativa de recuperación en Render y en el servidor del laboratorio desde una red externa.
2. Un integrante inicia sesión y consulta un tablero de prueba; se vuelve a capturar `/metricas/esc-01` con muestras reales.
3. Publicar los cambios locales, confirmar `SONAR_TOKEN` en GitHub y obtener un run verde del workflow actualizado.
4. Un administrador de `master` marca como requeridos los checks de pruebas, frontend, imágenes y SonarCloud.
