# ESC-01 — Línea base de latencia del tablero

Primera medición del escenario
[ESC-01](../escenarios-calidad.md#esc-01). Sirve de **línea base**: el número
contra el que se comparará cualquier cambio que afecte al rendimiento.

## Qué se midió

El escenario tal como está escrito: un proyecto con **200 tareas** y **30 usuarios
concurrentes** consultando el tablero, contrastado con su umbral —p95 ≤ 2 s, p99 ≤ 4 s y 0
errores—.

## Resultado

| Medida | Valor | Umbral | |
|--------|------:|-------:|---|
| Mediana | 650 ms | — | |
| **p95** | **762 ms** | 2000 ms | Cumple |
| **p99** | **1037 ms** | 4000 ms | Cumple |
| Máximo | 1246 ms | — | |
| Errores | 0 de 300 | 0 en 100 consecutivas | Cumple |

Rendimiento agregado: 300 solicitudes en 6,60 s, **45,4 solicitudes/s**.

**Fecha:** 2026-08-29 · **Commit:** el de la retirada de `X-Usuario`.

## Cómo reproducirlo

Requiere la API en marcha contra MySQL y el emisor de identidad disponible.

```bash
# 1. Levantar el sistema
docker compose up -d

# 2. Obtener un token
TOKEN=$(python scripts/token_dev.py ana@utb.edu.co)

# 3. Medir
python scripts/medir_esc01.py --url http://localhost:8000 --token "$TOKEN"
```

El script ([`scripts/medir_esc01.py`](../../../scripts/medir_esc01.py)) siembra las 200 tareas,
lanza los 30 usuarios concurrentes con 10 peticiones cada uno, calcula los percentiles y sale
con código 1 si no se cumple el umbral. Los parámetros son ajustables: `--tareas`,
`--usuarios`, `--peticiones`.

## Entorno de esta medición

Declararlo importa, porque **no es el entorno del escenario**:

| | Esta medición | Lo que dice ESC-01 |
|---|---|---|
| Infraestructura | Máquina de desarrollo | Infraestructura gratuita de despliegue (T3) |
| Base de datos | MariaDB 10.11, compatible con el protocolo MySQL | MySQL 8.4 |
| Servidor | Uvicorn, un solo proceso | Sin definir |
| Red | Local, sin latencia de red | Internet |
| Alcance | Solo la API | Extremo a extremo, incluida la interfaz |

**Qué significa esto.** El número mide **el código**, no el sistema desplegado. Los 762 ms de
p95 dejan un margen de 1,2 s sobre el umbral, y ese margen es el que tendrá que absorber la
latencia de red, el arranque en frío de la infraestructura gratuita y el renderizado del
tablero en el navegador. La medición de extremo a extremo tendrá que repetirse cuando exista
despliegue, previsto para el segundo corte.

Lo que sí queda establecido es el punto de partida: cualquier cambio que empeore estos números
es una regresión detectable.

## Observaciones

- La mediana (650 ms) y el p95 (762 ms) están cerca: la distribución es estrecha y no hay
  cola larga. No aparece contención evidente con 30 usuarios concurrentes.
- La consulta del tablero está paginada con tope de 200 y usa el índice de `proyecto_id`
  ([`tablas.py`](../../../app/infrastructure/tablas.py)). El filtro por responsable **no** tiene
  índice; no afecta a esta medición, que no filtra, pero es la siguiente palanca si el número
  empeora.
- Un solo proceso de Uvicorn atendió las 45 solicitudes/s sin errores. Escalar a varios
  trabajadores es la palanca obvia si hiciera falta, y no se ha necesitado.
