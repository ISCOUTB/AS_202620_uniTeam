# UniTeam — Plataforma colaborativa para equipos universitarios

### Integrantes del equipo

* Julio César Emiliani
* Ian Novoa Carrillo
* Juan Jose Bustamante
* Daniel Isaac Manjarres

### Idea original y aporte del prototipo

**UniTeam** es una herramienta web para facilitar la organización y coordinación de equipos de trabajo universitarios.

La idea consiste en centralizar la gestión de las actividades de un equipo en una sola plataforma. Los integrantes podrán crear tareas, asignarlas a otros miembros, establecer una prioridad, definir un estado y realizar seguimiento a su progreso.

El prototipo busca solucionar el problema de tener la información del trabajo grupal dispersa entre diferentes medios de comunicación y herramientas. UniTeam permitirá que cada integrante pueda identificar fácilmente **qué tareas existen, quién es responsable de ellas, qué prioridad tienen y cuál es su estado**.

### Stakeholders o beneficiarios

* **Estudiantes:** serán los principales usuarios de UniTeam. Podrán organizar sus proyectos, distribuir tareas entre los integrantes y realizar seguimiento al trabajo del equipo.
* **Equipos de trabajo universitarios:** se beneficiarán de una herramienta centralizada para coordinar responsabilidades y mejorar la organización del trabajo colaborativo.
* **Profesores:** podrán beneficiarse del sistema como herramienta de seguimiento de los proyectos y actividades realizadas por los equipos.
* **Universidad:** podrá beneficiarse indirectamente de una herramienta que facilite la organización y colaboración durante el desarrollo de proyectos académicos.

El mapa completo de interesados, con lo que le importa a cada uno y los conflictos entre sus intereses, está en [`docs/calidad/interesados.md`](docs/calidad/interesados.md).

### Documentación

| Documento | Contenido |
|-----------|-----------|
| [Ficha del problema](docs/ficha.md) | Problema, propuesta, usuarios y alcance del prototipo. |
| [Aspectos declarados](docs/aspectos.md) | Capacidades comprometidas, cada una enlazada con su escenario de calidad. |
| [Arquitectura (arc42)](docs/arc42/arc42-uniteam.md) | Objetivos, restricciones, contexto y requisitos de calidad. |
| [Mapa de interesados](docs/calidad/interesados.md) | Interesados, atributos derivados y conflictos entre ellos. |
| [Escenarios de calidad](docs/calidad/escenarios-calidad.md) | Cinco escenarios de seis partes con medidas verificables. |
| [Árbol de utilidad](docs/calidad/arbol-utilidad.md) | Priorización por impacto en el negocio y riesgo técnico. |
| [C4 nivel 1 — Contexto](docs/c4/nivel1-contexto.md) | Diagrama de contexto del sistema. |
| [C4 nivel 2 — Contenedores](docs/c4/nivel2-contenedores.md) | Contenedores y su correspondencia con el código. |
| [Decisiones de arquitectura](docs/adr/) | Registro de decisiones (ADR). |
| [Uso de IA y decisiones del equipo](docs/ia.md) | Bitácora de uso de IA generativa y registro de decisiones. |

### Entrega S2 — Interesados y escenarios de calidad

| Solicitud | Dónde encontrarlo |
|-----------|-----------|
| arc42 secciones 1–3 | [arc42 §1](docs/arc42/arc42-uniteam.md#1-introducción-y-objetivos) · [§2](docs/arc42/arc42-uniteam.md#2-restricciones-de-la-arquitectura) · [§3](docs/arc42/arc42-uniteam.md#3-contexto-y-alcance) |
| Árbol de utilidad | [docs/calidad/arbol-utilidad.md](docs/calidad/arbol-utilidad.md) — también en [arc42 §10.1](docs/arc42/arc42-uniteam.md#101-árbol-de-calidad) |
| 3–5 escenarios de calidad con medida | [docs/calidad/escenarios-calidad.md](docs/calidad/escenarios-calidad.md) (5 escenarios) — resumen en [arc42 §10.2](docs/arc42/arc42-uniteam.md#102-escenarios-de-calidad) |
| Restricciones justificadas | [arc42 §2](docs/arc42/arc42-uniteam.md#2-restricciones-de-la-arquitectura): técnicas, organizativas y legales |
| C4 de contexto (nivel 1) | [docs/c4/nivel1-contexto.md](docs/c4/nivel1-contexto.md) |
| Resumen del proceso (1 página) | [docs/entregas/S2-resumen.md](docs/entregas/S2-resumen.md) — el PDF se entrega aparte, fuera del repositorio |

## Cómo se arranca

**Requisitos previos:** Docker con el complemento Compose (`docker compose version`). Nada más:
ni Python ni MySQL instalados en la máquina.

```bash
docker compose up
```

Ese único comando construye la API, levanta MySQL, espera a que responda y arranca el sistema en
<http://localhost:8000>. La documentación interactiva de la API queda en
<http://localhost:8000/docs>, y `GET /activo` responde `{"status": "ok"}` cuando todo está en pie.

Para detenerlo, `Ctrl+C`; para borrar también los datos, `docker compose down -v`.

### Recorrido de ejemplo

```bash
# 1. Crear un proyecto (quien lo crea queda como líder)
curl -X POST localhost:8000/proyectos \
  -H "Content-Type: application/json" -H "X-Usuario: ana" \
  -d '{"nombre":"Proyecto de Arquitectura","miembros":["bruno"]}'

# 2. Crear una tarea dentro de él (usa el id devuelto arriba)
curl -X POST localhost:8000/proyectos/<ID>/tareas \
  -H "Content-Type: application/json" -H "X-Usuario: ana" \
  -d '{"titulo":"Redactar la sección 5","prioridad":"alta","responsable":"bruno"}'

# 3. Consultar el tablero
curl localhost:8000/proyectos/<ID>/tareas -H "X-Usuario: bruno"

# 4. Un usuario ajeno al proyecto recibe 403 y queda registrado en auditoría (ESC-03)
curl -i localhost:8000/proyectos/<ID>/tareas -H "X-Usuario: intruso"
```

> **Identidad provisional.** La cabecera `X-Usuario` sustituye al proveedor de identidad
> mientras no se integra OIDC (ver [C4 nivel 2](docs/c4/nivel2-contenedores.md)). No es
> autenticación y no debe exponerse fuera de un entorno de desarrollo. La **autorización** sí es
> real: cada operación comprueba la pertenencia al proyecto contra la base de datos.

### Alternativa sin Docker

Si prefieres no usar contenedores, hace falta Python 3.11 o superior y, para la persistencia
real, un MySQL accesible:

```bash
python -m venv .venv && . .venv/bin/activate    # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Sin `DATABASE_URL` definida arranca sobre un SQLite local, útil para probar la API pero **no**
es el entorno soportado (ver [ADR 0004](docs/adr/0004-usar-mysql-como-base-de-datos.md)).

## Cómo se prueba

En integración continua las pruebas se ejecutan **contra MySQL** en cada `push`
(ver [`.github/workflows/ci.yml`](.github/workflows/ci.yml)).

En local, sin levantar servicios:

```bash
python -m venv .venv && . .venv/bin/activate    # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

Sin `DATABASE_URL` definida, las pruebas usan un SQLite temporal. Para ejecutarlas contra el
MySQL de Docker:

```bash
docker compose up -d db
DATABASE_URL="mysql+pymysql://uniteam:uniteam@127.0.0.1:3306/uniteam" pytest -v
```

## Corte vertical

El recorrido que atraviesa las tres capas, para seguirlo en el código:

| Tramo | Ruta |
|-------|------|
| Interfaz | [`app/api/rutas_tareas.py`](app/api/rutas_tareas.py) — endpoints HTTP |
| Lógica | [`app/application/servicio_tareas.py`](app/application/servicio_tareas.py) — casos de uso y autorización |
| Dominio | [`app/domain/modelos.py`](app/domain/modelos.py) — entidades y flujo de estados |
| Eventos | [`app/application/bus.py`](app/application/bus.py) · [`app/events/consumidores.py`](app/events/consumidores.py) |
| Persistencia | [`app/infrastructure/repositorios.py`](app/infrastructure/repositorios.py) — MySQL vía SQLAlchemy |
| Prueba de punta a punta | [`test/test_corte_vertical.py`](test/test_corte_vertical.py) |

## Estructura del repositorio

```text
AS_202620_uniTeam/
├── app/
│   ├── main.py                 # Composición de la app y traducción de errores a HTTP
│   ├── config.py               # Configuración leída del entorno
│   ├── api/                    # Interfaz: endpoints, esquemas y dependencias
│   ├── application/            # Casos de uso, puertos y bus de eventos
│   ├── domain/                 # Entidades, flujo de estados y eventos de dominio
│   ├── events/                 # Consumidores (auditoría)
│   └── infrastructure/         # Motor, tablas y repositorios (MySQL)
├── test/                       # Pruebas, incluida la del recorrido completo
├── docs/                       # arc42, ADR, C4, aspectos y registro de IA
├── compose.yaml                # Arranque con un comando
├── Dockerfile
└── requirements.txt
```

## Tecnologías

| Tecnología | Versión | Propósito | Decisión |
|------------|---------|-----------|----------|
| FastAPI | 0.112.4 | Backend | [ADR 0002](docs/adr/0002-usar-fastapi-y-nextjs.md) |
| Uvicorn | 0.30.6 | Servidor ASGI | — |
| SQLAlchemy | 2.0.36 | Acceso a datos | [ADR 0004](docs/adr/0004-usar-mysql-como-base-de-datos.md) |
| MySQL | 8.4 | Base de datos | [ADR 0004](docs/adr/0004-usar-mysql-como-base-de-datos.md) |
| Next.js | *pendiente* | Frontend (semana 6) | [ADR 0002](docs/adr/0002-usar-fastapi-y-nextjs.md) |
| Pytest | 8.3.4 | Pruebas | — |
