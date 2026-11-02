# ADR 0010 — Autorización por pertenencia a equipo en una capa única

- Estado: Propuesto (S13)
- Amenaza: T1 (IDOR / elevación de privilegios)

## Contexto
Los datos (tareas) pertenecen a equipos. Verificar la pertenencia endpoint por endpoint deja huecos cuando se agregan rutas nuevas.

## Decisión
Centralizar la verificación en una dependencia/política de la API (FastAPI `Depends`) que resuelve el equipo del recurso y comprueba que el usuario autenticado es miembro antes de ejecutar la lógica.

## Consecuencias
- (+) Un solo punto que probar y revisar; las rutas nuevas heredan la regla.
- (−) Una consulta adicional por petición.
- Requiere pruebas negativas: usuario de otro equipo recibe 403/404 en cada endpoint.
