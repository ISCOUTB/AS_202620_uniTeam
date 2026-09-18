# Contrato de API — UniTeam

**Versión:** `v0.2.0`

**Documento humano:** [`contrato.md`](./contrato.md)
**Esquema OpenAPI:** [`openapi.yaml`](./openapi.yaml)
**Pruebas de contrato:** [`../../test/test_contrato.py`](../../test/test_contrato.py)

---

## Pruebas de contrato

Las pruebas de contrato verifican que la API cumple con su especificación formal.
No prueban lógica de negocio (eso corresponde a las pruebas de integración);
prueban que la interfaz se comporta según lo pactado.

### Categorías de verificación

| Categoría | Qué verifica | Archivo |
|-----------|-------------|---------|
| **Autenticación** | Sin token → 401; token inválido/caducado → 401 | `test/test_contrato.py` |
| **Validación de entrada** | Campos vacíos, valores inválidos, límites fuera de rango → 422 | `test/test_contrato.py` |
| **Autorización** | Usuario ajeno → 403 sin datos; líder vs integrante → 403 si no es líder | `test/test_contrato.py` |
| **Códigos de éxito** | Crear → 201; consultar → 200; respuesta tiene los campos esperados | `test/test_contrato.py` |
| **Forma de error** | Todos los errores llevan `{"detail": "..."}` | `test/test_contrato.py` |
| **Paginación** | `limite` en [1,200]; `desplazamiento` ≥ 0; resultado paginado | `test/test_contrato.py` |
| **Transiciones** | Transición inválida → 409; duplicar miembro → 409 | `test/test_corte_vertical.py` |
| **Seguridad** | Proyecto inexistente ≠ proyecto ajeno (ambos 403) | `test/test_corte_vertical.py` |

### Ejecución

```bash
# Pruebas de contrato
pytest -v test/test_contrato.py

# Pruebas de integración (corte vertical)
pytest -v test/test_corte_vertical.py test/test_tablero.py test/test_proyectos.py

# Pruebas de autenticación
pytest -v test/test_autenticacion.py

# Todas las pruebas
pytest -v
```

### Relación con el contrato

Cada test en `test_contrato.py` corresponde a una sección del contrato:

| Test | Sección del contrato que verifica |
|------|----------------------------------|
| `test_sin_token_responde_401` | Autenticación |
| `test_bearer_invalido_responde_401` | Autenticación |
| `test_crear_proyecto_sin_nombre_responde_422` | Validación de entrada — `nombre` |
| `test_crear_tarea_sin_titulo_responde_422` | Validación de entrada — `titulo` |
| `test_limite_paginacion_excesivo_responde_422` | Paginación — `limite ≤ 200` |
| `test_usuario_ajeno_no_puede_listar_tareas_403_sin_datos` | Autorización — ESC-03 |
| `test_proyecto_inexistente_devuelve_403_no_404` | Autorización — ESC-03 |
| `test_crear_proyecto_responde_201_con_formato` | Formato de respuesta — `ProyectoSalida` |
| `test_crear_tarea_responde_201_con_todos_los_campos` | Formato de respuesta — `TareaSalida` |
| `test_todos_los_errores_tienen_detail` | Formato de error |
| `test_la_auditoria_registra_acceso_denegado` | Auditoría — ESC-03 |
