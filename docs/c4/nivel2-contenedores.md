# C4 - Nivel 2: Diagrama de contenedores 

Abre la caja de UniTeam del nivel 1 y muestra sus contenedores: las unidades independientes  que lo componen
(aplicación web, API y base de datos), cómo se comunican entre si y con los sistemas externos ya identificados.
El nivel 2 responde a *como esta construido el sistema a alto nivel*, por eso aparece la tecnología concreta - 
la seleccionada en
[ADR-001](../adr/001-seleccion-de-stack.md).

## Diagrama

```mermaid
flowchart TB
 subgraph sys["UniTeam [Sistema de software]"]
    direction TB
        web["<b>Aplicación Web</b><br><i>[Contenedor: Next.js]</i><br>Interfaz donde los usuarios crean, asignan y consultan tareas."]
        api["<b>API</b><br><i>[Contenedor: FastAPI]</i><br>Expone la lógica de negocio: tareas, proyectos, prioridades y estados."]
        db["<b>Base de datos</b><br><i>[Contenedor: MySQL]</i><br>Almacena usuarios, proyectos, tareas y su historial."]
  end
    est["<b>Estudiante integrante</b><br><i>[Persona]</i>"] -- Usa (HTTPS) --> web
    lid["<b>Líder de equipo</b><br><i>[Persona]</i>"] -- Usa (HTTPS) --> web
    pro["<b>Profesor</b><br><i>[Persona]</i>"] -- Usa (HTTPS) --> web
    web -- Llama (REST/JSON) --> api
    api -- Lee y escribe (SQL) --> db
    api -- Delega autenticación --> idp["<b>Proveedor de identidad</b><br><i>[Externo — previsto]</i>"]
    api -- Envía invitaciones y avisos --> mail["<b>Servicio de correo</b><br><i>[Externo — previsto]</i>"]

    est@{ shape: rect}
    lid@{ shape: rect}
    pro@{ shape: rect}
     web:::contenedor
     api:::contenedor
     db:::contenedor
     est:::persona
     lid:::persona
     pro:::persona
     idp:::externo
     mail:::externo
    classDef persona fill:#08427b,stroke:#052e56,color:#ffffff
    classDef contenedor fill:#1168bd,stroke:#0b4884,color:#ffffff
    classDef externo fill:#6b6b6b,stroke:#4d4d4d,color:#ffffff
    classDef limite fill:none,stroke:#1168bd,stroke-dasharray: 4 3,color:#1168bd

    class est,lid,pro persona
    class web,api,db contenedor
    class idp,mail externo
    class sys limite
```

## Leyenda

| Color | Significado |
|-------|-------------|
| Azul oscuro | Persona: usuario del sistema. |
| Azul | Contenedor: unidad de despliegue dentro del alcance de este proyecto. |
| Gris | Sistema externo, fuera del control del equipo. |

## Contenedores

| Contenedor | Tecnología | Responsabilidad |
|------------|-----------|------------------|
| Aplicación Web | Next.js | Interfaz donde los usuarios crean, asignan y consultan tareas. Único punto de entrada para los tres actores. |
| API | FastAPI | Expone la lógica de negocio: tareas, proyectos, prioridades y estados. Única puerta de acceso a la base de datos y a los sistemas externos. |
| Base de datos | MySQL | Almacena usuarios, proyectos, tareas y su historial. |

## Relaciones

| Origen | Destino | Descripción | Protocolo |
|--------|---------|-------------|-----------|
| Estudiante, Líder de equipo, Profesor | Aplicación Web | Uso de la interfaz | HTTPS |
| Aplicación Web | API | Consumo de la lógica de negocio | REST/JSON |
| API | Base de datos | Persistencia de datos | SQL |
| API | Proveedor de identidad | Delegación de autenticación | — (previsto) |
| API | Servicio de correo | Envío de invitaciones y avisos | — (previsto) |

## Sistemas externos

Se mantienen los mismos identificados en el [nivel 1 — contexto](./nivel1-contexto.md), ambos
marcados como **previstos**.

| Sistema | Para qué se usa |
|---------|----------------|
| Proveedor de identidad | Autenticación de los usuarios mediante cuenta institucional o de Google. |
| Servicio de correo electrónico | Invitaciones a un proyecto y avisos de fechas límite. |

## Fuera del alcance

- División de la API en microservicios: en el prototipo se mantiene como un único contenedor
  monolítico (ver [ADR-001](../adr/ADR-001-seleccion-de-stack.md)).
- Caché o cola de mensajería independiente: no hay un contenedor dedicado a esto en esta
  entrega; `events/` vive dentro del contenedor API (ver nivel 3 — componentes).
- Balanceo de carga o réplicas de base de datos: no aplican a un prototipo académico.
