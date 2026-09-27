# ADR-009 — Usar Aiven for MySQL como base de datos gestionada

- **Estado:** Aceptada
- **Fecha:** 2026-09-27
- **Decisores:** Equipo de desarrollo (I-04)
- **Pieza:** Base de datos — contenedor «Base de datos» del [C4 nivel 2](../c4/nivel2-contenedores.md)
- **Relacionada:** [ADR-004](0004-usar-mysql-como-base-de-datos.md), que eligió el motor; este decide dónde se ejecuta

## Contexto

[ADR-004](0004-usar-mysql-como-base-de-datos.md) fijó MySQL como motor. Falta decidir dónde se
ejecuta en el entorno desplegado. Lo que pesa:

- **Disco persistente.** Es la única pieza con estado duradero; [ESC-04](../calidad/escenarios-calidad.md#esc-04)
  compromete 0 escrituras confirmadas perdidas.
- **Costo cero y sin tarjeta** ([arc42 §2](../arc42/arc42-uniteam.md#2-restricciones)).
- **Volumen pequeño**: el escenario de mayor carga es un proyecto de 200 tareas
  ([ESC-01](../calidad/escenarios-calidad.md#esc-01)).

## Alternativas

| | A. Aiven for MySQL, plan Free (**elegida**) | B. MySQL en un contenedor junto a la API |
|---|---|---|
| Motor | MySQL 8, el mismo de la CI y de `compose.yaml` | MySQL 8 |
| Disco | Persistente y gestionado, con copias de seguridad automáticas | Efímero: los servicios gratuitos de Render no tienen disco persistente |
| Operación | Parches y copias los hace el proveedor | A cargo del equipo |
| Tarjeta | No la pide | — |
| Costo | 0 USD | 0 USD, pero pierde los datos en cada despliegue |

**Por qué se descarta B.** En la capa gratuita de Render el disco de un servicio es efímero: cada
despliegue o reinicio borra la base de datos. Eso viola ESC-04 por construcción, no por
accidente. Un disco persistente en Render es de pago.

También se consideraron **Render Postgres gratuito**, que caduca a los 30 días y obligaría a
cambiar de motor contra el ADR-004, y **TiDB Cloud Serverless**, compatible con MySQL pero no
MySQL: las pruebas de la CI corren contra MySQL 8.4 y no demostrarían nada sobre TiDB.

## Capa gratuita verificada

Consultada el 2026-09-27 en la documentación de Aiven
([Aiven for MySQL free tier](https://aiven.io/docs/products/mysql/concepts/mysql-free-tier)):

- **Sin tarjeta** y sin límite de tiempo.
- **1 nodo, 1 GB de RAM y 1 GB de almacenamiento** (reducido de 5 GB en mayo de 2025).
- Sin alta disponibilidad; el servicio **se apaga tras un periodo de inactividad**, con aviso
  previo por correo, y se vuelve a encender desde la consola.
- Copias de seguridad automáticas incluidas.

## Decisión

La base de datos de producción es un servicio Aiven for MySQL, plan Free, en la costa este de
EE. UU. —la región más próxima a la API en Render Virginia—. La conexión va cifrada y
**verificando el certificado del servidor** contra la CA del proyecto de Aiven, que Render
monta como *Secret File*:

```
DATABASE_URL=mysql+pymysql://avnadmin:<clave>@<host>:<puerto>/defaultdb?ssl_ca=/etc/secrets/aiven-ca.pem
```

La URL entera es un secreto y vive solo en la configuración de Render.

## Consecuencias

- **Costo:** 0 USD/mes. El punto de ruptura no es el almacenamiento: al volumen supuesto la base
  de datos crece unos 4 MB al mes y el 1 GB dura años ([costos](../despliegue/costos.md)). Se
  rompe por **disponibilidad**: el plan Free no tiene SLA y se apaga por inactividad, así que no
  sostiene el 99 % mensual de ESC-04. El primer plan de pago (Developer) cuesta **5 USD/mes**; el
  que añade alta disponibilidad, bastante más. Se acepta mientras UniTeam sea un prototipo.
- **Seguridad:** tráfico cifrado con verificación de certificado; la contraseña no aparece en el
  repositorio ni en los logs.
- Aiven exige clave primaria en todas las tablas (`sql_require_primary_key`). Las cuatro tablas
  del esquema la tienen, así que `crear_esquema()` funciona sin cambios.

## Reversión

Aiven permite exportar con `mysqldump` usando la misma URL; el volcado se importa en cualquier
MySQL 8, incluido el de `docker compose`. La API no sabe dónde está la base de datos: cambiar de
proveedor es cambiar `DATABASE_URL` en Render.

## Trazabilidad

[`render.yaml`](../../render.yaml) · [`app/infrastructure/db.py`](../../app/infrastructure/db.py) ·
[arc42 §7](../arc42/arc42-uniteam.md#7-vista-de-despliegue) · [ESC-04](../calidad/escenarios-calidad.md#esc-04)
