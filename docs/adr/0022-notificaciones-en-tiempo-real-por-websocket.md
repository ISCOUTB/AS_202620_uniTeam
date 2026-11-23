# 0022 — Notificaciones en tiempo real por WebSocket

- Estado: Aceptada (implementada y probada)
- Fecha: 2026-11-22

## Contexto

El tablero Kanban necesitaba reflejar cambios de estado y de responsable de una tarea sin obligar al usuario a recargar la página. La Aplicación Web ya consultaba la API por REST, pero no tenía canal de subida del servidor al cliente.

## Decisión

Añadir un punto de conexión WebSocket autenticado en `ws(s)://<api>/proyectos/{proyecto_id}/eventos` implementado en proceso (`app/api/rutas_tiempo_real.py` y `app/api/tiempo_real.py`), sin broker externo. El cliente envía como primer mensaje `{"tipo":"autenticar","token":...}` con el mismo token OIDC de la sesión; el servidor valida el token contra el JWKS del emisor y comprueba que el usuario pertenezca al proyecto antes de aceptar la conexión. Los cambios de tarea se notifican solo después de que la transacción se confirme (`test_websocket_notifica_cambios_solo_despues_del_commit`).

## Alternativas descartadas

- Sondeo periódico (polling) desde el frontend: simples de implementar pero generan tráfico innecesario y latencia de hasta el intervalo de sondeo.
- Server-Sent Events (SSE): unidireccional y más sencillo, pero no encajaba con la necesidad de autenticar por mensaje y de mantener una conexión bidireccional ligera.
- Broker externo (RabbitMQ, Redis Streams): añadiría infraestructura, costo y una pieza más que mantener, en tensión con T5 (0 USD) y con el estilo sincrónico de eventos en proceso (ADR 0006).

## Consecuencias

- (+) El tablero se actualiza en tiempo real sin recargar; las pruebas cubren autenticación inválida, origen no permitido, usuario ajeno y notificación tras commit.
- (−) Al ser un bus en proceso sin broker, no hay entrega durable ni garantía de procesamiento eventual entre réplicas; si la instancia cae, los eventos en vuelo se pierden. Es una limitación declarada, no un defecto.
- (−) La conexión WebSocket puede quedar abierta con un token que caduca; la reautenticación requiere abrir una nueva conexión.
- No sustituye a la fuente de verdad (MySQL); el cliente vuelve a consultar la API tras reconectar.
