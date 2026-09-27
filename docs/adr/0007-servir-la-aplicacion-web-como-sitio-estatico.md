# ADR-007 — Servir la Aplicación Web como sitio estático en Render

- **Estado:** Aceptada
- **Fecha:** 2026-09-27
- **Decisores:** Equipo de desarrollo (I-04)
- **Pieza:** Aplicación Web (sitio) — contenedor «Aplicación Web» del [C4 nivel 2](../c4/nivel2-contenedores.md)
- **Relacionada:** [ADR-002](0002-usar-fastapi-y-nextjs.md), [ADR-008](0008-desplegar-la-api-como-contenedor-en-render.md)

## Contexto

La Aplicación Web es Next.js, pero **no hace nada en el servidor**: todas sus páginas son
componentes de cliente que, ya en el navegador, llaman a la API con el token del usuario. Hasta
ahora se ejecutaba con `next start`, un proceso Node.js que solo servía ficheros.

Restricciones que deciden: costo cero y sin tarjeta ([arc42 §2](../arc42/arc42-uniteam.md#2-restricciones),
T3), y [ESC-01](../calidad/escenarios-calidad.md#esc-01), que pide el tablero en ≤ 2 s en el p95.
Un proceso que se duerme por inactividad añade su arranque en frío a la primera carga del día.

## Alternativas

| | A. Sitio estático en CDN (**elegida**) | B. Servicio web Node.js (`next start`) |
|---|---|---|
| Qué se ejecuta | Nada: ficheros servidos desde el CDN del proveedor | Un proceso Node.js permanente |
| Arranque en frío | No hay | ~1 min tras 15 min sin tráfico en la capa gratuita de Render |
| Horas de instancia | No consume | Consume de las 750 h/mes del espacio de trabajo, que comparte con la API |
| Costo al volumen supuesto | 0 USD | 0 USD mientras quepan las horas; 7 USD/mes (Starter) para no dormirse |
| Cambio en el código | Exportación estática; el tablero pasa de `/proyectos/[id]` a `/proyecto/?id=` | Ninguno |

**Por qué se descarta B.** Por dos motivos técnicos, no de preferencia: compite con la API por
las mismas 750 horas de instancia —dos servicios siempre activos suman ~1 488 h y agotan la
capa gratuita a mitad de mes—, y su arranque en frío rompe ESC-01 en la primera visita. Y lo
que aporta, renderizar en el servidor, esta aplicación no lo usa.

Se consideró también Vercel, el proveedor natural de Next.js. Se descarta por sumar una cuenta
y una integración con la organización de GitHub más, cuando Render ya aloja la API y ofrece lo
mismo para ficheros estáticos.

## Capa gratuita verificada

Consultada el 2026-09-27 en la documentación de Render
([Deploy for Free](https://render.com/docs/free)): los sitios estáticos son gratuitos, se
sirven desde CDN con HTTPS y **no se duermen ni consumen horas de instancia**. El espacio de
trabajo Hobby incluye **100 GB/mes de ancho de banda de salida** y **500 minutos de
compilación**, compartidos con la API.

**Pendiente de confirmar al crear la cuenta:** si Render pide tarjeta en el registro. Las
fuentes consultadas no coinciden; el resultado se anota en la
[guía de despliegue](../despliegue/guia.md#1-cuentas).

## Decisión

El sitio se compila con `output: "export"` a `web/out/` y Render lo sirve como sitio estático,
declarado en [`render.yaml`](../../render.yaml). Las variables `NEXT_PUBLIC_*` se hornean al
compilar. Localmente, `docker compose up` sirve la misma compilación con nginx.

## Consecuencias

- **Costo:** 0 USD/mes. El punto de ruptura es el ancho de banda: el sitio completo pesa 221 KB
  comprimido; la capa gratuita se agota hacia las **450 000 primeras cargas al mes**
  ([costos](../despliegue/costos.md)). Pasado ese punto, 15 USD por cada 100 GB.
- **Rendimiento:** la primera carga no espera a ningún proceso; el tiempo de ESC-01 lo decide la
  API.
- **Limitación aceptada:** el sitio no puede tener rutas que dependan del servidor. Si en el
  futuro hiciera falta renderizar en el servidor, esta decisión se revisa.
- **URL del tablero:** `/proyecto/?id=<id>`. Los enlaces antiguos a `/proyectos/<id>` dejan de
  existir; no había usuarios que los tuvieran guardados.

## Reversión

Quitar `output: "export"` de `web/next.config.mjs` y cambiar en `render.yaml` el servicio a
`runtime: node` con `startCommand: npm start`. Es un cambio de configuración de dos archivos.

## Trazabilidad

[`web/next.config.mjs`](../../web/next.config.mjs) · [`render.yaml`](../../render.yaml) ·
[arc42 §7](../arc42/arc42-uniteam.md#7-vista-de-despliegue) · [ESC-01](../calidad/escenarios-calidad.md#esc-01)
