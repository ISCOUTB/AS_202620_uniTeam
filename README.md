# UniTeam

**Gestión colaborativa de tareas para equipos universitarios.** Centraliza qué hay que hacer,
quién responde por cada cosa, qué prioridad tiene y en qué estado está — información que hoy
vive dispersa entre chats, documentos y hojas de cálculo.

[![CI](https://github.com/ISCOUTB/AS_202620_uniTeam/actions/workflows/ci.yml/badge.svg)](https://github.com/ISCOUTB/AS_202620_uniTeam/actions/workflows/ci.yml)

Proyecto de la asignatura **Arquitecturas de Software**, semestre 2026-20 · Universidad
Tecnológica de Bolívar.

---

## Arranque rápido

**Requisito previo:** Docker con el complemento Compose (`docker compose version`). Nada más.

```bash
docker compose up
```

Ese único comando levanta los tres contenedores y deja el sistema en marcha:

| Servicio | URL | Qué es |
|----------|-----|--------|
| Aplicación Web | <http://localhost:3000> | Interfaz de usuario (Next.js) |
| API | <http://localhost:8000> | Backend (FastAPI) · documentación interactiva en `/docs` |
| Proveedor de identidad | <http://localhost:9000> | Emisor OIDC **de desarrollo** |
| Base de datos | `localhost:3306` | MySQL 8.4 |

Pulsa **Iniciar sesión**, escribe un nombre en el emisor de desarrollo y vuelves autenticado.

Para detenerlo, `Ctrl+C`. Para borrar también los datos, `docker compose down -v`.

> **El emisor de desarrollo no autentica a nadie.** Firma un token con el nombre que se le pida,
> para que el sistema se pueda ejercitar sin cuentas externas. **Nunca debe desplegarse fuera de
> desarrollo**; en su lugar va la cuenta institucional o Google, que es configuración
> (`OIDC_EMISOR`, `OIDC_AUDIENCIA`) y no código.

### Autenticación y autorización

Son dos cosas distintas y conviene no confundirlas:

- **Autenticación.** UniTeam no guarda contraseñas: delega en un proveedor OpenID Connect
  ([ADR 0005](docs/adr/0005-delegar-la-autenticacion-en-un-proveedor-oidc.md)). La aplicación web
  hace el flujo de código con PKCE y envía el token en `Authorization: Bearer`; la API lo
  verifica en cada petición contra el JWKS del emisor, comprobando firma, emisor, audiencia y
  caducidad.
- **Autorización.** Estar autenticado no da acceso a nada: cada operación comprueba contra la
  base de datos que el usuario pertenezca al proyecto. Quien no pertenece recibe `403` y el
  intento queda en el registro de auditoría ([ESC-03](docs/calidad/escenarios-calidad.md#esc-03)).

---

## Arquitectura

UniTeam es un sistema de tres contenedores, descritos en el
[C4 de contenedores](docs/c4/nivel2-contenedores.md):

```
Navegador ──HTTPS──▶ Aplicación Web ──REST/JSON──▶ API ──SQL──▶ MySQL
                       (Next.js)                (FastAPI)
```

El backend sigue un estilo orientado a eventos con **despacho en proceso**
([ADR 0003](docs/adr/0003-usar-eventos-de-dominio-en-proceso.md)): no hay broker ni cola
externa. Las reglas de negocio viven en un dominio que no depende de ningún framework, y la
persistencia queda detrás de repositorios.

| Documento | Contenido |
|-----------|-----------|
| [Documentación arc42](docs/arc42/arc42-uniteam.md) | Objetivos, restricciones, contexto, bloques de construcción y vista de ejecución. |
| [C4 nivel 1 — Contexto](docs/c4/nivel1-contexto.md) · [nivel 2 — Contenedores](docs/c4/nivel2-contenedores.md) | Diagramas como código, en Mermaid. |
| [Decisiones de arquitectura](docs/adr/) | Un ADR por decisión, con contexto, alternativas y consecuencias. |
| [Escenarios de calidad](docs/calidad/escenarios-calidad.md) | Cinco escenarios de seis partes con medida verificable. |
| [Árbol de utilidad](docs/calidad/arbol-utilidad.md) · [Interesados](docs/calidad/interesados.md) | Priorización por impacto y riesgo, y de dónde sale. |
| [Tabla de aspectos](docs/aspectos.md) | Trazabilidad de aspecto a evidencia, eslabón por eslabón. |
| [Uso de IA](docs/ia.md) | Qué se pidió, qué se aceptó y qué se rechazó, con su motivo. |
| [Ficha del problema](docs/ficha.md) | Problema, usuarios y alcance del prototipo. |

---

## API

Toda operación sobre un proyecto exige pertenecer a él.

| Método | Ruta | Qué hace |
|--------|------|----------|
| `POST` | `/proyectos` | Crea un proyecto; quien lo crea queda como líder. |
| `GET` | `/proyectos` | Lista los proyectos del usuario. Nunca devuelve ajenos. |
| `GET` | `/proyectos/{id}` | Detalle del proyecto con sus miembros y roles. |
| `POST` | `/proyectos/{id}/miembros` | Agrega un miembro. Reservado al líder. |
| `GET` | `/proyectos/{id}/progreso` | Resumen del avance, calculado en la base de datos. |
| `POST` | `/proyectos/{id}/tareas` | Crea una tarea. |
| `GET` | `/proyectos/{id}/tareas` | Tablero, con filtros `estado` y `responsable` y paginación. |
| `GET` | `/proyectos/{id}/tareas/{tarea}` | Detalle de una tarea. |
| `PUT` | `/proyectos/{id}/tareas/{tarea}/responsable` | Asigna la tarea a un miembro. |
| `PUT` | `/proyectos/{id}/tareas/{tarea}/estado` | Mueve la tarea de estado. |

Ejemplo completo:

Todas las peticiones necesitan un token. Sin él, la API responde `401`.

```bash
TOKEN="<el token que devuelve el proveedor de identidad>"

# Crear un proyecto
curl -X POST localhost:8000/proyectos \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{"nombre":"Proyecto de Arquitectura","miembros":["bruno@utb.edu.co"]}'

# Crear una tarea dentro de él
curl -X POST localhost:8000/proyectos/<ID>/tareas \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{"titulo":"Redactar la sección 5","prioridad":"alta"}'

# Consultar el tablero
curl localhost:8000/proyectos/<ID>/tareas -H "Authorization: Bearer $TOKEN"

# Sin credencial: 401
curl -i localhost:8000/proyectos
```

---

## Desarrollo

### Backend

Requiere Python 3.11 o superior.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Sin `DATABASE_URL` definida arranca sobre un SQLite local, cómodo para desarrollo pero **no es
el entorno soportado** ([ADR 0004](docs/adr/0004-usar-mysql-como-base-de-datos.md)). Para
trabajar contra MySQL:

```bash
docker compose up -d db
export DATABASE_URL="mysql+pymysql://uniteam:uniteam@127.0.0.1:3306/uniteam"
```

### Frontend

Requiere Node.js 20 o superior. Con la API ya en marcha:

```bash
cd web
npm install
npm run dev
```

| Variable | Dónde | Por defecto | Para qué |
|----------|-------|-------------|----------|
| `DATABASE_URL` | API | SQLite local | Conexión a la base de datos. |
| `OIDC_EMISOR` | API | — | Emisor esperado en el token. **Obligatoria.** |
| `OIDC_AUDIENCIA` | API | — | Audiencia esperada en el token. **Obligatoria.** |
| `OIDC_JWKS_URL` | API | se descubre | Útil cuando la API alcanza al emisor por otra URL que el navegador. |
| `OIDC_CLAIM_USUARIO` | API | `email` | Claim del que sale la identidad. |
| `ORIGENES_PERMITIDOS` | API | `http://localhost:3000` | Orígenes que la API acepta por CORS. |
| `NEXT_PUBLIC_API_URL` | Web | `http://localhost:8000` | Dónde está la API. |
| `NEXT_PUBLIC_OIDC_EMISOR` | Web | `http://localhost:9000` | Proveedor de identidad. |
| `NEXT_PUBLIC_OIDC_CLIENTE` | Web | `uniteam-web` | Identificador de cliente OIDC. |

Las variables `NEXT_PUBLIC_*` se hornean al compilar el frontend, no al arrancarlo.

---

## Pruebas

```bash
pytest -v                                    # 30 pruebas
python scripts/verificar_enlaces.py          # enlaces de la documentación
cd web && npm run build                      # comprueba tipos y compilación
```

En integración continua las pruebas se ejecutan **contra MySQL** en cada `push`, junto con la
verificación de enlaces y la compilación del frontend
([`.github/workflows/ci.yml`](.github/workflows/ci.yml)).

El recorrido completo —interfaz, lógica y persistencia— está cubierto por
[`test/test_corte_vertical.py`](test/test_corte_vertical.py), y la puerta de entrada por
[`test/test_autenticacion.py`](test/test_autenticacion.py). Las pruebas levantan el emisor de
desarrollo en un hilo y firman tokens de verdad: la criptografía no está simulada.

---

## Estructura del repositorio

```text
AS_202620_uniTeam/
├── app/                     API (FastAPI)
│   ├── api/                 Interfaz HTTP: rutas, esquemas y dependencias
│   ├── application/         Casos de uso, puertos y bus de eventos
│   ├── domain/              Entidades, flujo de estados y eventos de dominio
│   ├── events/              Consumidores de eventos (auditoría)
│   └── infrastructure/      Motor, tablas y repositorios (MySQL)
├── web/                     Aplicación Web (Next.js)
│   ├── app/                 Páginas y estilos
│   └── lib/                 Cliente de la API y sesión
├── test/                    Pruebas del backend
├── docs/                    arc42, ADR, C4, aspectos, escenarios y registro de IA
├── scripts/                 Emisor OIDC de desarrollo y verificación de enlaces
└── compose.yaml             Arranque completo con un comando
```

Los límites de estas carpetas se corresponden con los contenedores y paquetes de los diagramas
C4; la correspondencia concreta está en
[arc42 §5](docs/arc42/arc42-uniteam.md#5-vista-de-bloques-de-construcción).

---

## Equipo

| Integrante | Identidades en el historial de git |
|-----------|-----------------------------------|
| Julio César Emiliani Ramos | `super-gremlin` · `Julio Cesar Emiliani <jlemiliani@gmail.com>` |
| Ian Novoa Carrillo | `Ian Novoa` (`iansx`) |
| Juan José Bustamante | `JuanB` (`Paradox2700`) |
| Daniel Isaac Manjarrés | `Daniel Manjarres Herrera` |

Julio César Emiliani Ramos aparece con **dos identidades**, su cuenta de GitHub y su correo
personal, según desde dónde haya empujado cada commit. Son la misma persona.

**Sobre la coautoría de Claude.** Algunos commits llevan el pie `Co-Authored-By: Claude`. Los
redactó, revisó, probó y subió Julio César Emiliani Ramos, que es su autor y responsable; el
pie deja constancia de que hubo asistencia de IA, como exige la política del curso. El detalle
de qué se pidió, qué se aceptó y **qué se rechazó y por qué** está en [`docs/ia.md`](docs/ia.md).
