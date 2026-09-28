# Guía de despliegue y operación

Cómo se recrea el entorno desplegado de UniTeam desde cero, cómo se comprueba que funciona y
cómo se revierte. Está escrita para que la siga alguien que no estuvo cuando se hizo.

| Pieza | Dónde se ejecuta | Cómo se describe | Decisión |
|-------|-----------------|------------------|----------|
| Aplicación Web | Render, sitio estático (CDN) | [`render.yaml`](../../render.yaml) | [ADR-007](../adr/0007-servir-la-aplicacion-web-como-sitio-estatico.md) |
| API | Render, servicio web Docker | [`render.yaml`](../../render.yaml) + [`Dockerfile`](../../Dockerfile) | [ADR-008](../adr/0008-desplegar-la-api-como-contenedor-en-render.md) |
| Base de datos | Aiven for MySQL, plan Free | Pasos 2 y 4 de esta guía | [ADR-009](../adr/0009-usar-aiven-for-mysql-como-base-de-datos-gestionada.md) |
| Proveedor de identidad | Auth0, plan Free | Paso 3 de esta guía | [ADR-010](../adr/0010-usar-auth0-como-proveedor-de-identidad.md) |

## Entorno desplegado

| | URL |
|---|---|
| Aplicación Web | `https://uniteam-web.onrender.com` |
| API | `https://uniteam-api.onrender.com` |
| Health check | `https://uniteam-api.onrender.com/health` |
| Métrica de ESC-01 | `https://uniteam-api.onrender.com/metricas/esc-01` |
| Métricas (Prometheus) | `https://uniteam-api.onrender.com/metricas` |

Desplegado el 2026-09-27. Proveedor de identidad: el *tenant* de Auth0
`dev-6nhlg2x2gaqmcsmv.us.auth0.com`. Base de datos: Aiven for MySQL, servicio
`mysql-30e7be73-uniteam`. Ninguno de estos nombres es secreto; las credenciales viven en
Render (§7).

**Comprobación continua desde Internet.** El workflow
[`despliegue.yml`](../../.github/workflows/despliegue.yml) consulta el sitio, el health check,
la métrica de ESC-01 y el 401 sin token cada 6 horas desde los corredores de GitHub —fuera de
la red de la universidad— y deja en el resumen de cada ejecución la hora, el código y el tiempo
de respuesta: [historial de comprobaciones](https://github.com/ISCOUTB/AS_202620_uniTeam/actions/workflows/despliegue.yml).
También se lanza a mano con *Run workflow*.

---

## 1. Cuentas

Todas se crean sin tarjeta, salvo que Render la pida (ver abajo).

| Servicio | Para qué | Quién tiene acceso |
|----------|----------|--------------------|
| [Render](https://render.com) | API y sitio | Integrante que despliega; se invita al resto al espacio de trabajo |
| [Aiven](https://aiven.io) | Base de datos | Ídem |
| [Auth0](https://auth0.com) | Identidad | Ídem |
| [SonarCloud](https://sonarcloud.io/organizations/isco-utb) | Análisis estático | Organización `isco-utb` del curso |

**Verificación de «sin tarjeta».** Al crear cada cuenta, anotad aquí si el proveedor pidió
tarjeta. Es un dato que exigen las ADR y que la documentación de Render no deja claro:

| Proveedor | ¿Pidió tarjeta? | Fecha | Quién lo comprobó |
|-----------|-----------------|-------|-------------------|
| Render | **No** | 2026-09-27 | Julio César Emiliani Ramos, al crear la cuenta |
| Aiven | **No** | 2026-09-27 | Julio César Emiliani Ramos, al crear la cuenta |
| Auth0 | **No** | 2026-09-27 | Julio César Emiliani Ramos, al crear la cuenta |

Ninguno de los tres pidió tarjeta: la restricción [T5](../arc42/arc42-uniteam.md#21-restricciones-técnicas)
se cumple para todas las piezas. Si en el futuro alguno la exigiera, la alternativa sin tarjeta
es la misma imagen en el servidor del laboratorio con `docker compose up`.

## 2. Aiven: base de datos

1. *Create service* → **MySQL** → plan **Free** → región en la costa este de EE. UU.
2. Cuando esté en *Running*, en *Overview → Connection information*:
   - copiar el **Service URI** (`mysql://avnadmin:…@…:…/defaultdb?ssl-mode=REQUIRED`);
   - descargar el **CA certificate** (`ca.pem`).
3. Construir la `DATABASE_URL` de la API a partir del Service URI, cambiando el esquema y el
   parámetro final:

   ```
   mysql+pymysql://avnadmin:<clave>@<host>:<puerto>/defaultdb?ssl_ca=/etc/secrets/aiven-ca.pem
   ```

No hace falta crear tablas: la API las crea al arrancar.

## 3. Auth0: proveedor de identidad

1. **API.** *Applications → APIs → Create API*. Nombre `UniTeam API`, identificador
   `https://api.uniteam` (es la **audiencia**; no tiene que ser una URL que exista), algoritmo
   **RS256**.
2. **Aplicación.** *Applications → Create Application* → **Single Page Application**. En
   *Settings*, con la URL del sitio de Render (paso 4):
   - *Allowed Callback URLs*: `https://<sitio>.onrender.com/callback/` — **con barra final**;
   - *Allowed Logout URLs* y *Allowed Web Origins*: `https://<sitio>.onrender.com`.
   Copiar el **Client ID** y el **Domain**.
3. **Correo en el token.** *Actions → Library → Create Action* (trigger *Login / Post Login*),
   con este código, y añadirla al flujo *Login* con *Deploy*:

   ```js
   exports.onExecutePostLogin = async (event, api) => {
     if (event.user.email) {
       api.accessToken.setCustomClaim("https://uniteam.app/email", event.user.email);
     }
   };
   ```

   Sin esto el token solo lleva un identificador interno de Auth0 y no se pueden añadir
   miembros a un proyecto por su correo.
4. *Authentication → Social*: dejar activada **Google** para que se pueda entrar con una cuenta
   existente.

## 4. Render: API y sitio

1. *New → Blueprint* → repositorio `ISCOUTB/AS_202620_uniTeam`, rama `master`. Render lee
   [`render.yaml`](../../render.yaml) y propone los dos servicios. Si la organización no ha
   dado acceso a Render al repositorio, un administrador de `ISCOUTB` debe autorizarlo.
2. Render pide las variables marcadas con `sync: false`. Primera pasada:

   | Servicio | Variable | Valor |
   |----------|----------|-------|
   | uniteam-api | `DATABASE_URL` | La del paso 2 |
   | uniteam-api | `OIDC_EMISOR` | `https://<Domain de Auth0>/` |
   | uniteam-api | `OIDC_AUDIENCIA` | `https://api.uniteam` |
   | uniteam-api | `ORIGENES_PERMITIDOS` | La URL del sitio; si aún no se conoce, `https://uniteam-web.onrender.com` |
   | uniteam-web | `NEXT_PUBLIC_API_URL` | La URL de la API; si aún no se conoce, `https://uniteam-api.onrender.com` |
   | uniteam-web | `NEXT_PUBLIC_OIDC_EMISOR` | `https://<Domain de Auth0>` |
   | uniteam-web | `NEXT_PUBLIC_OIDC_CLIENTE` | El Client ID del paso 3 |
   | uniteam-web | `NEXT_PUBLIC_OIDC_AUDIENCIA` | `https://api.uniteam` |

3. **Certificado de la base de datos.** *uniteam-api → Environment → Secret Files → Add*:
   nombre `aiven-ca.pem`, contenido el `ca.pem` del paso 2. Render lo monta en
   `/etc/secrets/aiven-ca.pem`.
4. **Cerrar el círculo.** Las dos URL se conocen tras el primer despliegue. Si difieren de las
   supuestas, corregir `ORIGENES_PERMITIDOS` y `NEXT_PUBLIC_API_URL`, y en el sitio pulsar
   *Manual Deploy → Clear build cache & deploy*: las variables `NEXT_PUBLIC_*` se hornean al
   compilar. Actualizar también las URL de Auth0 (paso 3.2) y la tabla del principio.

A partir de aquí cada push a `master` se despliega solo, **cuando la CI termina en verde**
(`autoDeployTrigger: checksPass`).

## 5. Comprobación

Desde cualquier red, fuera de la universidad:

```bash
URL_API=https://uniteam-api.onrender.com
URL_WEB=https://uniteam-web.onrender.com

curl -sS -o /dev/null -w 'web=%{http_code} tiempo=%{time_total}s\n' "$URL_WEB"
curl -sS "$URL_API/health"            # {"estado":"ok","base_de_datos":"ok",...}
curl -sS "$URL_API/metricas/esc-01"   # p95 del tablero frente al umbral de 2 s
curl -sS "$URL_API/metricas" | grep ^uniteam_
curl -sS -o /dev/null -w 'sin token=%{http_code}\n' "$URL_API/proyectos"   # 401
```

Lo mismo, automatizado y con la hora registrada, lo hace el workflow `despliegue.yml`.

La primera petición tras 15 minutos sin tráfico tarda alrededor de un minuto: la API despierta
([ADR-008](../adr/0008-desplegar-la-api-como-contenedor-en-render.md#consecuencias)). Las
siguientes, no.

Luego, en el navegador: abrir el sitio, **Iniciar sesión**, entrar con Google, crear un
proyecto y una tarea. Los logs de esa sesión se ven en *uniteam-api → Logs*, una línea JSON por
petición.

### Registro de comprobaciones

| Momento (UTC) | Cómo | Resultado |
|---------------|------|-----------|
| 2026-09-28 00:25 | Navegador, desde Cartagena | Inicio de sesión con Google a través de Auth0; el correo llega en el token y la API lista los proyectos del usuario. Flujo completo: interfaz → API → Aiven. |
| 2026-09-28 00:39 | [Workflow `despliegue.yml`, run 36362991640](https://github.com/ISCOUTB/AS_202620_uniTeam/actions/runs/36362991640), corredor de GitHub | Sitio 200 (0,18 s) · `/callback/` 200 · `/health` 200 con base de datos `ok` · `/metricas/esc-01` 200 · `/metricas` 200 · API sin token 401. Revisión desplegada `f053ac255fe1`. |

**Observación de la primera comprobación.** `/health` mide **200 ms de latencia hasta la base de
datos** por consulta, y la primera consulta real del tablero tardó 0,90 s dentro de la API: casi
todo es ida y vuelta a Aiven, porque la consulta del tablero hace varias. Cumple ESC-01 (p95 ≤
2 s), pero con menos margen que la línea base local de 762 ms. Si el margen se estrecha, lo
primero es comprobar en la consola de Aiven que el servicio está en la misma región que la API
(Render Virginia) y, si no, recrearlo allí; lo segundo, reducir las consultas por petición.

### Mantener la API despierta

Decidido en el [ADR-011](../adr/0011-mantener-la-api-despierta-con-un-sondeo-externo.md). En
[cron-job.org](https://cron-job.org), una cuenta gratuita y sin tarjeta:

1. *Create cronjob* → **URL:** `https://uniteam-api.onrender.com/health`.
2. **Execution schedule:** cada minuto, **de 06:00 a 23:59**, zona horaria
   **America/Bogota**. Las 24 horas también funcionan, pero dejan solo 6 h de margen sobre las
   750 h gratuitas; si se agotan, Render suspende la API hasta el mes siguiente.
3. Guardar. Para revertir, desactivar el trabajo.

Los sondeos correctos no aparecen en los logs; se ven en `/metricas`, bajo
`uniteam_peticiones_total{ruta="/health"}`.

## 6. Reversión

| Qué falla | Qué se hace | Tiempo |
|-----------|-------------|--------|
| Un despliegue de la API rompe algo | *uniteam-api → Events* → despliegue anterior → **Rollback**. No recompila: reutiliza la imagen. | < 2 min |
| Un despliegue del sitio rompe algo | *uniteam-web → Events* → **Rollback** | < 1 min |
| El commit malo sigue en `master` | `git revert <commit>` y push; la CI lo valida y Render lo despliega | Lo que tarde la CI |
| Render deja de servir o se encarece | La misma imagen corre con `docker compose up` en el servidor del laboratorio; solo cambian las variables de entorno | Horas |
| Aiven se apaga por inactividad | Consola de Aiven → *Power on*. El health check devuelve 503 mientras tanto y Render no enruta tráfico a una API sin base de datos | Minutos |

## 7. Secretos

**Ninguna credencial del entorno desplegado está en el repositorio.** Viven en:

| Secreto | Dónde |
|---------|-------|
| `DATABASE_URL` (incluye la clave de MySQL) | Render → uniteam-api → Environment |
| Certificado de la CA de Aiven | Render → uniteam-api → Secret Files |
| `SONAR_TOKEN` | GitHub → Settings → Secrets and variables → Actions |
| Cuentas de Render, Aiven y Auth0 | En cada proveedor, con 2FA |

`render.yaml` declara las variables secretas con `sync: false`, que significa «sin valor en el
archivo». [`.env.example`](../../.env.example) documenta todas las variables; el `.env` real
está en `.gitignore`. Las credenciales que sí aparecen en `compose.yaml` y en la CI son las de
contenedores locales y efímeros, y se discuten en
[análisis estático](../calidad/analisis-estatico.md#6-credenciales-de-base-de-datos-en-el-repositorio--aceptado).

Si un secreto se filtra: se rota en el proveedor, se actualiza en Render y se vuelve a
desplegar. Borrarlo de un commit no basta: sigue en el historial.

## 8. SonarCloud

1. En SonarCloud, organización `isco-utb`: *Analyze new project* → `ISCOUTB_AS_202620_uniTeam`.
2. *Administration → Analysis Method*: **desactivar Automatic Analysis**. Si sigue activo, el
   análisis desde la CI falla.
3. *My Account → Security*: generar un token y guardarlo en GitHub como secreto `SONAR_TOKEN`.
   **Nunca** en un chat, un commit o un documento.
4. En el siguiente push, el trabajo «Análisis estático (SonarCloud)» de la CI ejecuta el
   análisis con la cobertura de las pruebas y **espera al Quality Gate**: si falla, la CI falla.

Panel público: <https://sonarcloud.io/summary/overall?id=ISCOUTB_AS_202620_uniTeam>

## 9. Protección de `master`

Para que un fallo **bloquee la integración** y no solo la avise, en GitHub → *Settings →
Branches → Add rule* para `master`: *Require status checks to pass before merging*, marcando
«Pruebas contra MySQL», «Compilación del frontend», «Construcción de las imágenes» y «Análisis
estático (SonarCloud)». Lo tiene que activar un administrador del repositorio.
