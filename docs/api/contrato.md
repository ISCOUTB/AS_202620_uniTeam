# Contrato de API — UniTeam

**Versión:** `v0.2.0`  
**Base:** `http://localhost:8000`  
**Documentación interactiva:** `http://localhost:8000/docs`  
**Esquema OpenAPI:** [`openapi.yaml`](./openapi.yaml)  
**Pruebas de contrato:** [`../../test/test_contrato.py`](../../test/test_contrato.py)

---

## Autenticación

Todas las peticiones (excepto `GET /` y `GET /activo`) requieren un token OIDC en la cabecera:

```
Authorization: Bearer <token>
```

| Sin token | Token inválido | Token válido pero sin acceso |
|-----------|---------------|------------------------------|
| `401` con `WWW-Authenticate: Bearer` | `401` con detalle del error | `403` sin datos del recurso |

El token debe ser firmado por el proveedor de identidad configurado (`OIDC_EMISOR`), con la audiencia correcta (`OIDC_AUDIENCIA`) y no expirado. La identidad del usuario se extrae del claim configurado (`OIDC_CLAIM_USUARIO`, por defecto `email`).

---

## Convenciones

### Códigos de estado

| Código | Significado | Cuándo se usa |
|--------|-------------|---------------|
| `200` | Éxito | Operaciones exitosas (GET, PUT) |
| `201` | Creado | Creación de recurso (POST) |
| `400` | Solicitud incorrecta | Formato de cuerpo no válido |
| `401` | No autenticado | Faltante o inválido token |
| `403` | Prohibido | Autenticado pero sin acceso al recurso |
| `404` | No encontrado | Recurso no existe (cuando la operación está permitida) |
| `409` | Conflicto | Duplicado, transición inválida |
| `422` | No procesable | Validación de entrada fallida |

### Formato de error

Todos los errores siguen el mismo formato:

```json
{
  "detail": "Descripción del error"
}
```

### Paginación

Las listas de tareas se paginan con dos parámetros de consulta:

| Parámetro | Tipo | Default | Restricciones |
|-----------|------|---------|---------------|
| `limite` | integer | `50` | `1 ≤ limite ≤ 200` |
| `desplazamiento` | integer | `0` | `desplazamiento ≥ 0` |

### Orden de resultados

Las tareas se ordenan por `creada_en` (ascendente) y desempatan por `id` (ascendente). El desempate es necesario porque `DATETIME` en MySQL tiene precisión de segundo.

---

## Rutas

### Sistema

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `GET` | `/` | No | Estado del servicio |
| `GET` | `/activo` | No | Estado del servicio |

### Proyectos

#### Crear proyecto

| | |
|---|---|
| **Método** | `POST` |
| **Ruta** | `/proyectos` |
| **Auth** | Sí |
| **Código éxito** | `201` |
| **Descripción** | Crea un proyecto. Quien lo crea queda como líder. |

**Cuerpo de entrada** (`application/json`):

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| `nombre` | string | Sí | `1 ≤ longitud ≤ 200` |
| `miembros` | string[] | No (default: `[]`) | Lista de correos |

**Respuesta** `201`:

```json
{
  "id": "uuid",
  "nombre": "Proyecto de Arquitectura",
  "miembros": ["ana@utb.edu.co", "bruno@utb.edu.co"]
}
```

**Errores:**

| Código | Condición |
|--------|-----------|
| `400` | `nombre` vacío o demasiado largo |
| `401` | Sin token |

#### Listar proyectos propios

| | |
|---|---|
| **Método** | `GET` |
| **Ruta** | `/proyectos` |
| **Auth** | Sí |
| **Código éxito** | `200` |
| **Descripción** | Lista los proyectos de los que el usuario es miembro. Nunca devuelve ajenos. |

**Respuesta** `200`:

```json
[
  {
    "id": "uuid",
    "nombre": "Proyecto de Arquitectura",
    "miembros": [
      { "usuario": "ana@utb.edu.co", "rol": "lider" },
      { "usuario": "bruno@utb.edu.co", "rol": "integrante" }
    ]
  }
]
```

**Errores:**

| Código | Condición |
|--------|-----------|
| `401` | Sin token |

#### Obtener detalle de proyecto

| | |
|---|---|
| **Método** | `GET` |
| **Ruta** | `/proyectos/{proyecto_id}` |
| **Auth** | Sí (pertenencia) |
| **Código éxito** | `200` |
| **Descripción** | Detalle del proyecto con sus miembros y roles. |

**Errores:**

| Código | Condición |
|--------|-----------|
| `401` | Sin token |
| `403` | No es miembro del proyecto **o** el proyecto no existe (no se distingue) |

#### Agregar miembro

| | |
|---|---|
| **Método** | `POST` |
| **Ruta** | `/proyectos/{proyecto_id}/miembros` |
| **Auth** | Sí (líder del proyecto) |
| **Código éxito** | `201` |
| **Descripción** | Agrega un miembro al proyecto. Reservado al líder. |

**Cuerpo de entrada:**

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| `usuario` | string | Sí | `1 ≤ longitud ≤ 120` |
| `rol` | string | No (default: `"integrante"`) | `"integrante"` o `"lider"` |

**Errores:**

| Código | Condición |
|--------|-----------|
| `401` | Sin token |
| `403` | No es líder del proyecto (o no es miembro) |
| `409` | El usuario ya es miembro del proyecto |

### Tareas

#### Crear tarea

| | |
|---|---|
| **Método** | `POST` |
| **Ruta** | `/proyectos/{proyecto_id}/tareas` |
| **Auth** | Sí (pertenencia) |
| **Código éxito** | `201` |
| **Descripción** | Crea una tarea dentro del proyecto. |

**Cuerpo de entrada:**

| Campo | Tipo | Requerido | Default | Restricciones |
|-------|------|-----------|---------|---------------|
| `titulo` | string | Sí | — | `1 ≤ longitud ≤ 300` |
| `prioridad` | string | No | `"media"` | `"baja"`, `"media"`, `"alta"` |
| `responsable` | string/null | No | `null` | Debe ser miembro del proyecto o `null` |
| `fecha_limite` | string/date/null | No | `null` | Formato `YYYY-MM-DD` |

**Respuesta** `201`:

```json
{
  "id": "uuid",
  "proyecto_id": "uuid",
  "titulo": "Redactar la sección 5",
  "prioridad": "alta",
  "estado": "pendiente",
  "responsable": "bruno@utb.edu.co",
  "fecha_limite": "2026-09-05",
  "creada_por": "ana@utb.edu.co",
  "creada_en": "2026-09-18T15:30:00+00:00"
}
```

**Errores:**

| Código | Condición |
|--------|-----------|
| `400` | `titulo` vacío o demasiado largo |
| `401` | Sin token |
| `403` | No pertenece al proyecto, o el responsable no es miembro |

#### Listar tareas (tablero)

| | |
|---|---|
| **Método** | `GET` |
| **Ruta** | `/proyectos/{proyecto_id}/tareas` |
| **Auth** | Sí (pertenencia) |
| **Código éxito** | `200` |
| **Descripción** | Tablero del proyecto, con filtros y paginación. |

**Parámetros de consulta:**

| Parámetro | Tipo | Default | Restricciones |
|-----------|------|---------|---------------|
| `estado` | string | — | `"pendiente"`, `"en_progreso"`, `"completada"` |
| `responsable` | string | — | Correo de miembro del proyecto |
| `limite` | integer | `50` | `1 ≤ limite ≤ 200` |
| `desplazamiento` | integer | `0` | `≥ 0` |

**Respuesta** `200`:

```json
[
  {
    "id": "uuid",
    "proyecto_id": "uuid",
    "titulo": "Redactar la sección 5",
    "prioridad": "alta",
    "estado": "pendiente",
    "responsable": "bruno@utb.edu.co",
    "fecha_limite": "2026-09-05",
    "creada_por": "ana@utb.edu.co",
    "creada_en": "2026-09-18T15:30:00+00:00"
  }
]
```

**Errores:**

| Código | Condición |
|--------|-----------|
| `401` | Sin token |
| `403` | No pertenece al proyecto |
| `422` | `limite > 200` o `limite < 1` |

#### Obtener tarea

| | |
|---|---|
| **Método** | `GET` |
| **Ruta** | `/proyectos/{proyecto_id}/tareas/{tarea_id}` |
| **Auth** | Sí (pertenencia) |
| **Código éxito** | `200` |

**Errores:**

| Código | Condición |
|--------|-----------|
| `401` | Sin token |
| `403` | No pertenece al proyecto |
| `404` | La tarea no existe en este proyecto |

#### Asignar responsable

| | |
|---|---|
| **Método** | `PUT` |
| **Ruta** | `/proyectos/{proyecto_id}/tareas/{tarea_id}/responsable` |
| **Auth** | Sí (pertenencia) |
| **Código éxito** | `200` |

**Cuerpo de entrada:**

| Campo | Tipo | Requerido |
|-------|------|-----------|
| `responsable` | string | Sí — correo de miembro del proyecto |

**Errores:**

| Código | Condición |
|--------|-----------|
| `401` | Sin token |
| `403` | No pertenece al proyecto, o el responsable no es miembro |

#### Cambiar estado

| | |
|---|---|
| **Método** | `PUT` |
| **Ruta** | `/proyectos/{proyecto_id}/tareas/{tarea_id}/estado` |
| **Auth** | Sí (pertenencia) |
| **Código éxito** | `200` |

**Cuerpo de entrada:**

| Campo | Tipo | Requerido |
|-------|------|-----------|
| `estado` | string | Sí — `"pendiente"`, `"en_progreso"`, `"completada"` |

**Errores:**

| Código | Condición |
|--------|-----------|
| `401` | Sin token |
| `403` | No pertenece al proyecto |
| `409` | Transición de estado inválida |

### Progreso

#### Consultar progreso

| | |
|---|---|
| **Método** | `GET` |
| **Ruta** | `/proyectos/{proyecto_id}/progreso` |
| **Auth** | Sí (pertenencia) |
| **Código éxito** | `200` |
| **Descripción** | Resumen agregado del avance del proyecto. |

**Respuesta** `200`:

```json
{
  "total": 4,
  "por_estado": { "pendiente": 3, "completada": 1 },
  "sin_responsable": 2,
  "vencidas": 0,
  "porcentaje_completado": 25.0
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `total` | integer | Número total de tareas |
| `por_estado` | object | Conteo por estado (`"pendiente"`, `"en_progreso"`, `"completada"`) |
| `sin_responsable` | integer | Tareas sin responsable asignado |
| `vencidas` | integer | Tareas con fecha límite anterior a hoy, no completadas |
| `porcentaje_completado` | number | Porcentaje de tareas completadas (0.0–100.0) |

**Errores:**

| Código | Condición |
|--------|-----------|
| `401` | Sin token |
| `403` | No pertenece al proyecto |

---

## Flujo de estados de tarea

```
pendiente ──→ en_progreso ──→ completada
    ↑                          │
    └──────────────────────────┘
```

| Desde | Hacia | Permitido |
|-------|-------|-----------|
| `pendiente` | `en_progreso` | Sí |
| `pendiente` | `completada` | No → `409` |
| `en_progreso` | `pendiente` | Sí |
| `en_progreso` | `completada` | Sí |
| `completada` | `en_progreso` | Sí |
| `completada` | `pendiente` | No → `409` |

---

## Esquemas

### CrearProyecto

| Campo | Tipo | Restricciones |
|-------|------|---------------|
| `nombre` | string | `1 ≤ longitud ≤ 200` |
| `miembros` | string[] | Opcional, default `[]` |

### CrearTarea

| Campo | Tipo | Restricciones |
|-------|------|---------------|
| `titulo` | string | `1 ≤ longitud ≤ 300` |
| `prioridad` | string | `"baja"`, `"media"`, `"alta"` (default: `"media"`) |
| `responsable` | string/null | Opcional. Debe ser miembro del proyecto |
| `fecha_limite` | string/null | Opcional, formato `YYYY-MM-DD` |

### TareaSalida

| Campo | Tipo |
|-------|------|
| `id` | string (UUID) |
| `proyecto_id` | string (UUID) |
| `titulo` | string |
| `prioridad` | string |
| `estado` | string |
| `responsable` | string/null |
| `fecha_limite` | string/date/null |
| `creada_por` | string |
| `creada_en` | string (datetime ISO 8601) |

### ProgresoSalida

| Campo | Tipo |
|-------|------|
| `total` | integer |
| `por_estado` | object |
| `sin_responsable` | integer |
| `vencidas` | integer |
| `porcentaje_completado` | number |
