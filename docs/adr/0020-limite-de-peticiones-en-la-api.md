# ADR 0020 — Límite de peticiones en la API

- Estado: Propuesto (no implementado aún)
- Amenaza: T8 (denegación de servicio)

## Decisión
Aplicar un límite por usuario autenticado e IP en la API mediante middleware.

## Consecuencias
- (+) Protege la API y MySQL de ráfagas.
- (−) Requiere elegir un almacén de contadores (memoria local suficiente con una sola instancia).
