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
| [C4 nivel 2 — Contenedores](docs/c4/nivel2-contenedores.md) | Diagrama de contenedores del sistema. |
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

## Estructura del repositorio

```powershell
AS_202620_uniTeam/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada
│   ├── api/                    # Capa de presentación (endpoints HTTP)
│   ├── domain/                 # Reglas de negocio (vacío - para Semana 4)
│   ├── application/            # Casos de uso (vacío - para Semana 4)
│   ├── events/                 # Eventos y consumidores (vacío - para Semana 4)
│   └── infrastructure/         # DB, mensajería (vacío - para Semana 4)
├── tests/
│   ├── __init__.py
│   └── test_health.py          # Prueba en verde
├── requirements.txt
├── CLAUDE.md
├── .gitignore
└── README.md
```

## Tecnologias utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **FastAPI** | 0.112.4 | Framework web para el backend |
| **Uvicorn** | 0.30.6 | Servidor para ejecutar FastAPI |
| **Next.js** | *Por definir* | Framework frontend (React) |
| **MySQL** | *Por definir* | Base de datos relacional |
| **Pytest** | 8.3.4 | Framework de pruebas automatizadas |
| **HTTPX** | 0.27.2 | Cliente HTTP para pruebas |

## ¿Cómo ejecutar el esqueleto del proyecto?

### 1. Clonar el repositorio

```powershell
git clone <url-del-repositorio>
cd AS_202620_uniTeam
```
### 2. Crear y activar el entorno virtual

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependecias
```powershell
pip install -r requirements.txt
```

### 4. Arrancar la aplicacion
```powershell
uvicorn app.main:app --reload
```

### 5. Ejecutar la prueba verde

```powershell
pytest -v
```

**resultado esperado** 

```powershell
================= test session starts =================
collected 1 item

tests/test_health.py::test_health PASSED       [100%]

================= 1 passed in 0.50s ==================
```
