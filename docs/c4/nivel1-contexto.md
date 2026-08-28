# C4 — Nivel 1: Diagrama de contexto del sistema

Muestra a UniTeam como una caja negra, quién lo usa y con qué sistemas externos se relaciona.
El nivel 1 responde a *qué hace el sistema y para quién*, no a *cómo está construido*: por eso
**no aparece ninguna tecnología** en el diagrama. La elección del stack se documentará en
[ADR-001](../adr/ADR-001-seleccion-de-stack.md) y afectará a partir del nivel 2 (contenedores).

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
| Azul | Sistema en construcción, alcance de este proyecto. |
| Gris | Sistema externo, fuera del control del equipo. |

## Actores

| Actor | Descripción | Interesado |
|-------|-------------|-----------|
| Estudiante integrante | Miembro de un equipo de trabajo universitario. Usa UniTeam para saber qué le corresponde y reportar su avance. | [I-01](../calidad/interesados.md) |
| Líder de equipo | Estudiante que coordina el proyecto. No es un rol administrativo distinto, sino un integrante con permisos de gestión del proyecto. | [I-02](../calidad/interesados.md) |
| Profesor | Consulta el avance de los equipos. Su acceso es de solo lectura. | [I-03](../calidad/interesados.md) |

## Sistemas externos

Ambos están marcados como **previstos**: son parte del alcance planeado, pero todavía no se
ha seleccionado el proveedor concreto ni se ha implementado la integración.

| Sistema | Para qué se usa | Por qué es externo |
|---------|----------------|--------------------|
| Proveedor de identidad | Autenticación de los usuarios mediante cuenta institucional o de Google. | Construir un manejo propio de contraseñas aumentaría el riesgo de ESC-03 y el trabajo de cumplimiento de la restricción L1, sin aportar valor al problema que UniTeam resuelve. |
| Servicio de correo electrónico | Invitaciones a un proyecto y avisos de fechas límite. | Entregar correo de forma confiable es un problema resuelto por terceros y ajeno al dominio del proyecto. |

## Fuera del alcance

Lo siguiente **no** forma parte del sistema y por lo tanto no aparece en el diagrama:

- Aplicación móvil nativa. El prototipo se entrega para **navegador web y/o escritorio**
  (restricción T2).
- Integración con plataformas institucionales de aprendizaje o con el sistema de
  calificaciones de la universidad.
- Mensajería o chat entre integrantes: UniTeam organiza tareas, no reemplaza el canal de
  comunicación del equipo.
- Registro de tiempo trabajado y facturación.
