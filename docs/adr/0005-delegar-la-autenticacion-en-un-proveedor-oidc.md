# 0005 — Delegar la autenticación en un proveedor OIDC

- **Estado:** Aceptada
- **Fecha:** 2026-08-29
- **Decide:** el equipo de desarrollo (I-04)

## Contexto

Hasta ahora la API tomaba la identidad de una cabecera `X-Usuario` que el cliente escribía a
mano. Era andamiaje declarado como tal, pero con una consecuencia grave: **cualquiera podía
afirmar ser quien quisiera**. La autorización de
[ESC-03](../calidad/escenarios-calidad.md#esc-03) era real —comprobaba la pertenencia al
proyecto contra la base de datos—, pero se apoyaba en una identidad que nadie verificaba, de
modo que bastaba con escribir el nombre de un miembro para entrar en su proyecto.

El [C4 de contexto](../c4/nivel1-contexto.md) ya preveía un proveedor de identidad externo
desde la primera semana. Esta decisión lo hace efectivo.

## Opciones evaluadas

| Opción | A favor | En contra |
|--------|---------|----------|
| **Delegar en un proveedor OIDC** | UniTeam no almacena ni valida contraseñas, lo que reduce el alcance de la restricción legal [L1](../arc42/arc42-uniteam.md#23-restricciones-legales) y elimina toda una clase de vulnerabilidades. Los estudiantes ya tienen cuenta institucional o de Google. Sin costo (O3). | Depende de un tercero disponible, y obliga a manejar tokens, JWKS y caducidades. |
| Usuarios y contraseñas propios | Sin dependencias externas. | Obliga a almacenar credenciales, con su cifrado, su recuperación y su exposición legal. Es trabajo que no aporta nada al problema que UniTeam resuelve, con un equipo de dedicación parcial (O1). |
| Seguir con la cabecera | Cero trabajo. | No es autenticación. Deja ESC-03 apoyado en una afirmación no verificada. |

## Decisión

Se delega la autenticación en un **proveedor OpenID Connect**. La aplicación web ejecuta el
flujo de código de autorización con **PKCE** (RFC 7636), que es el que corresponde a un cliente
público —una aplicación en el navegador no puede guardar un secreto—, y envía el token a la API
en la cabecera `Authorization: Bearer`.

La API **verifica el token en cada petición**: firma contra el JWKS del emisor, emisor
esperado, audiencia esperada y caducidad. La identidad sale del token, no de lo que el cliente
diga. La cabecera `X-Usuario` se elimina por completo.

Para desarrollo se incluye un **emisor mínimo** (`scripts/emisor_dev.py`) que habla
descubrimiento, JWKS, autorización con PKCE y canje de código. Existe para que
`docker compose up` funcione sin cuentas externas y para que las pruebas usen criptografía
real en vez de simulaciones. **No autentica a nadie** y no debe desplegarse fuera de
desarrollo.

## Consecuencias

**Positivas.** La identidad pasa a ser verificable; ESC-03 deja de apoyarse en una afirmación
del cliente. UniTeam no guarda contraseñas. El cambio de proveedor es configuración
(`OIDC_EMISOR`, `OIDC_AUDIENCIA`), no código.

**Negativas.** El sistema depende de que el proveedor esté disponible, lo que resta margen a
[ESC-04](../calidad/escenarios-calidad.md#esc-04). Aparece un componente más que configurar en
cada entorno. El token se guarda en `sessionStorage` del navegador, expuesto a XSS; mitigarlo
del todo exigiría cookies `HttpOnly` y un backend de sesión, que se pospone.

**Pendiente.** No se ha seleccionado el proveedor concreto para el despliegue —cuenta
institucional o Google—; hasta entonces solo está configurado el emisor de desarrollo.

## Trazabilidad

| Eslabón | Dónde |
|---------|-------|
| Aspecto y requisito | [A-09](../aspectos.md) |
| Elemento C4 | «Proveedor de identidad» en [C4 nivel 2](../c4/nivel2-contenedores.md) |
| Código | `app/api/seguridad.py`, `web/lib/oidc.ts`, `scripts/emisor_dev.py` |
| Pruebas | `test/test_autenticacion.py` |
| Escenario de calidad | [ESC-03](../calidad/escenarios-calidad.md#esc-03) |
