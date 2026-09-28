# Taller aplicado: dónde ejecutar la API

## Condición operativa elegida

El equipo elige **tiempo de recuperación ante un despliegue fallido**: volver a la última
versión conocida como buena y recuperar `/health` 200 en **menos de 5 minutos**, con un costo
de **0 USD al mes y sin tarjeta**. Es una condición verificable en ambos proveedores y relevante
para una API pública. La disponibilidad desde fuera de la universidad (T6) es requisito de
admisibilidad de la alternativa, no un resultado que se dé por supuesto. ESC-01 —tablero de 200
tareas, 30 usuarios concurrentes, p95 ≤ 2 s, p99 ≤ 4 s y cero errores— es la medida de calidad
complementaria.

## Alternativas

| Criterio | A. Render Free, contenedor Docker (elegida) | B. Servidor del laboratorio, Docker Compose |
|---|---|---|
| Costo directo del equipo | 0 USD/mes con 750 horas compartidas; el sondeo de 06:00 a 23:59 usa aproximadamente 560 h/mes | 0 USD/mes para el equipo si el servidor lo provee el curso; capacidad, energía y operación quedan a cargo del laboratorio |
| Tarjeta | No la pidió al crear la cuenta (guía de despliegue, 2026-09-27) | No; condición garantizada por el curso |
| Acceso externo | URL HTTPS pública ya comprobada | Por verificar con el administrador: DNS/IP pública, firewall, TLS y proxy inverso |
| ESC-01 | El sondeo horario solo evitaría el frío si cron-job.org está activo; el 2026-09-27 a las 22:40 Colombia Render mostró la API despertando | No debería dormir mientras el host esté activo; la latencia real hacia Aiven y la disponibilidad del host deben medirse |
| Health y rollback | `/health` comprueba MySQL; Render conserva despliegues anteriores y ofrece rollback desde Events. Objetivo: health 200 en < 5 min, por medir en la ejecución del taller | La misma ruta funciona con Compose; volver al tag anterior y comprobar health. Objetivo: health 200 en < 5 min, por medir en la ejecución del taller |
| Riesgo dominante | Cuota de horas compartida y dependencia de Render/Aiven | No está confirmada la llegada desde Internet; disponibilidad y recuperación dependen del laboratorio |

La comparación usa **la misma pieza** (API FastAPI), imagen de producción y base de datos
MySQL administrada; solo cambia dónde corre el contenedor API. No se despliega el emisor OIDC
de desarrollo. La alternativa del laboratorio no se declara apta para T6 hasta que una prueba
desde una red externa confirme HTTPS y `/health`.

## Plan reproducible

1. Preparar una identidad de prueba y un proyecto dedicado por entorno. No usar cuentas ni datos
   de estudiantes. Mantener el token en una variable de entorno y no adjuntarlo a los resultados.
2. En Render, anotar la revisión de `/health`; comprobar `/health` y guardar la hora, código y
   tiempo de respuesta del workflow [`despliegue.yml`](../../.github/workflows/despliegue.yml).
3. Para el laboratorio, pedir al administrador el nombre del host, confirmar que Docker está
   disponible y que permite salida TLS a Aiven. Desplegar el destino `api` de `Dockerfile` con
   `DATABASE_URL` y OIDC de prueba suministrados como secretos del entorno. Publicarlo detrás
   de un proxy HTTPS; no abrir directamente MySQL ni el puerto de la API a Internet.
4. Desde una máquina fuera de la universidad, verificar `GET /health` y guardar la revisión,
   el código y la latencia. Si no se puede resolver el host o el health no devuelve 200, marcar
   la alternativa B como **no apta para T6** y no continuar la comparación de rendimiento.
5. En cada entorno apto, ejecutar desde el mismo cliente y con la misma carga el medidor
   [`scripts/medir_esc01.py`](../../scripts/medir_esc01.py), con un token válido para esa
   instalación. El valor predeterminado reproduce 200 tareas y 30 usuarios × 10 consultas.
   Registrar p95, p99, errores y hora; hacer una ejecución tras inactividad para observar el
   arranque en frío y otra con la instancia ya activa.
6. En un entorno de prueba aislado, anotar la hora de inicio y simular un despliegue fallido
   (por ejemplo, introducir una configuración inválida que impida el arranque, sin cambiar el
   esquema ni escribir datos). En Render, usar **Events → Rollback**; en el laboratorio,
   restaurar el tag previo y ejecutar `docker compose up -d`. Medir hasta que el `/health`
   externo devuelva 200 y confirme la base de datos. No hacer esta prueba sobre producción ni
   sobre la base de datos con datos reales.
7. Completar la tabla de resultados. Adjuntar el run de CI y la ejecución del workflow externo;
   no copiar secretos ni datos personales.

## Registro de resultados

No se inventan resultados del servidor del laboratorio: se completan al ejecutar el plan.

| Medida | Render Free | Laboratorio | Criterio |
|---|---|---|---|
| Revisión probada | `f053ac255fe1` (comprobación pública existente) | Pendiente | Revisiones identificables |
| Health desde red externa | 200, comprobado | Pendiente | 200 sobre HTTPS |
| ESC-01 p95 / p99 / errores | Pendiente repetir con token de prueba | Pendiente | ≤ 2 s / ≤ 4 s / 0 |
| Arranque tras inactividad | ~1 min si queda fuera de la franja sondeada | Pendiente | Registrar, no ocultar |
| Rollback y recuperación de health | Pendiente medir con prueba controlada | Pendiente medir | Objetivo < 5 min; registrar tiempo observado |
| Costo directo mensual | 0 USD bajo T5 y el horario de sondeo | 0 USD para el equipo, sujeto a confirmación del servicio del laboratorio | ≤ 0 USD |
| Requiere tarjeta | No, verificado | No, garantía del curso | No |

## Decisión provisional

Se conserva Render para la API porque T6 ya está demostrado con una URL pública y health
comprobable, y el panel ofrece una acción de rollback incorporada. El servidor del laboratorio
es la alternativa de 0 USD y sin tarjeta, pero su alcance desde Internet y su tiempo de
recuperación todavía no están verificados. La elección solo se confirma al medir el objetivo de
5 minutos en ambas alternativas; el laboratorio no sustituye al despliegue público si no cumple
T6.

**Evidencia de la ejecución del taller:** pendiente de ejecutar la prueba de recuperación en
ambos entornos y medir el servidor del laboratorio. Este documento es el plan reproducible, no
una afirmación de que el prototipo o las mediciones ya se hayan ejecutado.