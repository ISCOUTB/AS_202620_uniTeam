# 11. Modelado de amenazas y riesgos aceptados

El registro aplica STRIDE a los contenedores y flujos del [C4 nivel 2](../c4/nivel2-contenedores.md),
no a una lista genérica. La [arquitectura de seguridad, arc42 §8.4](08-arquitectura-de-seguridad.md)
describe los controles y datos; esta sección registra prioridad, responsable y estado de cada
mitigación. La matriz y evidencia de ejecución están en
[Evidencia S13](../entregas/S13-modelado-amenazas.md).

## Registro STRIDE

| Prioridad | STRIDE | Elemento C4 afectado | P | I | Riesgo y mitigación asignada | Responsable | Estado |
|---:|---|---|---:|---:|---|---|---|
| 1 | Tampering | Aplicación Web (Next.js), API y sus dependencias | 2 | 3 | Una dependencia vulnerable puede alterar el artefacto o afectar disponibilidad/confidencialidad. En la revisión inicial, `pip-audit` reportó 46 registros de avisos en `cryptography`, `PyJWT` y `Starlette`; `npm audit` reportó 3 avisos (1 crítico, 2 altos) en el árbol web. Se actualizaron FastAPI/Starlette, `cryptography`, PyJWT, Next.js y PostCSS; el lock web corrigió también `source-map-js`. La CI ahora bloquea avisos Python y avisos web altos/críticos. | Equipo de plataforma/CI | **Hecha** en los manifiestos y locks; escáner agregado a CI, run pendiente. |
| 2 | Spoofing | Navegador/Aplicación Web → API; Proveedor de identidad | 2 | 3 | Robo del token del usuario permitiría actuar como él. Mitigar con OIDC, `PKCE S256` y `state`; la API verifica firma, emisor, audiencia, caducidad y `sub`. El token sigue legible por JavaScript en `sessionStorage`; una sesión/BFF con cookie `HttpOnly` queda como alternativa estructural. | Equipo Web/API | Validaciones OIDC y PKCE **hechas**; exposición XSS **aceptada temporalmente** conforme a ADR-005; cambio a BFF **pendiente de decisión y ADR**. |
| 3 | Information Disclosure | API → MySQL → Estudiante, líder o profesor | 2 | 3 | Un fallo de autorización o una respuesta almacenada fuera de su ámbito puede exponer correos, membresías o tareas. La API consulta pertenencia por operación y no existe caché de negocio. Implementar `Cache-Control: private, no-store` en respuestas de negocio y conservar pruebas negativas por proyecto. | Equipo API | Comprobación de pertenencia y ausencia de caché de negocio **hechas**; encabezado `no-store` **pendiente**. |
| 4 | Tampering / Elevation of Privilege | API → MySQL (proyectos, membresías y tareas) | 2 | 3 | Un miembro podría cambiar tareas ajenas o elevar su rol manipulando solicitudes. Mitigar validando entradas, comprobando pertenencia en cada operación y reservando operaciones de líder al rol correspondiente; mantener pruebas negativas de autorización. | Equipo API | **Hecha** en el flujo actual y cubierta por pruebas de integración/robustez. |
| 5 | Elevation of Privilege | API (configuración `AUTH_DISABLED`) | 1 | 3 | Una variable de modo demo activada en producción aceptaría una identidad fija y anularía autenticación. El valor predeterminado es `0` y la imagen de API no incluye el emisor de desarrollo; añadir una validación de arranque que rechace el modo demo con `ENTORNO=produccion`. | Equipo de despliegue/API | Valores por defecto y exclusión del emisor **hechos**; guardia explícita de configuración **pendiente**. |
| 6 | Repudiation | API → MySQL (Auditoría) | 2 | 2 | `BusEventos.publicar` registra y absorbe excepciones de consumidores; una operación de negocio puede terminar sin su fila de auditoría. Mantener el log de error y decidir si la auditoría debe ser transaccional/durable; si se elige outbox u otro componente, registrar ADR antes del cambio. | Equipo API | La excepción se registra **hecho**; la pérdida de un evento se **acepta temporalmente** para el prototipo; durabilidad reforzada **pendiente** de requisito y ADR. |
| 7 | Denial of Service | Aplicación Web → API → MySQL y Proveedor de identidad | 2 | 2 | Tráfico automatizado puede consumir la cuota de cómputo, MySQL o la consulta JWKS. Paginación y límites de entradas reducen trabajo por solicitud y `/health`/métricas facilitan observación; no hay rate limiting dedicado. | Equipo de operación | Límites y señales operativas **hechos**; rate limiting **aceptado como riesgo** por el alcance académico, bajo volumen esperado e infraestructura gratuita; reevaluar si se abre el registro o aumenta el uso. |

## Riesgos aceptados y motivo

1. **Token en `sessionStorage` (riesgo 2).** Se conserva el cliente OIDC estático previsto por el
   C4. PKCE, `state`, el alcance por pestaña y la validación completa en la API reducen riesgos,
   pero no impiden que un XSS lea el token. Un BFF/cookie `HttpOnly` cambia el flujo y agrega una
   estructura de sesión; el equipo no la adopta sin escenario de calidad que la justifique.
   [ADR-005](../adr/0005-delegar-la-autenticacion-en-un-proveedor-oidc.md) registra el compromiso.
2. **Pérdida de auditoría por fallo del consumidor (riesgo 6).** El bus en proceso no es durable y
   no se incorpora infraestructura de cola solo para el prototipo. El error queda en logs y el
   flujo exitoso está probado; se reabre si la institución exige trazabilidad durable o si las
   pruebas/operación revelan pérdidas. No equivale a declarar satisfecha una obligación legal.
3. **Denegación de servicio sin rate limiting (riesgo 7).** Los usuarios previstos son equipos de
   curso y la infraestructura tiene límites gratuitos; paginación, validación y métricas son las
   mitigaciones de alcance actual. Se acepta el riesgo residual hasta que haya uso público o un
   escenario de disponibilidad que exija cuotas, protección perimetral o capacidad adicional.

## Componente generativo

UniTeam no incorpora un modelo ni un servicio generativo en producción. [ADR-014](../adr/0014-no-incorporar-un-componente-generativo.md)
lo descarta; por ello, inyección de prompt, fuga hacia un modelo y envenenamiento del contexto no
son flujos actuales. Antes de añadir IA generativa debe reabrirse el ADR y modelar esos tres riesgos
sobre los datos que saldrían del sistema.

