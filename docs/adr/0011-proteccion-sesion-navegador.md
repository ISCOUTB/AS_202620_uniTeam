# ADR 0011 — Protección de la sesión en el navegador

- Estado: Propuesto (S13)
- Amenazas: T4, T5

## Contexto
Si el token se guarda en `localStorage`, un XSS puede robarlo.

## Decisión
Aplicar Content-Security-Policy y escapado de salida en la aplicación Next.js, y mantener el token en memoria (o cookie `httpOnly` si se incorpora un intermediario en el servidor de Next.js). La opción elegida se registra al implementarla.

## Consecuencias
- (+) Reduce el impacto de un XSS.
- (−) Mantener el token solo en memoria obliga a reautenticar al recargar; la cookie `httpOnly` cambia el flujo de autenticación.
