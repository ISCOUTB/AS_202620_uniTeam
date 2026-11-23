# Guía de despliegue y operación

Cómo se recrea el entorno desplegado de UniTeam desde cero, cómo se comprueba que funciona y
cómo se revierte. Está escrita para que la siga alguien que no estuvo cuando se hizo.

Procedimiento de medición de ESC-01: [`docs/calidad/mediciones/esc-01-linea-base.md`](../calidad/mediciones/esc-01-linea-base.md).

| Pieza | Dónde se ejecuta | Cómo se describe | Decisión |
|-------|-----------------|------------------|----------|
| Aplicación Web | Servidor institucional · Dokploy | [`docker-compose.yml`](../../docker-compose.yml), servicio `web` | [ADR-007](../adr/0007-servir-la-aplicacion-web-como-sitio-estatico.md) |
| API | Servidor institucional · Dokploy | [`docker-compose.yml`](../../docker-compose.yml), servicio `api` | [ADR-008](../adr/0008-desplegar-la-api-como-contenedor-en-render.md) (reemplazado por 0021) |
| Base de datos | Servidor institucional · Dokploy | [`docker-compose.yml`](../../docker-compose.yml), servicio `db` | [ADR-009](../adr/0009-usar-aiven-for-mysql-como-base-de-datos-gestionada.md) (reemplazado por 0021) |
| Proveedor de identidad | Fuera del servidor | Cuenta institucional o Google | [ADR-010](../adr/0010-usar-auth0-como-proveedor-de-identidad.md) |

## Entorno desplegado

| | URL |
|---|---|
| Aplicación Web | `https://uniteam-web.iscoutb.dev` |
| API | `https://uniteam-api.iscoutb.dev` |
| Health check | `https://uniteam-api.iscoutb.dev/health` |
| Métrica de ESC-01 | `https://uniteam-api.iscoutb.dev/metricas/esc-01` |
| Métricas (Prometheus) | `https://uniteam-api.iscoutb.dev/metricas` |

Desplegado en Dokploy sobre un servidor institucional cedido por el docente ([ADR-0021](../adr/0021-desplegar-en-dokploy-en-un-servidor-institucional.md)). Traefik, ya presente en el servidor, termina TLS y enruta los dos dominios.

**Límites declarados.** El servidor es de un tercero: el equipo no controla parches del sistema operativo ni de Traefik, no hay SLA, y la disponibilidad depende de ese tercero ([R-08](../arc42/arc42-uniteam.md#11-riesgos-y-deuda-técnica)). El costo para el equipo es 0 USD al mes; no se necesita tarjeta.

**Comprobación continua desde Internet.** El workflow [`despliegue.yml`](../../.github/workflows/despliegue.yml) consulta el sitio, el health check, la métrica de ESC-01 y el 401 sin token cada 6 horas desde los corredores de GitHub —fuera de la red de la universidad— y deja en el resumen de cada ejecución la hora, el código y el tiempo de respuesta: [historial de comprobaciones](https://github.com/ISCOUTB/AS_202620_uniTeam/actions/workflows/despliegue.yml). También se lanza a mano con *Run workflow*.

> **Registro histórico (Render, retirado).** El 2026-09-28 el sistema se verificó sobre Render con las URL `uniteam-web.onrender.com` y `uniteam-api.onrender.com` (sitio 200, callback 200, health 200 con base de datos, métricas 200, API sin token 401; revisión `f053ac255fe1`). Esa infraestructura ya no está en uso: el despliegue actual es Dokploy sobre servidor institucional. Se conserva el registro como evidencia histórica, no como estado vigente.

---

## 1. Cuentas

| Servicio | Para qué | Quién tiene acceso |
|----------|----------|--------------------|
| Dokploy (servidor institucional) | API, sitio, base de datos, Traefik | Administrador del servidor (docente) |
| Cuenta institucional / Google | Identidad | Cada usuario del sistema |
| SonarCloud | Análisis estático | Organización `isco-utb` del curso |

**Límite de costo (T5).** El servidor institucional no genera costo para el equipo y no requiere tarjeta. La contrapartida es la dependencia del tercer servidor sin SLA, declarada como riesgo R-08.

---

## 2. Base de datos

La base de datos es MySQL 8.4 corriendo en el servicio `db` de `docker-compose.yml`, con el volumen persistente `datos_mysql:/var/lib/mysql`. La API crea las tablas al arrancar; no es necesario crearlas a mano.

---

## 3. Proveedor de identidad

La API delega la autenticación en un proveedor OpenID Connect ([ADR-0005](../adr/0005-delegar-la-autenticacion-en-un-proveedor-oidc.md)). Los valores se inyectan por variables de entorno en Dokploy:

- `OIDC_EMISOR`: emisor esperado en el token (obligatorio).
- `OIDC_AUDIENCIA`: audiencia esperada (obligatorio).
- `OIDC_JWKS_URL`: opcional, para descubrir las claves públicas por otra URL.

La aplicación web hace el flujo de código con PKCE y envía el token en `Authorization: Bearer`; la API lo verifica contra el JWKS del emisor (firma, `iss`, `aud` y `exp`).

---

## 4. Dokploy: API y sitio

1. Crear una aplicación desde Git, repositorio `ISCOUTB/AS_202620_uniTeam`, rama `master`, usando **Docker Compose** con `docker-compose.yml` en la raíz.
2. Configurar los dominios en Traefik: `uniteam-web.iscoutb.dev` → servicio `web` (puerto 3000) y `uniteam-api.iscoutb.dev` → servicio `api` (puerto 8000). No publicar `db` ni `migrate`.
3. Definir en Dokploy las variables de [`.env.example`](../../.env.example). En particular, `DATABASE_URL`, `OIDC_EMISOR`, `OIDC_AUDIENCIA` y `ORIGENES_PERMITIDOS` son de la API.
4. Las variables `NEXT_PUBLIC_*` son build args del servicio `web` (Next.js las hornea en `npm run build`): `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_OIDC_EMISOR`, `NEXT_PUBLIC_OIDC_CLIENTE`, `NEXT_PUBLIC_OIDC_AUDIENCIA`, `NEXT_PUBLIC_OIDC_CLAIM_USUARIO`, `NEXT_PUBLIC_DEMO_MODE`.
5. El servicio `migrate` ejecuta `python migrate.py` antes de `api`.

Puertos: `api` expone el 8000, `web` el 3000. La base de datos no publica puerto.

---

## 5. Comprobación

Desde cualquier red, fuera de la universidad:

```bash
URL_API=https://uniteam-api.iscoutb.dev
URL_WEB=https://uniteam-web.iscoutb.dev

curl -sS -o /dev/null -w 'web=%{http_code} tiempo=%{time_total}s\n' "$URL_WEB"
curl -sS "$URL_API/health"            # {"estado":"ok","base_de_datos":"ok",...}
curl -sS "$URL_API/metricas/esc-01"   # p95 del tablero frente al umbral de 2 s
curl -sS "$URL_API/metricas" | grep ^uniteam_
curl -sS -o /dev/null -w 'sin token=%{http_code}\n' "$URL_API/proyectos"   # 401
```

Lo mismo, automatizado y con la hora registrada, lo hace el workflow `despliegue.yml`.

Luego, en el navegador: abrir el sitio, **Iniciar sesión**, entrar con la cuenta institucional o Google, crear un proyecto y una tarea. Los logs de esa sesión se ven como una línea JSON por petición.

### Registro de comprobaciones vigentes

| Momento (UTC) | Cómo | Resultado |
|---------------|------|-----------|
| 2026-11-22 | `curl` desde fuera, comprobación directa | `web` 200 (0,75 s), `callback/` 200, `/health` 200, `/metricas/esc-01` 200, `/metricas` 200, `/proyectos` sin token 401. Dominios `iscoutb.dev`. |

---

## 6. Reversión

| Qué falla | Qué se hace | Tiempo |
|-----------|-------------|--------|
| Un despliegue de la API rompe algo | Dokploy → despliegue anterior → **Rollback** | < 2 min |
| Un despliegue del sitio rompe algo | Dokploy → despliegue anterior → **Rollback** | < 1 min |
| El commit malo sigue en `master` | `git revert <commit>` y push; la CI lo valida y Dokploy lo despliega | Lo que tarde la CI |
| El servidor institucional deja de servir | Depende del administrador del servidor (docente); el equipo no controla parches ni disponibilidad | Indefinido (riesgo R-08) |

---

## 7. Secretos

**Ninguna credencial del entorno desplegado está en el repositorio.** Viven en variables de entorno del panel de Dokploy: `DATABASE_URL` (incluye la clave de MySQL), `OIDC_EMISOR`, `OIDC_AUDIENCIA`, `ORIGENES_PERMITIDOS`. [`.env.example`](../../.env.example) documenta todas las variables; el `.env` real está en `.gitignore`.

Las credenciales de `compose.yaml` son las de contenedores locales y efímeros, y se discuten en [análisis estático](../calidad/analisis-estatico.md#6-credenciales-de-base-de-datos-en-el-repositorio--aceptado).

Si un secreto se filtra: se rota en el proveedor, se actualiza en Dokploy y se vuelve a desplegar. Borrarlo de un commit no basta: sigue en el historial.

---

## 8. SonarCloud

El análisis de SonarCloud se ejecuta como **Automatic Analysis** (desde SonarCloud al actualizarse el repositorio), no como un job de GitHub Actions. No requiere `SONAR_TOKEN` ni un job de scanner; con este modo, el CI de GitHub no espera al Quality Gate y SonarCloud no recibe el reporte de cobertura generado por las pruebas.

Panel público: <https://sonarcloud.io/summary/overall?id=ISCOUTB_AS_202620_uniTeam>

Consultado el 2026-11-22: `status: OK`, fiabilidad A, seguridad A, mantenibilidad A, 0 % duplicación, 100 % de hotspots revisados.

---

## 9. Protección de `master`

Para que un fallo **bloquee la integración** y no solo la avise, en GitHub → *Settings → Branches → Add rule* para `master`: *Require status checks to pass before merging*, marcando «Pruebas contra MySQL», «Compilación del frontend» y «Construcción de las imágenes». Lo tiene que activar un administrador del repositorio. El Quality Gate de SonarCloud ya no forma parte de estos checks porque el análisis es automático y no se ejecuta en la CI.
