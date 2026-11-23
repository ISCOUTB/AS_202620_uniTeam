# 0021 — Desplegar en Dokploy sobre un servidor institucional

- Estado: Aceptada (reemplaza a 0008, 0009 y, en lo relativo al arranque en frío, a 0011)
- Fecha: 2026-11-22

## Contexto

La API se desplegaba como contenedor Docker en Render plan Free (ADR 0008) con la base de datos en Aiven for MySQL plan Free (ADR 0009) y el sitio estático también en Render (ADR 0007). Ese planteamiento tenía tres problemas graves para el curso:

1. Render plan Free duerme la API tras 15 min sin tráfico, incumpliendo ESC-01 en la primera petición tras la hibernación. El ADR 0011 proponía mantenerla despierta con un sondeo externo cada 6 h, lo que no garantiza ausencia de arranque en frío y consume las 750 h gratuitas.
2. Aiven plan Free apaga la base de datos por inactividad y no tiene SLA, por lo que no sostiene el 99 % mensual de ESC-04.
3. Render pide método de pago para algunas operaciones, en tensión con la restricción T5 (0 USD al mes y cada pieza usable sin tarjeta).

Además, el equipo necesitaba desplegar en un entorno real accesible desde Internet para la sustentación final, con un health check que compruebe la base de datos.

## Decisión

Desplegar las cuatro piezas del sistema en Dokploy sobre un servidor institucional cedido por el docente, usando `docker-compose.yml` (raíz del repositorio) con los servicios `web` (Next.js exportado servido por nginx), `api` (FastAPI), `migrate` (job idempotente `python migrate.py`) y `db` (MySQL 8.4 con volumen `datos_mysql`). Traefik (ya presente en el servidor institucional) enruta TLS y tráfico a los dominios públicos `uniteam-web.iscoutb.dev` (frontend) y `uniteam-api.iscoutb.dev` (API). Los secretos (`DATABASE_URL`, `OIDC_EMISOR`, `OIDC_AUDIENCIA`, `ORIGENES_PERMITIDOS`) se definen como variables de entorno del panel de Dokploy, nunca en el repositorio.

El frontend se construye como sitio estático (`output: "export"`) y se sirve por nginx desde el servicio `web`, igual que en desarrollo. El servicio `db` no publica puertos; solo `web` y `api` son accesibles desde Internet a través de Traefik.

## Alternativas descartadas

- Render Free para API y sitio: descartado por el arranque en frío (incumple ESC-01) y el disco efímero de la base de datos.
- Render Starter (7 USD/mes): supera el límite de costo T5 (0 USD al mes, sin tarjeta).
- VPS propio de pago: supera el límite de costo y requeriría que el equipo gestione parches y disponibilidad.
- Mantener Render + Aiven: el equipo ya no tiene control sobre esas cuentas y la documentación del despliegue vigente debía reflejar el entorno real.

## Consecuencias

- (+) Costo para el equipo: 0 USD al mes.
- (+) Sin arranque en frío: el servidor institucional no hiberna los servicios.
- (+) Base de datos con volumen persistente (`datos_mysql`), no efímero.
- (−) Dependencia del servidor del docente: el equipo no controla parches del sistema operativo, ni Traefik, ni la disponibilidad del servidor; no hay SLA. Es un riesgo declarado (R-08 en arc42 §11).
- (−) No hay alta disponibilidad: una sola instancia, sin réplicas. El bus de eventos sigue en proceso (ADR 0006), así que no hay entrega de eventos entre instancias.
- Sustituye a ADR 0008 (API en contenedor en Render), ADR 0009 (Aiven for MySQL) y, en lo relativo al arranque en frío, a ADR 0011 (sondeo externo). ADR 0007 (sitio estático exportado y servido por nginx) sigue vigente en su fondo.
