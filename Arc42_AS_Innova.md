---
date: Marzo 2026
title: InnovaActivos – Sistema de Gestión de Inventario de Activos Fijos
---

# InnovaActivos – Documentación de Arquitectura de Software
### Basada en la Plantilla arc42

**Acerca de arc42**
arc42, La plantilla de documentación para arquitectura de sistemas y de software.
Por Dr. Gernot Starke, Dr. Peter Hruschka y otros contribuyentes.
Revisión de la plantilla: 7.0 ES, Enero 2017
© https://www.arc42.org

---

# 1. Introducción y Metas

**InnovaActivos** es una aplicación multiplataforma (Web y Móvil) desarrollada en **Flutter**,
que permite a las organizaciones registrar, rastrear y gestionar sus activos fijos
(computadores, sillas, impresoras, equipos, etc.) y controlar los traslados internos
entre áreas o empleados, con trazabilidad completa de cada movimiento.

### Problema que resuelve

Muchas empresas llevan el control de sus activos en hojas de Excel o en papel, lo que genera:

- Pérdida de activos sin saber quién los tiene ni dónde están
- Traslados internos sin ningún tipo de documentación
- Auditorías lentas y con muchos errores humanos
- Imposibilidad de saber cuándo un equipo necesita mantenimiento

InnovaActivos digitaliza todo ese proceso desde el celular o el computador.

---

## 1.1 Vista de Requerimientos

### Requerimientos Funcionales

| ID    | Requerimiento                                                                              | Prioridad |
|-------|--------------------------------------------------------------------------------------------|-----------|
| RF-01 | El sistema debe permitir registrar activos con nombre, código, categoría, foto y ubicación | Alta      |
| RF-02 | El sistema debe generar y leer códigos QR por cada activo registrado                       | Alta      |
| RF-03 | El sistema debe permitir solicitar y aprobar traslados de activos entre áreas              | Alta      |
| RF-04 | Al completar un traslado, el sistema debe actualizar automáticamente la ubicación del activo| Alta     |
| RF-05 | El sistema debe permitir realizar tomas de inventario físico escaneando activos            | Alta      |
| RF-06 | El sistema debe detectar activos faltantes o registrados en una ubicación incorrecta       | Alta      |
| RF-07 | El sistema debe guardar el historial completo de movimientos de cada activo                | Alta      |
| RF-08 | El sistema debe tener usuarios con diferentes roles y permisos                             | Alta      |
| RF-09 | El sistema debe enviar notificaciones cuando hay traslados pendientes de aprobación        | Media     |
| RF-10 | El sistema debe generar reportes exportables en PDF                                        | Media     |
| RF-11 | El sistema debe mostrar un dashboard con el resumen general del inventario                 | Media     |

### Requerimientos No Funcionales

| ID     | Requerimiento                                                             | Prioridad |
|--------|---------------------------------------------------------------------------|-----------|
| RNF-01 | La aplicación debe funcionar en Web, Android e iOS usando Flutter         | Alta      |
| RNF-02 | La aplicación debe responder en menos de 2 segundos por cada acción       | Alta      |
| RNF-03 | El sistema debe estar disponible al menos el 95% del tiempo               | Alta      |
| RNF-04 | Las contraseñas deben guardarse cifradas, nunca en texto plano            | Alta      |
| RNF-05 | Solo los usuarios con sesión activa pueden acceder al sistema             | Alta      |
| RNF-06 | La app móvil debe poder escanear activos sin necesidad de internet        | Media     |
| RNF-07 | El historial de movimientos no puede ser modificado ni eliminado          | Alta      |
| RNF-08 | La interfaz debe ser fácil de usar sin necesidad de capacitación extensa  | Media     |

---

## 1.2 Metas de Calidad

| Prioridad | Meta de Calidad    | Descripción                                                             | Escenario Clave                                                          |
|-----------|--------------------|-------------------------------------------------------------------------|--------------------------------------------------------------------------|
| 1         | **Trazabilidad**   | Cada cambio en un activo queda registrado con fecha, hora y usuario     | El auditor puede ver quién movió un activo y cuándo lo hizo              |
| 2         | **Seguridad**      | Solo los usuarios autorizados pueden ver y modificar los activos        | Un empleado solo puede ver los activos de su área asignada               |
| 3         | **Usabilidad**     | Cualquier usuario puede escanear un activo en menos de 30 segundos      | Un técnico sin experiencia técnica puede completar una toma de inventario|
| 4         | **Confiabilidad**  | El sistema guarda los datos aunque se pierda la conexión a internet     | El técnico escanea activos sin señal y los datos se sincronizan después  |
| 5         | **Rendimiento**    | El sistema responde rápido aunque varios usuarios lo usen al mismo tiempo| 50 usuarios usando el sistema simultáneamente sin lentitud visible      |

---

## 1.3 Partes Interesadas (Stakeholders)

| Rol / Nombre                                        | Contacto                  | Expectativas                                                                  |
|-----------------------------------------------------|---------------------------|-------------------------------------------------------------------------------|
| **Jairo Enrique Serrano Castañeda** – Profesor      | jserrano@utb.edu.co       | Que el proyecto cumpla los entregables académicos con buena arquitectura      |
| **Ricardo David Chacón** – Project Manager          | ricardo.chacon@utb.edu.co | Que el equipo entregue a tiempo y que todos los módulos se integren bien      |
| **José Fernando Chimá** – Backend Developer         | jchima@utb.edu.co         | Tener claro qué endpoints construir y cómo conectarlos con la base de datos   |
| **Jhouran Del Toro** – Frontend Developer           | jdel@utb.edu.co           | Saber qué pantallas construir en Flutter y cómo consumir la API               |
| **Nilson David Rivera** – Database Manager          | riveran@utb.edu.co        | Tener el modelo de datos claro para diseñar las tablas en PostgreSQL          |
| **Dilson Rivera** – DevOps / Control de Versiones   | dilson@utb.edu.co         | Mantener el repositorio de GitHub organizado y el sistema desplegado          |
| **Empresa / Cliente Ficticio**                      | empresa@ejemplo.com       | Reducir pérdida de activos y tener control total del inventario               |
| **Área de Inventarios**                             | inventarios@empresa.com   | Registrar activos, controlar movimientos y evitar pérdidas                    |
| **Área de Auditoría Interna**                       | auditoria@empresa.com     | Acceso a reportes confiables y trazabilidad completa para auditorías rápidas  |
| **Empleados / Usuarios del sistema**                | usuarios@empresa.com      | Consultar activos disponibles y solicitar traslados de forma sencilla         |

---

## 1.4 Estado Actual del Proyecto (Corte Abril 2026)

### Artefactos disponibles

- Diagrama UML (clases y relaciones): `Asset Management Lifecycle-2026-03-22-210039.svg`
- Diagrama entidad-relacion: `Active Asset Management-2026-03-22-210133.svg`
- Esquema de base de datos: `innova-activos.v2.sql`
- **API Backend completa**: `app/` (FastAPI, 16 routers, 20+ modelos ORM)

### Avance real reportado

| Componente | Estado | Detalle |
|------------|--------|---------|
| Base de datos | ✅ Listo | Modelo en PostgreSQL con tablas, restricciones, indices, funciones y triggers |
| Diagramas UML/ER | ✅ Listo | Los diagramas reflejan entidades principales y relaciones del dominio |
| Interfaz Flutter responsive | ✅ Listo (UI) | Vista adaptada para celular y PC |
| Registro e inicio de sesion | ✅ Listo (UI) | Panel de registro/login con condicionales para flujo realista de acceso |
| **API Backend (FastAPI)** | ✅ **Listo** | **16 routers, 20+ modelos ORM, JWT auth, RBAC, CRUD completo para todas las entidades** |
| **Modulo Autenticación** | ✅ **Listo** | **Register, login, refresh token, logout, perfil (JWT + bcrypt)** |
| **Modulo Activos** | ✅ **Listo** | **CRUD completo, escaneo QR/barras/RFID, cambio de estado, asignación, historial** |
| **Modulo Traslados** | ✅ **Listo** | **Flujo completo: crear → aprobar/rechazar → en_transito → confirmar/cancelar** |
| **Modulo Inventario** | ✅ **Listo** | **Sesiones, escaneo con clasificación automática, cierre con totales** |
| **Modulo Sincronización** | ✅ **Listo** | **Cola offline, push de lotes, resolución de conflictos** |
| **Modulo Mantenimiento** | ✅ **Listo** | **Planes y órdenes de mantenimiento con prioridades** |
| **Modulo Notificaciones** | ✅ **Listo** | **CRUD, marcar leída, marcar todas leídas** |
| **Modulo Reportes** | ✅ **Listo** | **Solicitud y seguimiento de exportaciones** |
| **Roles en API** | ✅ **Listo** | **SUPERADMIN, ADMIN, AUDITOR, CUSTODIO, TECNICO con RBAC completo** |

---

# 2. Restricciones de la Arquitectura

### Restricciones Técnicas

| ID   | Restricción                                                           | Justificación                                              |
|------|-----------------------------------------------------------------------|------------------------------------------------------------|
| RT-1 | El frontend se desarrolla en **Flutter**                              | Tecnología definida por el equipo, cubre web y móvil       |
| RT-2 | El backend se desarrolla con **FastAPI (Python)**                     | Tecnología que el equipo conoce para construir APIs REST    |
| RT-3 | La base de datos es **PostgreSQL**                                    | Base de datos relacional que el equipo ya ha utilizado      |
| RT-4 | La comunicación entre frontend y backend es por **API REST con JSON** | Formato estándar, fácil de implementar y probar            |
| RT-5 | El proyecto se gestiona en **GitHub** con ramas por funcionalidad     | Control de versiones y trabajo colaborativo del equipo     |

### Restricciones del Equipo

| ID   | Restricción                                                                    | Justificación                                    |
|------|--------------------------------------------------------------------------------|--------------------------------------------------|
| RE-1 | El equipo tiene **5 integrantes** con roles definidos                          | Cada uno trabaja en su área específica           |
| RE-2 | El proyecto debe estar terminado al **final del semestre**                     | Fecha límite definida por la materia             |
| RE-3 | Solo se usan tecnologías que el equipo **ya conoce o puede aprender rápido**   | Tiempo limitado del semestre académico           |
| RE-4 | Toda la documentación se escribe en **español**                                | Contexto académico de la UTB                     |

### Restricciones de Convenciones

| ID   | Restricción                                               | Justificación                        |
|------|-----------------------------------------------------------|--------------------------------------|
| RC-1 | El código Flutter debe seguir las guías de **Effective Dart** | Consistencia y buenas prácticas  |
| RC-2 | El código Python debe seguir las guías de estilo **PEP 8**    | Consistencia y mantenibilidad    |
| RC-3 | Se utilizará **Gitflow** como estrategia de ramas en GitHub   | Trabajo en paralelo sin conflictos|

---

# 3. Alcance y Contexto del Sistema

## 3.1 Contexto de Negocio

```
┌──────────────────────────────────────────────────────────────────┐
│                      CONTEXTO DE NEGOCIO                         │
│                                                                  │
│  [Técnico]       ── escanea activos con el celular ──►           │
│  [Empleado]      ── solicita traslado de un activo ──►           │
│  [Supervisor]    ── aprueba o rechaza traslados ────►  ┌───────┐ │
│  [Auditor]       ── consulta historial y reportes ──►  │       │ │
│  [Administrador] ── gestiona usuarios y activos ────►  │FIXTRAK│ │
│  [Director]      ── consulta el dashboard ──────────►  │       │ │
│                                                        └───┬───┘ │
│                                                            │     │
│               ◄── envía correos de notificación ──────────►     │
│          [Servicio de Email: Gmail SMTP]                         │
│                                                                  │
│               ◄── almacena fotos de activos ──────────────►     │
│          [Firebase Storage]                                      │
└──────────────────────────────────────────────────────────────────┘
```

| Actor / Sistema Externo | Tipo    | ¿Qué hace con InnovaActivos?                                   |
|-------------------------|---------|-----------------------------------------------------------|
| Técnico de Inventario   | Usuario | Escanea activos con la cámara del celular                 |
| Empleado / Custodio     | Usuario | Ve sus activos asignados y solicita traslados             |
| Supervisor / Aprobador  | Usuario | Aprueba o rechaza las solicitudes de traslado             |
| Auditor                 | Usuario | Consulta el historial y descarga reportes                 |
| Administrador           | Usuario | Registra activos, crea usuarios y configura el sistema    |
| Director / Gerente      | Usuario | Consulta el dashboard con el resumen del inventario       |
| Gmail SMTP              | Sistema | Envía correos cuando hay traslados pendientes o aprobados |
| Firebase Storage        | Sistema | Almacena las fotos de los activos registrados             |

## 3.2 Contexto Técnico

```
┌─────────────────────────────────────────────────────────────────┐
│                       CONTEXTO TÉCNICO                          │
│                                                                 │
│  ┌───────────────────────────────────────┐                      │
│  │         FLUTTER (Frontend)            │                      │
│  │  Web / Android / iOS                  │                      │
│  │  - Pantallas y navegación             │                      │
│  │  - Escaneo QR con la cámara           │                      │
│  │  - Almacenamiento local (offline)     │                      │
│  └──────────────────┬────────────────────┘                      │
│                     │                                           │
│                     │  HTTP / REST / JSON                       │
│                     │                                           │
│  ┌──────────────────▼────────────────────┐                      │
│  │         FASTAPI (Backend)             │                      │
│  │  - Endpoints REST                     │                      │
│  │  - Lógica del negocio                 │                      │
│  │  - Autenticación con JWT              │                      │
│  │  - Envío de correos (SMTP)            │                      │
│  └──────────────────┬────────────────────┘                      │
│                     │                                           │
│                     │  SQL                                      │
│                     │                                           │
│  ┌──────────────────▼────────────────────┐                      │
│  │         POSTGRESQL (Base de Datos)    │                      │
│  │  - Activos, traslados, usuarios       │                      │
│  │  - Historial de movimientos           │                      │
│  │  - Sesiones de inventario             │                      │
│  └───────────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

### Mapeo de Entrada/Salida a Canales

| Desde           | Hacia           | Protocolo       | Descripción                                   |
|-----------------|-----------------|-----------------|-----------------------------------------------|
| Flutter         | FastAPI         | HTTP REST/JSON  | El frontend consume los datos de la API       |
| FastAPI         | PostgreSQL      | SQL             | La API lee y escribe datos en la base de datos|
| FastAPI         | Firebase Storage| HTTPS           | Sube y descarga fotos de activos              |
| FastAPI         | Gmail SMTP      | SMTP            | Envía correos de notificación al usuario      |

---

# 4. Estrategia de Solución

El sistema se construye en **3 capas** bien definidas:

| Capa              | Tecnología       | Responsabilidad                                         |
|-------------------|------------------|---------------------------------------------------------|
| **Frontend**      | Flutter          | Interfaz de usuario para web y móvil                    |
| **Backend / API** | FastAPI (Python) | Lógica del negocio y endpoints REST                     |
| **Base de Datos** | PostgreSQL       | Almacenamiento persistente de todos los datos           |

### Decisiones principales

| Decisión                       | Elección               | ¿Por qué?                                                   |
|--------------------------------|------------------------|-------------------------------------------------------------|
| Framework frontend             | Flutter                | Un solo código para web y móvil, el equipo lo conoce        |
| Framework backend              | FastAPI                | Python sencillo, rápido y genera documentación automática   |
| Base de datos                  | PostgreSQL             | Relacional, gratuita y ya utilizada en materias anteriores  |
| Autenticación                  | JWT                    | Estándar seguro, fácil de implementar con FastAPI           |
| Control de versiones           | GitHub con ramas       | Trabajo colaborativo, cada uno trabaja en su propia rama    |
| Escaneo de activos             | QR con cámara del cel  | No requiere hardware adicional, Flutter lo soporta nativo   |
| Almacenamiento de fotos        | Firebase Storage       | Gratuito para proyectos pequeños, fácil de integrar         |
| Notificaciones por correo      | Gmail SMTP             | Gratuito y sencillo de configurar con Python                |

---

# 5. Vista de Bloques

## 5.1 Sistema General (Nivel 1)

```
┌──────────────────────────────────────────────────────────┐
│                    SISTEMA InnovaActivos                       │
│                                                          │
│  ┌───────────────────────────────────────────────────┐   │
│  │               FLUTTER (Frontend)                  │   │
│  │                                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐                │   │
│  │  │   Módulo    │  │   Módulo    │                 │   │
│  │  │   Activos   │  │  Traslados  │                 │   │
│  │  └─────────────┘  └─────────────┘                │   │
│  │  ┌─────────────┐  ┌─────────────┐                │   │
│  │  │   Módulo    │  │   Módulo    │                 │   │
│  │  │  Inventario │  │  Reportes  │                 │   │
│  │  └─────────────┘  └─────────────┘                │   │
│  └───────────────────────┬───────────────────────────┘   │
│                          │  API REST (HTTP/JSON)          │
│  ┌───────────────────────▼───────────────────────────┐   │
│  │               FASTAPI (Backend)                   │   │
│  │                                                   │   │
│  │  /activos    /traslados    /usuarios               │   │
│  │  /inventario /reportes    /auth                   │   │
│  └───────────────────────┬───────────────────────────┘   │
│                          │  SQL                           │
│  ┌───────────────────────▼───────────────────────────┐   │
│  │              POSTGRESQL (Base de Datos)           │   │
│  │                                                   │   │
│  │  activos | traslados | usuarios | movimientos_activos │   │
│  │  ubicaciones | categorias_activos | inventarios       │   │
│  └───────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

**Motivación:**
La separación en 3 capas permite que cada integrante trabaje de forma
independiente en su área sin afectar el trabajo de los demás.

## 5.2 Módulos del Frontend (Flutter)

### Estado actual implementado en interfaz

### Caja Negra 1: Módulo de Autenticación y Registro
**Responsabilidad:** Registro de cuenta, inicio de sesión y acceso a la app por perfil.
**Pantallas:** Registro, login y validaciones condicionales de acceso.
**Desarrollado por:** Jhouran Del Toro

### Caja Negra 2: Módulo de Activos
**Responsabilidad:** Visualizar activos disponibles y gestionar acciones según perfil.
**Pantallas:** Lista de activos y acciones de editar/actualizar/eliminar para administrador.
**Desarrollado por:** Jhouran Del Toro

### Caja Negra 3: Módulo de Envíos / Traslados
**Responsabilidad:** Mostrar el flujo de traslados de activos entre ubicaciones según tipo/clase.
**Pantallas:** Vista de envíos/traslados.
**Desarrollado por:** Jhouran Del Toro

### Caja Negra 4: Módulo de Bodega
**Responsabilidad:** Clasificación de activos dentro del inventario.
**Pantallas:** Vista de bodega con clasificación general.
**Desarrollado por:** Jhouran Del Toro

### Caja Negra 5: Módulo de Perfil de Usuario
**Responsabilidad:** Consultar y editar datos del usuario en tiempo real.
**Pantallas:** Perfil con datos de registro y cantidad de activos asociados al usuario.
**Desarrollado por:** Jhouran Del Toro

### Nota de estado
Los módulos de inventario avanzado, reportes y automatizaciones permanecen como parte del diseño objetivo y no se reportan como cerrados end-to-end en esta iteración.

## 5.3 Endpoints del Backend (FastAPI) – ✅ IMPLEMENTADOS

**Estructura del backend:** `app/` con 16 routers, 20+ modelos ORM, schemas Pydantic, servicios de negocio y utilidades core.
**Documentación automática:** Swagger UI en `/docs` y ReDoc en `/redoc`.

### Caja Negra 6: Autenticación (`app/routers/auth.py`)
| Endpoint           | Método | Descripción                                   | Acceso     |
|--------------------|--------|-----------------------------------------------|------------|
| `/auth/register`   | POST   | Registra un nuevo usuario                     | Público    |
| `/auth/login`      | POST   | Recibe correo y contraseña, devuelve JWT pair | Público    |
| `/auth/refresh`    | POST   | Renueva el access token con refresh token     | Autenticado|
| `/auth/logout`     | POST   | Revoca sesiones de refresh del usuario        | Autenticado|
| `/auth/me`         | GET    | Retorna perfil del usuario autenticado        | Autenticado|

### Caja Negra 7: Departamentos (`app/routers/departamentos.py`)
| Endpoint               | Método | Descripción              | Acceso  |
|------------------------|--------|--------------------------|--------|
| `/departamentos`       | GET    | Lista todos              | Auth   |
| `/departamentos`       | POST   | Crear departamento       | ADMIN+ |
| `/departamentos/{id}`  | GET    | Detalle                  | Auth   |
| `/departamentos/{id}`  | PUT    | Actualizar               | ADMIN+ |
| `/departamentos/{id}`  | DELETE | Desactivar (soft-delete) | ADMIN+ |

### Caja Negra 8: Usuarios (`app/routers/usuarios.py`)
| Endpoint                  | Método | Descripción             | Acceso      |
|---------------------------|--------|-------------------------|------------|
| `/usuarios`               | GET    | Listar (filtros, paginación) | ADMIN+ |
| `/usuarios/{id}`          | GET    | Detalle                 | ADMIN+ o propio |
| `/usuarios/{id}`          | PUT    | Actualizar perfil       | ADMIN+ o propio |
| `/usuarios/{id}/rol`      | PATCH  | Cambiar rol             | SUPERADMIN |
| `/usuarios/{id}/estado`   | PATCH  | Activar/desactivar      | ADMIN+     |

### Caja Negra 9: Ubicaciones (`app/routers/ubicaciones.py`)
| Endpoint               | Método | Descripción              | Acceso |
|------------------------|--------|--------------------------|-------|
| `/ubicaciones`         | GET    | Lista plana              | Auth  |
| `/ubicaciones/arbol`   | GET    | Árbol jerárquico         | Auth  |
| `/ubicaciones`         | POST   | Crear ubicación          | ADMIN+|
| `/ubicaciones/{id}`    | GET    | Detalle                  | Auth  |
| `/ubicaciones/{id}`    | PUT    | Actualizar               | ADMIN+|
| `/ubicaciones/{id}`    | DELETE | Soft-delete              | ADMIN+|

### Caja Negra 10: Categorías (`app/routers/categorias.py`)
| Endpoint             | Método | Descripción        | Acceso |
|----------------------|--------|--------------------|-------|
| `/categorias`        | GET    | Lista plana        | Auth  |
| `/categorias/arbol`  | GET    | Árbol jerárquico   | Auth  |
| `/categorias`        | POST   | Crear categoría    | ADMIN+|
| `/categorias/{id}`   | GET    | Detalle            | Auth  |
| `/categorias/{id}`   | PUT    | Actualizar         | ADMIN+|

### Caja Negra 11: Activos (`app/routers/activos.py`)
| Endpoint                     | Método | Descripción                              | Acceso |
|------------------------------|--------|------------------------------------------|-------|
| `/activos`                   | GET    | Lista paginada con filtros               | Auth  |
| `/activos`                   | POST   | Registra nuevo activo + movimiento       | ADMIN+|
| `/activos/escanear/{codigo}` | GET    | Busca por QR/barras/RFID                 | Auth  |
| `/activos/{id}`              | GET    | Detalle completo                         | Auth  |
| `/activos/{id}`              | PUT    | Actualizar datos + movimiento            | ADMIN+|
| `/activos/{id}`              | DELETE | Soft-delete (marca eliminado_en)         | ADMIN+|
| `/activos/{id}/estado`       | PATCH  | Cambiar estado + movimiento              | ADMIN+|
| `/activos/{id}/asignar`      | PATCH  | Reasignar a usuario + movimiento         | ADMIN+|
| `/activos/{id}/historial`    | GET    | Historial de movimientos del activo      | Auth  |

### Caja Negra 12: Documentos (`app/routers/documentos.py`)
| Endpoint                                 | Método | Descripción      | Acceso |
|------------------------------------------|--------|------------------|-------|
| `/activos/{activo_id}/documentos`        | GET    | Listar documentos| Auth  |
| `/activos/{activo_id}/documentos`        | POST   | Subir documento  | ADMIN+|
| `/activos/{activo_id}/documentos/{id}`   | DELETE | Eliminar         | ADMIN+|

### Caja Negra 13: Traslados (`app/routers/traslados.py`)
| Endpoint                        | Método | Descripción                            | Acceso |
|---------------------------------|--------|----------------------------------------|-------|
| `/traslados`                    | GET    | Lista (filtros por estado, paginación) | Auth  |
| `/traslados`                    | POST   | Crea solicitud de traslado             | Auth  |
| `/traslados/{id}`               | GET    | Detalle                                | Auth  |
| `/traslados/{id}/aprobar`       | PUT    | Aprueba traslado pendiente             | ADMIN+|
| `/traslados/{id}/rechazar`      | PUT    | Rechaza con motivo                     | ADMIN+|
| `/traslados/{id}/en-transito`   | PUT    | Marca en tránsito                      | ADMIN+|
| `/traslados/{id}/confirmar`     | PUT    | Confirma recepción (trigger DB)        | Auth  |
| `/traslados/{id}/cancelar`      | PUT    | Cancela traslado                       | Auth  |

### Caja Negra 14: Movimientos (`app/routers/movimientos.py`) – Solo lectura
| Endpoint                 | Método | Descripción                  | Acceso |
|--------------------------|--------|------------------------------|-------|
| `/movimientos`           | GET    | Lista paginada con filtros   | Auth  |
| `/movimientos/{activo_id}`| GET   | Historial de un activo       | Auth  |

### Caja Negra 15: Inventario (`app/routers/inventario.py`)
| Endpoint                            | Método | Descripción                            | Acceso   |
|-------------------------------------|--------|----------------------------------------|---------|
| `/inventario/sesiones`              | GET    | Lista sesiones                         | Auth    |
| `/inventario/sesiones`              | POST   | Inicia sesión (calcula total esperado) | TECNICO+|
| `/inventario/sesiones/{id}`         | GET    | Detalle con items                      | Auth    |
| `/inventario/sesiones/{id}/scan`    | POST   | Registra escaneo con clasificación auto| TECNICO+|
| `/inventario/sesiones/{id}/cerrar`  | PUT    | Cierra sesión y calcula faltantes      | TECNICO+|
| `/inventario/sesiones/{id}/reporte` | GET    | Reporte de la sesión                   | Auth    |

### Caja Negra 16: Sincronización Offline (`app/routers/sincronizacion.py`)
| Endpoint                               | Método | Descripción               | Acceso |
|----------------------------------------|--------|---------------------------|-------|
| `/sincronizacion/push`                 | POST   | Envía lote desde dispositivo| Auth |
| `/sincronizacion/conflictos`           | GET    | Lista conflictos pendientes| ADMIN+|
| `/sincronizacion/conflictos/{id}/resolver`| PUT | Resuelve conflicto        | ADMIN+|

### Caja Negra 17: Notificaciones (`app/routers/notificaciones.py`)
| Endpoint                       | Método | Descripción         | Acceso |
|--------------------------------|--------|---------------------|-------|
| `/notificaciones`              | GET    | Listar (filtro no leídas)| Auth|
| `/notificaciones`              | POST   | Crear notificación  | ADMIN+|
| `/notificaciones/{id}/leer`    | PUT    | Marcar como leída   | Auth  |
| `/notificaciones/leer-todas`   | PUT    | Marcar todas leídas | Auth  |

### Caja Negra 18: Reportes (`app/routers/reportes.py`)
| Endpoint          | Método | Descripción              | Acceso |
|-------------------|--------|--------------------------|-------|
| `/reportes`       | GET    | Listar mis reportes      | Auth  |
| `/reportes`       | POST   | Solicitar exportación    | Auth  |
| `/reportes/{id}`  | GET    | Estado del reporte       | Auth  |

### Caja Negra 19: Integraciones (`app/routers/integraciones.py`)
| Endpoint              | Método | Descripción          | Acceso |
|-----------------------|--------|----------------------|-------|
| `/integraciones`      | GET    | Listar trabajos      | ADMIN+|
| `/integraciones`      | POST   | Crear trabajo        | ADMIN+|
| `/integraciones/{id}` | GET    | Detalle              | ADMIN+|

### Caja Negra 20: Mantenimiento (`app/routers/mantenimiento.py`)
| Endpoint                     | Método | Descripción           | Acceso   |
|------------------------------|--------|-----------------------|---------|
| `/mantenimiento/planes`      | GET    | Listar planes         | Auth    |
| `/mantenimiento/planes`      | POST   | Crear plan            | ADMIN+  |
| `/mantenimiento/planes/{id}` | PUT    | Actualizar plan       | ADMIN+  |
| `/mantenimiento/ordenes`     | GET    | Listar órdenes        | Auth    |
| `/mantenimiento/ordenes`     | POST   | Crear orden           | TECNICO+|
| `/mantenimiento/ordenes/{id}`| GET    | Detalle orden         | Auth    |
| `/mantenimiento/ordenes/{id}`| PUT    | Actualizar orden      | TECNICO+|

### Caja Negra 21: Predicciones IA (`app/routers/predicciones.py`)
| Endpoint            | Método | Descripción          | Acceso |
|---------------------|--------|----------------------|-------|
| `/predicciones`     | GET    | Listar predicciones  | Auth  |
| `/predicciones`     | POST   | Registrar predicción | ADMIN+|
| `/predicciones/{id}`| GET    | Detalle              | Auth  |

## 5.4 Tablas de la Base de Datos (PostgreSQL)

### Caja Negra 22: Base de Datos

| Tabla                        | Descripción                                                   | Modelo ORM                       |
|------------------------------|---------------------------------------------------------------|----------------------------------|
| `departamentos`              | Catálogo de áreas/departamentos de la organización            | `app/models/departamento.py`     |
| `usuarios`                   | Usuarios, credenciales cifradas y rol                         | `app/models/usuario.py`          |
| `ubicaciones`                | Estructura física (edificio/piso/jerarquía)                   | `app/models/ubicacion.py`        |
| `categorias_activos`         | Clasificación y configuración de depreciación/mantenimiento   | `app/models/categoria_activo.py` |
| `activos`                    | Registro maestro de activos y su estado actual                | `app/models/activo.py`           |
| `documentos_activos`         | Documentos adjuntos (facturas, garantías, fotos)              | `app/models/documento_activo.py` |
| `traslados`                  | Flujo de traslado de activos entre ubicaciones                | `app/models/traslado.py`         |
| `movimientos_activos`        | Historial inmutable de cambios sobre activos                  | `app/models/movimiento_activo.py`|
| `sesiones_inventario`        | Sesiones de inventario físico                                 | `app/models/sesion_inventario.py`|
| `items_inventario`           | Detalle de escaneos por sesión                                | `app/models/item_inventario.py`  |
| `cola_sincronizacion`        | Cola de operaciones offline pendientes                        | `app/models/cola_sincronizacion.py`|
| `conflictos_sincronizacion`  | Conflictos detectados entre cliente y servidor                | `app/models/conflicto_sincronizacion.py`|
| `sesiones_autenticacion`     | Sesiones JWT de refresh token                                 | `app/models/sesion_autenticacion.py`|
| `notificaciones`             | Notificaciones para usuarios                                  | `app/models/notificacion.py`     |
| `entregas_notificacion`      | Seguimiento de entregas por canal                             | `app/models/entrega_notificacion.py`|
| `exportaciones_reportes`     | Solicitudes de exportación de reportes                        | `app/models/exportacion_reporte.py`|
| `trabajos_integracion`       | Trabajos de integración ERP (SAP/Odoo)                        | `app/models/trabajo_integracion.py`|
| `planes_mantenimiento`       | Planes de mantenimiento preventivo por activo                 | `app/models/plan_mantenimiento.py`|
| `ordenes_mantenimiento`      | Órdenes de trabajo de mantenimiento                           | `app/models/orden_mantenimiento.py`|
| `predicciones_ia`            | Predicciones de modelos ML sobre activos                      | `app/models/prediccion_ia.py`    |

### Diagrama Entidad-Relación
![Diagrama Entidad-Relación](Active%20Asset%20Management-2026-03-22-210133.svg)

Modelo completo en: `innova-activos.v2.sql`

**Diseñado por:** Nilson David Rivera

---

# 6. Vista de Ejecución

## Escenario 1: Escanear un Activo

```
Técnico        Flutter App       FastAPI          PostgreSQL
   │                │                │                 │
   │  Abre cámara   │                │                 │
   │───────────────►│                │                 │
   │  Escanea QR    │                │                 │
   │───────────────►│                │                 │
   │                │ GET /activos/  │                 │
   │                │ escanear/{cod} │                 │
   │                │───────────────►│                 │
   │                │                │ SELECT * FROM   │
   │                │                │ activos WHERE   │
   │                │                │ codigo = {cod}  │
   │                │                │────────────────►│
   │                │                │ datos del activo│
   │                │                │◄────────────────│
   │                │ 200 {activo}   │                 │
   │                │◄───────────────│                 │
   │ Muestra info   │                │                 │
   │◄───────────────│                │                 │
```

## Escenario 2: Solicitar y Aprobar un Traslado

```
Empleado       Flutter App      FastAPI         PostgreSQL      Supervisor
   │                │               │                │               │
   │ Llena form.    │               │                │               │
   │───────────────►│               │                │               │
   │                │ POST          │                │               │
   │                │ /traslados    │                │               │
   │                │──────────────►│                │               │
   │                │               │ INSERT INTO    │               │
   │                │               │ traslados      │               │
   │                │               │───────────────►│               │
   │                │               │ Envía email    │               │
   │                │               │ al supervisor  │───────────────►
   │ Traslado creado│               │                │               │
   │◄───────────────│               │                │               │
   │                │               │                │   Aprueba     │
   │                │               │◄───────────────────────────────│
   │                │               │ PUT /traslados │               │
   │                │               │ /{id}/aprobar  │               │
   │                │               │ UPDATE estado  │               │
   │                │               │───────────────►│               │
   │ Notificación   │               │                │               │
   │◄───────────────│               │                │               │
```

## Escenario 3: Inventario Sin Conexión a Internet

```
Técnico     Flutter (sin internet)   Memoria local    [Vuelve internet]   FastAPI
   │                 │                     │                  │               │
   │ Inicia sesión   │                     │                  │               │
   │────────────────►│                     │                  │               │
   │ Escanea activo 1│                     │                  │               │
   │────────────────►│ Guarda localmente   │                  │               │
   │                 │────────────────────►│                  │               │
   │ Escanea activo 2│                     │                  │               │
   │────────────────►│ Guarda localmente   │                  │               │
   │                 │────────────────────►│                  │               │
   │                 │    [Detecta conexión disponible]       │               │
   │                 │                     │ Envía datos      │               │
   │                 │─────────────────────────────────────── │               │
   │                 │                     │    POST /inventario/sesiones/sync │
   │                 │                     │                  │──────────────►│
   │ Sincronizado ✓  │                     │                  │               │
   │◄────────────────│                     │                  │               │
```

---

# 7. Vista de Despliegue

## 7.1 Nivel 1 – Visión General

```
┌─────────────────────────────────────────────────────────────────┐
│                      DESPLIEGUE InnovaActivos                        │
│                                                                 │
│  DISPOSITIVOS DEL USUARIO                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Navegador Web│  │  Android     │  │     iOS      │          │
│  │(Flutter Web) │  │(Flutter App) │  │(Flutter App) │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         └─────────────────┼─────────────────┘                  │
│                           │  HTTPS                              │
│  SERVIDOR                 │                                     │
│  ┌────────────────────────▼──────────────────────────────────┐  │
│  │  FastAPI                                                  │  │
│  │  Puerto 8000 – API REST                                   │  │
│  └────────────────────────┬──────────────────────────────────┘  │
│                           │  SQL                                │
│  ┌────────────────────────▼──────────────────────────────────┐  │
│  │  PostgreSQL                                               │  │
│  │  Puerto 5432 – Base de datos                              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  SERVICIOS EXTERNOS (gratuitos)                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │   Firebase Storage (fotos)  │  Gmail SMTP (correos)     │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────���─────────────────────────────────────────────────┘
```

## 7.2 Nivel 2 – Opciones de Despliegue

| Entorno     | Herramienta         | Descripción                                      |
|-------------|---------------------|--------------------------------------------------|
| Local       | Computador propio   | Cada integrante corre el sistema en su máquina   |
| Backend     | Render / Railway    | Plataformas gratuitas para publicar FastAPI      |
| Base de datos| Render (PostgreSQL)| Base de datos gratuita en la nube                |
| Frontend Web| Firebase Hosting    | Hosting gratuito para publicar Flutter Web       |
| Repositorio | GitHub              | Control de versiones y colaboración del equipo   |

---

# 8. Conceptos Transversales (Cross-cutting)

## Concepto 1: Seguridad

- Las contraseñas se almacenan cifradas con **bcrypt**, nunca en texto plano
- Al hacer login, FastAPI devuelve un **token JWT** que Flutter guarda
- Cada petición a la API incluye el token en el header `Authorization`
- FastAPI verifica el token antes de responder cualquier solicitud
- Cada rol tiene acceso solo a lo que le corresponde

## Concepto 2: Manejo de Errores

Si la API falla o hay un error, Flutter muestra un mensaje claro al usuario.
Los errores siguen este formato estándar en toda la API:

```json
{
  "error": "ACTIVO_NO_ENCONTRADO",
  "mensaje": "No existe un activo con el código QR escaneado",
  "codigo": 404
}
```

## Concepto 3: Historial Inmutable de Movimientos

- Cada vez que un activo cambia de ubicación, estado o responsable,
  FastAPI **inserta** un registro nuevo en la tabla `movimientos_activos`
- Esa tabla **nunca se modifica ni se elimina**, solo se pueden insertar registros
- Esto garantiza que siempre se pueda consultar el historial completo de cualquier activo

## Concepto 4: Modo Offline

- Cuando no hay internet, Flutter guarda los escaneos en la memoria del dispositivo
- Cuando vuelve la conexión, la app envía automáticamente los datos guardados a la API
- El usuario ve un indicador visual: **"Sin conexión – guardando localmente"**

## Concepto 5: Roles y Permisos – ✅ IMPLEMENTADO EN API

| Rol           | Estado              | Permisos en API                                                                    |
|---------------|---------------------|----------------------------------------------------------------------------------|
| `SUPERADMIN`  | ✅ Implementado     | Acceso total, cambiar roles de usuarios, gestión completa                        |
| `ADMIN`       | ✅ Implementado     | CRUD de activos, ubicaciones, categorías, aprobar traslados, gestión de usuarios |
| `AUDITOR`     | ✅ Implementado     | Lectura de movimientos, reportes, historial de activos                           |
| `CUSTODIO`    | ✅ Implementado     | Consultar activos asignados, solicitar traslados, ver notificaciones             |
| `TECNICO`     | ✅ Implementado     | Inventario físico (escaneo), mantenimiento (órdenes), consultas                  |

**Implementación técnica:** `app/core/dependencies.py` con `RoleChecker` reutilizable y atajos `require_admin`, `require_superadmin`, `require_tecnico`, `require_auditor`.

---

# 9. Decisiones de Diseño

| ID    | Decisión                             | Opciones evaluadas              | ¿Por qué elegimos esta?                                     |
|-------|--------------------------------------|---------------------------------|-------------------------------------------------------------|
| AD-01 | Frontend en Flutter                  | React Native, solo web          | El equipo lo conoce y funciona en web y móvil a la vez      |
| AD-02 | Backend en FastAPI                   | Django, Node.js, Spring         | Python es el lenguaje que más domina el equipo              |
| AD-03 | Base de datos PostgreSQL             | MySQL, Firebase, MongoDB        | Es relacional, gratuita y el equipo ya la ha usado          |
| AD-04 | Autenticación con JWT                | Sesiones en servidor, cookies   | Estándar moderno, fácil de implementar con FastAPI          |
| AD-05 | GitHub con ramas por funcionalidad   | Trabajar todos en main          | Evita conflictos cuando varios trabajan simultáneamente     |
| AD-06 | Firebase Storage para fotos          | Servidor propio, Cloudinary     | Gratuito, fácil de integrar con Flutter                     |
| AD-07 | Gmail SMTP para correos              | SendGrid, servidor propio       | Gratuito y sencillo de configurar desde Python              |
| AD-08 | Historial de movimientos inmutable   | Solo guardar el estado actual   | Permite auditorías completas, es requisito del proyecto     |
| AD-09 | API REST con JSON                    | GraphQL, SOAP                   | Más sencillo de implementar y de probar con herramientas    |
| AD-10 | Arquitectura en 3 capas              | Microservicios                  | Adecuada para el tamaño del equipo y el tiempo disponible   |

---

# 10. Requerimientos de Calidad

## 10.1 Árbol de Calidad

```
Calidad InnovaActivos
├── Funcionalidad
│   ├── Registrar y consultar activos correctamente
│   └── Traslados con flujo completo (solicitud → aprobación → confirmación)
├── Confiabilidad
│   ├── No perder datos cuando se pierde la conexión a internet
│   └── El historial de movimientos no se puede alterar
├── Rendimiento
│   ├── La API responde en menos de 2 segundos
│   └── El escaneo QR identifica el activo en menos de 3 segundos
├── Seguridad
│   ├── Solo usuarios autenticados con JWT acceden al sistema
│   └── Cada rol solo puede ver y hacer lo que le corresponde
└── Usabilidad
    ├── Un técnico aprende a usar la app en menos de 10 minutos
    └── El flujo de escaneo tiene máximo 3 pasos
```

## 10.2 Escenarios de Calidad

| ID   | Atributo       | Situación                                          | Respuesta esperada                                   | Medición                             |
|------|----------------|----------------------------------------------------|------------------------------------------------------|--------------------------------------|
| EQ-1 | Rendimiento    | 20 usuarios usan la app al mismo tiempo            | La app responde sin lentitud notable                 | Tiempo de respuesta menor a 2 seg    |
| EQ-2 | Confiabilidad  | Técnico pierde internet durante toma de inventario | Los escaneos se guardan y sincronizan al volver      | Cero datos perdidos al sincronizar   |
| EQ-3 | Seguridad      | Alguien intenta entrar sin credenciales válidas    | El sistema rechaza el acceso con código 401          | 100% de peticiones sin token rechazadas|
| EQ-4 | Trazabilidad   | Auditor busca quién movió un activo hace 3 meses   | El sistema muestra el historial completo del activo  | Historial visible en menos de 2 seg  |
| EQ-5 | Usabilidad     | Técnico nuevo usa la app por primera vez           | Puede completar un escaneo sin ayuda externa         | Tarea completada en menos de 5 min   |
| EQ-6 | Disponibilidad | El servidor tiene un problema temporal             | La app muestra mensaje claro de error al usuario     | El usuario entiende qué pasó         |

---

# 11. Riesgos y Deuda Técnica

## Riesgos del Proyecto

| ID   | Riesgo                                                           | Probabilidad | Impacto | Plan de mitigación                                           |
|------|------------------------------------------------------------------|--------------|---------|--------------------------------------------------------------|
| R-01 | Un integrante del equipo se atrasa en su módulo                  | Alta         | Alto    | Reuniones semanales y tareas registradas en GitHub Issues    |
| R-02 | La sincronización offline presenta errores difíciles de detectar | Media        | Alto    | Probar el flujo offline desde el inicio del desarrollo       |
| R-03 | Problemas de CORS entre Flutter y FastAPI                        | Alta         | Medio   | Configurar CORS en FastAPI desde el primer día de desarrollo |
| R-04 | El modelo de base de datos necesita cambios cuando ya hay datos  | Media        | Medio   | Diseñar bien las tablas antes de escribir cualquier código   |
| R-05 | El tiempo del semestre no alcanza para todos los módulos         | Media        | Alto    | Priorizar los RF de prioridad Alta; los de Media son opcionales|
| R-06 | Conflictos en el repositorio de GitHub entre ramas              | Alta         | Medio   | Usar Gitflow y hacer code reviews antes de hacer merge       |

## Deuda Técnica (funcionalidades para versiones futuras)

| Funcionalidad                            | Estado                    | Nota                                                     |
|------------------------------------------|---------------------------|----------------------------------------------------------|
| ~~Exportación de reportes~~              | ✅ Endpoint listo         | Falta implementar generación real de PDF/XLSX/CSV        |
| ~~Integración con sistemas ERP~~         | ✅ Endpoint listo         | Falta conectar con SAP/Odoo reales                       |
| ~~Mantenimiento preventivo~~             | ✅ Endpoint listo         | Planes y órdenes funcionales                             |
| ~~Predicciones IA~~                      | ✅ Endpoint listo         | Falta conectar con modelos ML reales                     |
| Notificaciones push en el celular        | Pendiente                 | Requiere configuración adicional de Firebase             |
| Soporte para lectores RFID               | Parcial (campo en modelo) | Requiere hardware especial no disponible en el equipo    |
| Dashboard con gráficas avanzadas         | Pendiente                 | Se implementará en el frontend Flutter                   |
| Envío real de correos SMTP               | Pendiente                 | El endpoint de notificaciones existe, falta integrar SMTP|

---

# 12. Glosario

| Término                 | Definición                                                                                          |
|-------------------------|-----------------------------------------------------------------------------------------------------|
| **Activo Fijo**         | Bien físico de una empresa (computador, silla, impresora) con vida útil mayor a un año              |
| **Traslado**            | Mover un activo de un área o persona a otra, dejando un registro documentado                        |
| **Custodio**            | Empleado responsable de cuidar y usar correctamente un activo asignado                              |
| **Código QR**           | Código en forma de cuadrado que la cámara puede leer para identificar un activo                     |
| **Inventario físico**   | Proceso de verificar que los activos están físicamente donde el sistema dice que están              |
| **Inconsistencia**      | Cuando un activo no está donde el sistema dice, o hay activos físicos sin registro en el sistema    |
| **Trazabilidad**        | Capacidad de ver todo el historial de un activo: quién lo tuvo, dónde estuvo y cuándo se movió     |
| **JWT**                 | Token de seguridad que el sistema entrega al hacer login para identificar al usuario en cada petición|
| **API REST**            | Forma estándar de comunicación entre Flutter (frontend) y FastAPI (backend) usando HTTP             |
| **FastAPI**             | Framework de Python para construir APIs de forma rápida con documentación automática                |
| **Flutter**             | Framework de Google para crear aplicaciones que funcionan en web, Android e iOS con un solo código  |
| **PostgreSQL**          | Sistema de base de datos relacional donde se guardan todos los datos del sistema                    |
| **Firebase Storage**    | Servicio de Google para almacenar archivos (fotos de activos) en la nube de forma gratuita          |
| **Rol**                 | Conjunto de permisos asignados a un tipo de usuario (admin, técnico, auditor, empleado)             |
| **Historial inmutable** | Registros que solo se pueden leer; nunca modificar ni borrar, garantizando la trazabilidad          |
| **CORS**                | Configuración que permite que Flutter (en web) pueda hacer peticiones a la API de FastAPI           |
| **Bcrypt**              | Algoritmo para cifrar contraseñas de forma segura antes de guardarlas en la base de datos           |
| **Endpoint**            | Dirección URL de la API a la que Flutter envía peticiones (ej: `/activos`, `/traslados`)            |
| **GitHub Issues**       | Sistema de tareas dentro del repositorio de GitHub para organizar el trabajo del equipo             |
| **Gitflow**             | Estrategia de trabajo con ramas en GitHub: cada funcionalidad se desarrolla en su propia rama       |

---

*Proyecto: InnovaActivos – Sistema de Gestión de Inventario de Activos Fijos*
*Universidad Tecnológica de Bolívar – Ingeniería en Sistemas – 7mo Semestre*
*Materia: Arquitectura de Software | Marzo 2026*
*Equipo: Ricardo Chacón · Jose Chima · Jhouran Del Toro · Nilson David · Dilson Rivera*
