# C4 — Nivel 2: Diagrama de contenedores

Descompone UniTeam en las unidades desplegables que lo forman. A diferencia del
[nivel 1](nivel1-contexto.md), este nivel sí lleva tecnología: la fijan
[0002 — Usar FastAPI y Next.js](../adr/0002-usar-fastapi-y-nextjs.md) y
[0004 — Usar MySQL](../adr/0004-usar-mysql-como-base-de-datos.md).

## Diagrama

```mermaid
flowchart LR
    est["<b>Estudiante integrante</b><br/><i>[Persona]</i>"]
    lid["<b>Líder de equipo</b><br/><i>[Persona]</i>"]
    pro["<b>Profesor</b><br/><i>[Persona]</i>"]

    subgraph sys["UniTeam · Sistema de software"]
        web["<b>Aplicación Web</b><br/><i>[Contenedor: Next.js]</i><br/>Interfaz de usuario"]
        api["<b>API</b><br/><i>[Contenedor: FastAPI]</i><br/>Lógica de negocio y autorización"]
        db[("<b>Base de datos</b><br/><i>[Contenedor: MySQL]</i><br/>Datos y auditoría")]
    end

    idp["<b>Proveedor de identidad</b><br/><i>[Sistema externo]</i>"]
    mail["<b>Servicio de correo</b><br/><i>[Sistema externo]</i>"]

    est -->|"Usa (HTTPS)"| web
    lid -->|"Usa (HTTPS)"| web
    pro -->|"Consulta (HTTPS)"| web
    web -->|"REST/JSON"| api
    api -->|"SQL"| db
    api -->|"Valida el token (OIDC)"| idp
    api -->|"Invitaciones y avisos"| mail
    web -->|"Inicia sesión (OIDC)"| idp

    classDef persona fill:#08427b,stroke:#052e56,color:#ffffff
    classDef contenedor fill:#1168bd,stroke:#0b4884,color:#ffffff
    classDef almacen fill:#0e5595,stroke:#083a6d,color:#ffffff
    classDef externo fill:#737b85,stroke:#4d4d4d,color:#ffffff

    class est,lid,pro persona
    class web,api contenedor
    class db almacen
    class idp,mail externo
    style sys fill:none,stroke:#9aa4b2,stroke-dasharray: 7 5,color:#8a94a3
    linkStyle default stroke:#8a94a3,stroke-width:1.5px
```

## Leyenda

| Color | Significado |
|-------|-------------|
| Azul oscuro | Persona que usa el sistema. |
| Azul | Contenedor: unidad desplegable dentro del alcance del proyecto. |
| Gris | Sistema externo, fuera del control del equipo. |

## Relaciones

| Origen | Destino | Descripción | Protocolo |
|--------|---------|-------------|-----------|
| Estudiante, Líder de equipo, Profesor | Aplicación Web | Uso de la interfaz | HTTPS |
| Aplicación Web | Proveedor de identidad | Inicio de sesión del usuario (código + PKCE) | OIDC |
| Aplicación Web | API | Consumo de la lógica de negocio | REST/JSON |
| API | Proveedor de identidad | Descarga del JWKS y validación del token | OIDC |
| API | Base de datos | Persistencia y registro de auditoría | SQL |
| API | Servicio de correo | Invitaciones y avisos de fecha límite | *(previsto)* |

## Correspondencia con el nivel 1

Las tres personas y los dos sistemas externos del [nivel 1](nivel1-contexto.md) reaparecen aquí
sin cambios; lo que el nivel 1 dibujaba como una caja única —UniTeam— se abre en tres
contenedores. No hay ningún elemento en este diagrama que no exista en el de contexto.

## Correspondencia con el código

Cada contenedor tiene su lugar en el repositorio. Es lo primero que se contrasta en el corte:

| Contenedor | Tecnología | Dónde vive en el repositorio |
|-----------|-----------|------------------------------|
| Aplicación Web | Next.js | `web/app/` — páginas de proyectos y tablero; `web/lib/api.ts` — cliente de la API. |
| API | FastAPI | `app/main.py`, `app/api/`, `app/application/`, `app/domain/`, `app/events/` |
| Base de datos | MySQL | `app/infrastructure/` — esquema en `tablas.py`, acceso en `repositorios.py` |

## Nota sobre los eventos de dominio

[0003](../adr/0003-usar-eventos-de-dominio-en-proceso.md) elige un estilo orientado a eventos.
Ese estilo **no aparece como contenedor** porque se aplica **en proceso**: el despacho ocurre
dentro de la API (`app/application/bus.py`), sin broker ni cola externa. Añadir un componente de
mensajería restaría margen a [ESC-04](../calidad/escenarios-calidad.md#esc-04) e implicaría
infraestructura que la restricción T3 no contempla. Productores y consumidores son estructura
interna de la API y corresponden al nivel 3.

## Nota sobre el flujo de autenticación

El navegador se redirige al proveedor de identidad (OIDC) y la API se limita a validar el token
recibido: las credenciales **nunca pasan por UniTeam**, lo que reduce el alcance de la
restricción legal L1 y la superficie de riesgo de
[ESC-03](../calidad/escenarios-calidad.md#esc-03).

**Estado actual:** implementado ([ADR 0005](../adr/0005-delegar-la-autenticacion-en-un-proveedor-oidc.md)).
La Aplicación Web ejecuta el flujo de código de autorización con PKCE (`web/lib/oidc.ts`) y
envía el token en `Authorization: Bearer`; la API lo verifica en cada petición contra el JWKS
del emisor (`app/api/seguridad.py`). La identidad sale del token, no de lo que declare el
cliente.

Autenticar no es autorizar: estar autenticado no da acceso a un proyecto ajeno. La pertenencia
se sigue comprobando contra la base de datos en cada operación, y ese es el mecanismo que
sostiene [ESC-03](../calidad/escenarios-calidad.md#esc-03).

**Proveedor pendiente.** Todavía no se ha elegido entre la cuenta institucional y Google. Para
desarrollo se usa un emisor mínimo (`scripts/emisor_dev.py`) que habla el protocolo pero **no
autentica a nadie**; existe para que el sistema arranque sin cuentas externas.

Como la Aplicación Web se ejecuta en el navegador del usuario, la relación «Aplicación Web →
API» es una petición entre orígenes distintos y necesita CORS. La lista de orígenes es
explícita (`ORIGENES_PERMITIDOS`), nunca `*`.
