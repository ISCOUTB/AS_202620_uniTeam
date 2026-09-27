# ADR-010 — Usar Auth0 como proveedor de identidad del despliegue

- **Estado:** Aceptada
- **Fecha:** 2026-09-27
- **Decisores:** Equipo de desarrollo (I-04)
- **Pieza:** Proveedor de identidad — sistema externo del [C4 nivel 1](../c4/nivel1-contexto.md) y del [nivel 2](../c4/nivel2-contenedores.md)
- **Completa:** [ADR-005](0005-delegar-la-autenticacion-en-un-proveedor-oidc.md), que dejó pendiente el proveedor concreto

## Contexto

[ADR-005](0005-delegar-la-autenticacion-en-un-proveedor-oidc.md) delegó la autenticación en un
proveedor OpenID Connect y dejó pendiente cuál. En local se usa el emisor de desarrollo, que
**no puede desplegarse**: firma un token para cualquier nombre que se le pida, así que en una URL
pública cualquiera podría entrar como cualquier otro y ESC-03 dejaría de significar nada.

La API ya espera, sin cambios de código, un proveedor que:

1. emita **tokens de acceso en JWT** firmados con RS256 y publique su JWKS;
2. los emita **para una audiencia** —la de UniTeam— que la API comprueba;
3. acepte el flujo de código con **PKCE sin secreto de cliente**, porque el cliente es el
   navegador;
4. incluya en el token **el correo**, que es con lo que se identifican los miembros de un
   proyecto.

## Alternativas

| | A. Auth0, plan Free (**elegida**) | B. Google directamente como emisor |
|---|---|---|
| Token de acceso | JWT para la audiencia que se registre | Opaco: no es un JWT y la API no puede verificarlo |
| PKCE sin secreto | Sí, aplicación de tipo SPA | Los clientes web de Google exigen secreto en el canje |
| Correo en el token | Con una *Action* de cuatro líneas | Solo en el `id_token` |
| Inicio de sesión con Google | Sí, como conexión social | Sí |
| Cuenta institucional | Una conexión empresarial incluida | No |

**Por qué se descarta B.** Google no cumple los requisitos 1 y 3: su token de acceso es opaco y
su canje exige un secreto que un navegador no puede guardar. Usarlo obligaría a que la API
aceptara el `id_token` como credencial de acceso, que no está hecho para eso —su audiencia es el
cliente, no la API—, y a cambiar `app/api/seguridad.py`. Auth0 cumple los cuatro sin tocar
código de la API, y además permite **iniciar sesión con Google** a través de él.

Se consideró **la cuenta institucional** directamente: depende de que la universidad registre la
aplicación en su directorio, fuera del control del equipo y del plazo. Queda como evolución:
Auth0 la admite como conexión empresarial sin cambiar nada en UniTeam.

## Capa gratuita verificada

Consultada el 2026-09-27 ([precios de Auth0](https://auth0.com/pricing)): el plan Free admite
**25 000 usuarios activos al mes**, inicios de sesión ilimitados, conexiones sociales —Google
entre ellas— y una conexión empresarial. **No pide tarjeta** para crear el *tenant*.

## Decisión

El proveedor de identidad del despliegue es un *tenant* de Auth0 con:

- una **API** registrada cuyo identificador es la audiencia (`OIDC_AUDIENCIA`);
- una **aplicación SPA** con PKCE, cuyas URL de retorno son las del sitio desplegado;
- una ***Action* de inicio de sesión** que añade el correo al token de acceso en el claim
  `https://uniteam.app/email` (`OIDC_CLAIM_USUARIO`).

Los pasos exactos están en la [guía de despliegue](../despliegue/guia.md#3-auth0-proveedor-de-identidad).
En el código solo cambia la Aplicación Web, que ahora envía el parámetro `audience` cuando
`NEXT_PUBLIC_OIDC_AUDIENCIA` está definido. El emisor de desarrollo sigue sirviendo para local y
para las pruebas, y **ya no viaja en la imagen de la API** (destino `idp-dev` del `Dockerfile`).

## Consecuencias

- **Costo:** 0 USD/mes. Punto de ruptura: 25 000 usuarios activos al mes, unas 500 veces el
  volumen supuesto ([costos](../despliegue/costos.md)). Pasado ese punto, plan de pago por
  tramos de usuarios activos.
- **Dependencia de un tercero** para entrar al sistema: si Auth0 cae, nadie inicia sesión, aunque
  quien ya tenga un token sigue trabajando hasta que caduque. Riesgo aceptado en ADR-005.
- **Privacidad:** el correo del usuario viaja en el token, como ya viajaba con el emisor de
  desarrollo. La API no lo escribe en los logs.

## Reversión

La API solo conoce tres variables: `OIDC_EMISOR`, `OIDC_AUDIENCIA` y `OIDC_CLAIM_USUARIO`.
Cambiar de proveedor es cambiarlas en Render, junto con las `NEXT_PUBLIC_OIDC_*` del sitio, y
volver a desplegar. Los datos no dependen del proveedor porque los miembros se identifican por
correo, no por el identificador interno de Auth0.

## Trazabilidad

[`web/lib/oidc.ts`](../../web/lib/oidc.ts) · [`app/api/seguridad.py`](../../app/api/seguridad.py) ·
[`render.yaml`](../../render.yaml) · [ESC-03](../calidad/escenarios-calidad.md#esc-03)
