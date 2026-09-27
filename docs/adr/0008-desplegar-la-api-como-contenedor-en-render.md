# ADR-008 — Desplegar la API como contenedor en Render

- **Estado:** Aceptada
- **Fecha:** 2026-09-27
- **Decisores:** Equipo de desarrollo (I-04)
- **Pieza:** API — contenedor «API» del [C4 nivel 2](../c4/nivel2-contenedores.md)
- **Relacionada:** [ADR-003](0003-usar-eventos-de-dominio-en-proceso.md), [ADR-006](0006-estilo-sincrono-con-eventos-en-proceso.md), [ADR-009](0009-usar-aiven-for-mysql-como-base-de-datos-gestionada.md)

## Contexto

La API es un proceso FastAPI que ya se empaqueta como imagen Docker. Tres propiedades suyas
deciden dónde puede ejecutarse:

- **Mantiene estado en memoria entre peticiones**: la caché de claves del proveedor de identidad
  (`app/api/seguridad.py`) y la ventana de latencias de ESC-01 (`app/observabilidad.py`).
- **Abre conexiones a MySQL** con un *pool* de SQLAlchemy.
- **Su escenario es ESC-01**: tablero en ≤ 2 s en el p95.

Y las restricciones de [arc42 §2](../arc42/arc42-uniteam.md#2-restricciones): costo cero y al
menos una alternativa sin tarjeta.

## Alternativas

| | A. Servicio web Docker en Render (**elegida**) | B. Función (FaaS: AWS Lambda, Vercel Functions) |
|---|---|---|
| Qué se ejecuta | La misma imagen que `docker compose up`, sin cambios | La API troceada en funciones, con un adaptador ASGI |
| Estado en memoria | Se conserva mientras la instancia vive | Se pierde entre invocaciones frías |
| Conexiones a MySQL | Un *pool* por instancia | Una conexión por invocación concurrente; agota las del plan gratuito de la BD |
| Arranque en frío | ~1 min tras 15 min sin tráfico (capa gratuita) | Del orden de segundos por invocación fría, con PyJWT y SQLAlchemy cargando |
| Tarjeta | Ver abajo | AWS exige tarjeta |

**Por qué se descarta B.** Las tres propiedades de la API la descalifican como función: perdería
la caché de claves en cada arranque frío —una descarga del JWKS del proveedor por petición—, el
*pool* de conexiones dejaría de tener sentido y agotaría las conexiones de la base de datos
gratuita, y AWS Lambda exige tarjeta. La ficha pide contrastar el arranque en frío de una función
con el p95 medido; no se midió porque las otras dos causas la descartan antes.

## Capa gratuita verificada

Consultada el 2026-09-27 en la documentación de Render
([Deploy for Free](https://render.com/docs/free)):

- **750 horas de instancia al mes** por espacio de trabajo; agotadas, el servicio se suspende
  hasta el mes siguiente, no se cobra.
- El servicio **se duerme tras 15 minutos sin tráfico** y tarda **alrededor de un minuto** en
  despertar.
- 512 MB de memoria por instancia.

**Pendiente de confirmar al crear la cuenta:** si Render pide tarjeta en el registro (las fuentes
no coinciden). Si la pide, la alternativa sin tarjeta es la misma imagen en el servidor del
laboratorio con `docker compose`, que la guía del curso garantiza; queda anotado en la
[guía de despliegue](../despliegue/guia.md#1-cuentas).

## Decisión

La API se despliega como servicio web Docker en Render, región Virginia, a partir del destino
`api` del [`Dockerfile`](../../Dockerfile) —que no incluye el emisor OIDC de desarrollo—. Lo
declara [`render.yaml`](../../render.yaml), con:

- `healthCheckPath: /health`, que exige respuesta de la base de datos: una versión que no alcanza
  MySQL nunca sustituye a la que funciona;
- `autoDeployTrigger: checksPass`: solo se despliega un commit con la CI en verde;
- todos los secretos con `sync: false`, guardados en la configuración de Render.

## Consecuencias

- **Costo:** 0 USD/mes. Una instancia siempre despierta son 720–744 h al mes: cabe en las 750 h
  **solo si es el único servicio que consume horas**, que es otra razón del
  [ADR-007](0007-servir-la-aplicacion-web-como-sitio-estatico.md).
- **ESC-01 no se cumple en la primera petición tras 15 minutos de inactividad.** El arranque de
  ~1 min supera el umbral de 2 s. Con uso continuo sí se cumple, y la métrica
  `/metricas/esc-01` lo muestra. **Este es el punto de ruptura:** cuando el primer acceso del día
  tenga que cumplir ESC-01, la API pasa al plan Starter, **7 USD/mes**, que no se duerme.
- Se descartó mantener la instancia despierta con peticiones periódicas desde un cron externo:
  consume las mismas horas, depende de un planificador sin garantía de puntualidad y roza las
  condiciones de uso del proveedor.
- **Una sola instancia**, sin redundancia: coherente con la renuncia a alta disponibilidad
  aceptada en el árbol de utilidad (D-004).

## Reversión

Cada despliegue en Render conserva los anteriores: *Dashboard → uniteam-api → Events → Rollback*
vuelve a la imagen previa en un clic, sin recompilar. Para abandonar el proveedor, la misma
imagen corre en cualquier sitio con Docker (`docker compose up`); la única configuración está en
variables de entorno. Procedimiento en la [guía](../despliegue/guia.md#6-reversión).

## Trazabilidad

[`Dockerfile`](../../Dockerfile) · [`render.yaml`](../../render.yaml) ·
[`app/main.py`](../../app/main.py) (`/health`) · [arc42 §7](../arc42/arc42-uniteam.md#7-vista-de-despliegue) ·
[ESC-01](../calidad/escenarios-calidad.md#esc-01) · [costos](../despliegue/costos.md)
