# Modelado de amenazas y plan de mitigación (S13)

Método: STRIDE aplicado a los elementos del C4 de contenedores de UniTeam
(Navegador → Aplicación Web Next.js → API FastAPI → MySQL, más el proveedor OpenID Connect, ADR 0005).
Priorización: **puntaje = probabilidad (1-5) × impacto (1-5)**. Se atiende de mayor a menor.
Estado del documento: revisado el 2026-11-01. Arquitectura de seguridad en [arc42 §8](../arc42/08-conceptos-transversales-seguridad.md); riesgos aceptados en [arc42 §11](../arc42/11-riesgos-amenazas-aceptadas.md).

## 1. Tabla de amenazas (ordenada por prioridad)

| ID | Elemento C4 | STRIDE | Amenaza | P | I | Pts | Mitigación asignada | Dueño | Estado | ADR |
|----|-------------|--------|---------|---|---|-----|---------------------|-------|--------|-----|
| T1 | API | Elevación de privilegios | Un usuario autenticado lee o modifica tareas de un equipo al que no pertenece (IDOR por `id` de tarea o equipo) | 4 | 5 | 20 | Capa única de autorización que verifica pertenencia al equipo en cada endpoint; pruebas negativas por endpoint | Julio César Emiliani | Pendiente | [0010](../adr/0010-autorizacion-por-equipo.md) |
| T2 | API ↔ Proveedor OIDC | Suplantación | Token falsificado, vencido o emitido por el emisor de desarrollo aceptado en producción | 3 | 5 | 15 | Validar firma (JWKS), `iss`, `aud` y `exp`; emisor de desarrollo solo con bandera de entorno explícita | Ian Novoa Carrillo | Pendiente | ADR 0005 |
| T3 | MySQL | Divulgación de información | Credenciales por defecto (`uniteam:uniteam`) y puerto 3306 accesible fuera de la red de la API | 3 | 5 | 15 | Credenciales por variable de entorno/secreto, usuario con mínimo privilegio, puerto no publicado en despliegue | Daniel Isaac Manjarres | Pendiente | — |
| T4 | Aplicación Web ↔ Navegador | Divulgación de información | Un XSS roba el token de sesión si se guarda en almacenamiento accesible por JS | 3 | 4 | 12 | Cabeceras CSP y escapado de salida; decidir dónde se almacena el token | Juan Jose Bustamante | Pendiente | [0011](../adr/0011-proteccion-sesion-navegador.md) |
| T5 | Aplicación Web | Manipulación | XSS almacenado en título o descripción de tareas | 4 | 3 | 12 | Validación y longitud máxima en la API; escapado al renderizar (sin `dangerouslySetInnerHTML`) | Juan Jose Bustamante | Pendiente | — |
| T6 | Repositorio / CI | Manipulación | Dependencia vulnerable o secreto en el historial (repositorio público) | 3 | 4 | 12 | `pip-audit` y `npm audit` en CI, Dependabot, barrido de secretos antes de cada entrega | Ian Novoa Carrillo | Hecha (workflow `seguridad.yml`; hallazgos en `dependencias.md`) | — |
| T7 | API → MySQL | Manipulación | Inyección SQL | 2 | 5 | 10 | Consultas parametrizadas vía ORM/driver; prohibido concatenar SQL | Daniel Isaac Manjarres | Pendiente (verificar en revisión de código) | — |
| T8 | API | Denegación de servicio | Ráfagas de peticiones sin límite agotan la API o la base de datos | 3 | 3 | 9 | Límite de peticiones por usuario/IP | Julio César Emiliani | Pendiente | [0012](../adr/0012-limite-de-peticiones.md) |
| T9 | API ↔ Aplicación Web | Divulgación de información | CORS permisivo permite que otros orígenes llamen a la API con la sesión del usuario | 3 | 3 | 9 | Lista blanca de orígenes por entorno | Ian Novoa Carrillo | Pendiente | — |
| T10 | API | Repudio | No queda registro de quién cambió responsable o estado de una tarea | 3 | 2 | 6 | Registro de auditoría de cambios | Julio César Emiliani | Aceptada como riesgo (ver arc42 §11) | — |
| T11 | API | Divulgación de información | Tokens o correos aparecen en los logs | 2 | 3 | 6 | Filtrar `Authorization` y correos en el logging | Daniel Isaac Manjarres | Pendiente | — |

## 2. Orden de ataque del plan

El plan se ejecuta por puntaje: T1 → T2 → T3 → T4/T5/T6 → T7 → T8/T9 → T10/T11.
T6 se resolvió primero por ser de bajo costo (solo CI); T10 se acepta porque su impacto es bajo (2) frente al costo de implementar auditoría completa.
Cada cambio de estado debe verse en el historial de commits; los commits de T1-T3 preceden a los de T8-T11.

## 3. Componente generativo

UniTeam no invoca ningún modelo de lenguaje en tiempo de ejecución: el uso de IA es de apoyo al desarrollo (`docs/ia.md`) y no procesa datos de usuarios.
Por tanto no aplican inyección de prompt, fuga de datos vía modelo ni envenenamiento de contexto.
**Si en el futuro se incorpora un componente generativo**, se deberá abrir un ADR y modelar esos tres riesgos.

## 4. Análisis de dependencias

Ver [dependencias.md](dependencias.md) y el workflow [`seguridad.yml`](../../.github/workflows/seguridad.yml).

## 5. Privacidad

Ver [privacidad.md](privacidad.md).
