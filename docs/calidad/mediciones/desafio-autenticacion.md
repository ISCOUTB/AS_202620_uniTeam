# Desafío final: delegar la autenticación en un proveedor OIDC

**Consigna operativa asignada:** sustituir la autenticación por cabecera `X-Usuario`
(que cualquiera podía falsificar) por la delegación en un proveedor OpenID Connect.
Corresponde a la restricción de seguridad identificada ya en el corte 1 y documentada
en [`ADR 0005`](../../adr/0005-delegar-la-autenticacion-en-un-proveedor-oidc.md) y
[`ADR 0010`](../../adr/0010-usar-auth0-como-proveedor-de-identidad.md).

## Antes (línea base)

En el commit anterior a [`984922e`](https://github.com/ISCOUTB/AS_202620_uniTeam/commit/984922edfb62b03a18f261021d1a630bf632a794) ("Autenticación con OpenID Connect y retirada de la cabecera X-Usuario"):

- `app/api/dependencias.py` resolvía el usuario con
  `def usuario_actual(x_usuario: str = Header(..., alias="X-Usuario")) -> str`.
- `app/main.py` permitía la cabecera con
  `allow_headers=["Content-Type", "X-Usuario"]`.
- Cualquier persona que conociera el correo de un miembro podía entrar en su proyecto
  solo con `X-Usuario: <correo>`: no había firma, ni emisor, ni audiencia, ni caducidad.
- Cifra de explotabilidad: **100 % de identidades suplantables** mediante esa cabecera.
- ESC-03 estaba nominalmente cubierta, pero la identidad no era verificable.

## Después

En el commit [`984922e`](https://github.com/ISCOUTB/AS_202620_uniTeam/commit/984922edfb62b03a18f261021d1a630bf632a794):

- La API verifica el token en cada petición contra el JWKS del emisor (firma, `iss`,
  `aud` y `exp`) en [`app/api/seguridad.py`](../../../app/api/seguridad.py).
- La identidad sale del claim configurado (`sub` como respaldo), nunca de lo que diga el
  cliente (`test_la_identidad_sale_del_token_no_de_lo_que_diga_el_cliente`).
- Sin `OIDC_EMISOR` ni `OIDC_AUDIENCIA` la API no autentica y no hay vía alternativa.
- La cabecera `X-Usuario` se eliminó del código y de las pruebas.

## Medición frente al umbral

| Momento | Cifra | Umbral / criterio | Resultado |
|---------|-------|-------------------|-----------|
| Antes | 100 % de identidades suplantables vía `X-Usuario` | 0 % (identidad verificable) | No cumple |
| Después | 0 % de aceptación de `X-Usuario` sola | 0 % | Cumple |
| Después | 11 pruebas negativas en 401 (`test/test_autenticacion.py`) | ≥ 1 caso negativo por entrada | Cumple |
| Despliegue real | 7 identidades con `X-Usuario` → `401` (2026-11-22) | 401 para cualquier nombre | Cumple |

**Prueba reproducible:** [`test_la_cabecera_x_usuario_sola_no_autentica`](../../../test/test_autenticacion.py)
envía `GET /proyectos` con solo `X-Usuario` (sin `Authorization`) y exige `401` con
`WWW-Authenticate: Bearer`. También `test_la_cabecera_x_usuario_no_desplaza_al_token`
comprueba que, incluso con un token válido de otro usuario, `X-Usuario` no cambia la
sesión.

**Ejecución:** `python -m pytest -q test/test_autenticacion.py` → 11 pruebas, todas verdes.

**Conclusión:** el desafío está implementado, evidenciado con código y prueba, y la
cifra de antes (100 % suplantable) frente a la de después (0 % vía X-Usuario, 401
garantizado) cuantifica la mejora, que es lo que separa un resultado competente de uno
sobresaliente.
