# 8.4 Arquitectura de seguridad

Esta sección complementa [arc42 §8](arc42-uniteam.md#8-conceptos-transversales) con los
controles de seguridad que existen en los contenedores del C4, sus límites de confianza y los
datos que cruzan cada límite. El diagrama de referencia es [C4 nivel 2](../c4/nivel2-contenedores.md);
el [nivel 1](../c4/nivel1-contexto.md) identifica a estudiantes, líderes y profesores como actores.

## Límites de confianza y flujos

| Flujo del C4 | Datos y límite de confianza | Control actual y estado |
|---|---|---|
| Navegador → Aplicación Web | La interfaz se sirve como archivos estáticos por HTTPS. El navegador y su entorno no son de confianza. | Next.js usa `output: "export"` y nginx sirve `out/`; no hay servidor Next.js en producción. |
| Aplicación Web/navegador ↔ Proveedor de identidad | El navegador inicia OIDC con código de autorización, `PKCE S256` y `state`. El proveedor recibe la solicitud de inicio de sesión. | La aplicación comprueba `state` y el verificador PKCE. UniTeam no recibe ni almacena contraseñas. El proveedor concreto es externo. |
| Navegador → API | El token Bearer cruza una frontera pública. El navegador puede ser manipulado y no determina su propia identidad ni pertenencia. | CORS usa una lista explícita de orígenes. La API valida firma RS256, emisor, audiencia, caducidad y presencia de `sub`; obtiene la identidad del claim configurado. |
| API → Proveedor de identidad | La API obtiene el documento OIDC/JWKS por HTTP(S) desde configuración; las claves se cachean en memoria del proceso por 600 s. | El esquema de URL se limita a HTTP(S). Un token inválido se rechaza con 401. La configuración del emisor y la disponibilidad del proveedor siguen siendo dependencias externas. |
| API → MySQL | Proyectos, membresías, tareas y auditoría cruzan el límite de persistencia. MySQL es la fuente de verdad. | Las operaciones consultan la pertenencia y el rol en la base de datos; SQLAlchemy administra las transacciones. No existe caché de datos de negocio. |
| API → Servicio de correo | El C4 lo dibuja como sistema externo previsto. | La integración SMTP y el envío de avisos aún no están implementados; no es un flujo activo ni se configuran credenciales de correo. |

## Autorización e integridad

- Autenticación no equivale a autorización: cada operación sobre un proyecto comprueba la
  pertenencia; las operaciones reservadas comprueban además el rol de líder. La unidad de
  autorización es el proyecto.
- Los esquemas Pydantic limitan longitudes, tipos, enumeraciones y formatos antes de llegar a
  los repositorios. El cliente no puede asignar una identidad distinta a la del token validado.
- La auditoría persiste usuario, recurso, operación, resultado y momento. La observabilidad
  operativa no registra el correo ni el cuerpo de la petición y registra rutas como plantillas;
  la tabla de auditoría sí contiene el identificador de usuario y tiene acceso más restringido.
- `AUTH_DISABLED` tiene valor predeterminado `0`; el emisor de desarrollo no se incluye en la
  imagen de producción. Activar el modo demo fuera de una demostración controlada anula el
  control de identidad y está prohibido para usuarios reales.

## Confidencialidad, caché y sesión

El modelo persiste identificadores de usuario (por defecto, correos), membresías, nombres de
proyecto, títulos y atributos de tareas, y eventos de auditoría. El acceso a las vistas se limita
por pertenencia al proyecto y no se registran correos en los logs operativos. Los identificadores
personales y el contenido de proyectos no se deben enviar a terceros fuera de los flujos
documentados.

Las respuestas de proyectos, tareas, membresías y progreso no se cachean en el servidor; cada
lectura vuelve a MySQL. La política `Cache-Control: private, no-store` está propuesta en
[arc42 §8.2](arc42-uniteam.md#82-caché-e-invalidación), pero **todavía no está implementada** en
las respuestas. No se debe presentar la ausencia de caché de negocio como si ese encabezado ya
estuviera activo.

El token OIDC se conserva en `sessionStorage`, no en una cookie `HttpOnly`. Esto limita su
persistencia a la pestaña, pero código JavaScript ejecutado por un XSS podría leerlo. Adoptar un
BFF/sesión con cookie `HttpOnly` cambiaría el flujo y la estructura del contenedor web; no se ha
decidido. La decisión actual y su costo están registrados en
[ADR-005](../adr/0005-delegar-la-autenticacion-en-un-proveedor-oidc.md).

## Privacidad y base del tratamiento

El modelo confirma que UniTeam **sí trata datos personales**:

| Dato | Evidencia en el modelo/código | Finalidad | Base prevista y estado |
|---|---|---|---|
| Identificador OIDC (`sub`) y correo usado como identidad | Claim configurado en `app/config.py`; `MiembroTabla.usuario`, `TareaTabla.creada_por` y `TareaTabla.responsable` en `app/infrastructure/tablas.py`. | Identificar al integrante, autenticarlo y asignarle tareas dentro del proyecto. | Autorización previa, expresa e informada del titular, conforme a la restricción L1 de [arc42 §2.3](arc42-uniteam.md#23-restricciones-legales). El flujo de consentimiento y su evidencia no aparecen implementados en el repositorio. |
| Proyecto, título, prioridad, estado, responsable y fecha límite | `ProyectoTabla` y `TareaTabla` en `app/infrastructure/tablas.py`; esquemas de salida en `app/api/esquemas.py`. | Coordinar el trabajo académico y mostrar el avance solo a miembros autorizados y al profesor según el alcance. | La misma autorización informada, limitada a esta finalidad. Los campos de texto libre podrían contener datos personales no previstos; no deben usarse para datos sensibles. |
| Usuario, recurso, operación, resultado y fecha/hora de auditoría | `AuditoriaTabla` en `app/infrastructure/tablas.py`. | Trazar accesos y operaciones para el control de acceso de ESC-03. | Autorización informada y finalidad de seguridad/auditoría, con acceso restringido. No se encontró una política de retención o eliminación de auditoría definida en el código. |
| Token de acceso y verificador temporal PKCE | `web/lib/oidc.ts`, en `sessionStorage`. | Completar OIDC y autorizar solicitudes a la API. | Tratamiento técnico transitorio para autenticación; no guardar contraseñas en UniTeam. El riesgo de lectura del token ante XSS se acepta temporalmente y se detalla en [arc42 §11](11-modelado-de-amenazas.md). |

La restricción L1 del propio proyecto cita la Ley 1581 de 2012 y el Decreto 1377 de 2013, y exige
consentimiento informado, finalidad declarada, supresión y control de acceso. Esta ficha deja
identificada la base prevista, pero no afirma que el consentimiento ya se capture ni que la
universidad haya validado el rol de responsable del tratamiento. Antes de usar datos reales se
deben confirmar el responsable, el aviso de privacidad, la autorización y la retención con la
institución. El proveedor de identidad administra las credenciales; UniTeam no almacena
contraseñas.

## Dependencias y despliegue

La CI incorpora `pip-audit` para las dependencias Python de producción y `npm audit` para el
árbol web. Las versiones vulnerables encontradas durante esta revisión se actualizaron en los
manifiestos y locks; los escaneos locales posteriores no reportaron vulnerabilidades conocidas.
El run de GitHub que existía para el commit base es anterior a este job y no contiene sus
resultados; la URL y esa limitación están en la [evidencia S13](../entregas/S13-modelado-amenazas.md).
