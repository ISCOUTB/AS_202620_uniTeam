# 8. Conceptos transversales — Arquitectura de seguridad

Detalle del análisis en [docs/seguridad/amenazas.md](../seguridad/amenazas.md).

## Autenticación
Delegada en un proveedor OpenID Connect; UniTeam no guarda contraseñas (ADR 0005). La API valida firma, emisor (`iss`), audiencia (`aud`) y expiración de cada token (T2).

## Autorización
Control por pertenencia a equipo, aplicado en una capa única de la API y no endpoint por endpoint (ADR 0010, T1).

## Protección del navegador
CSP, escapado de salida y decisión sobre almacenamiento de la sesión (ADR 0011, T4, T5). CORS limitado a orígenes conocidos (T9).

## Protección de datos
MySQL accesible solo desde la API, con usuario de mínimo privilegio y credenciales por variable de entorno (T3). Consultas parametrizadas (T7). Datos personales y su base de tratamiento en [privacidad.md](../seguridad/privacidad.md).

## Disponibilidad
Límite de peticiones en la API (ADR 0012, T8).

## Cadena de suministro
Análisis de dependencias en CI y Dependabot (T6); resultados en [dependencias.md](../seguridad/dependencias.md). Los secretos no se versionan; las credenciales del README son solo de desarrollo local.
