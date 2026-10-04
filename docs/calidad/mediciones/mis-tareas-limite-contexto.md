# Medición — «Mis tareas» sin cruzar el límite de contexto (A-12)

Escenarios asociados: [ESC-03](../escenarios-calidad.md#esc-03) (no se debilita) y
[ESC-01](../escenarios-calidad.md#esc-01) (el cambio no degrada el rendimiento). Decisión:
[ADR-013](../../adr/0013-tareas-no-lee-las-tablas-de-proyectos.md). Fecha: 2026-10-04.

## Resultado

| Medida | Antes | Después | Umbral | |
|--------|------:|--------:|-------:|---|
| Tablas de Proyectos que lee el repositorio de Tareas | **2** (`MiembroTabla`, `ProyectoTabla`) | **0** | 0 | Cumple |
| Pruebas de la suite | 145 en verde | **149 en verde** (+4 nuevas) | todas | Cumple |
| ESC-03: proyecto ajeno visible en «Mis tareas» | 0 | 0 (`test_mis_tareas_nunca_muestra_un_proyecto_ajeno`) | 0 | Cumple |
| ESC-01: mediana de `GET /mis-tareas` (200 tareas, 20 proyectos) | 8,8 – 9,2 ms | 10,0 – 10,3 ms | — | |
| ESC-01: p95 de `GET /mis-tareas` | 9,7 – 10,7 ms | 11,5 – 11,8 ms | ≤ 2000 ms | Cumple |

Cada columna agrupa **tres ejecuciones** de 300 peticiones. El cambio cuesta ≈ 1,2 ms de mediana.

## La prueba que falla ante el defecto

Las 4 pruebas de [`test/test_limites_contexto.py`](../../../test/test_limites_contexto.py) se ejecutaron
**antes** del cambio: 4 fallaron (la guardia estructural con `['MiembroTabla', 'ProyectoTabla']`; las otras
tres porque `asignadas_a` no admitía una lista de proyectos). Tras el cambio, 4 pasan.

## Salvedades

1. **Es SQLite, en proceso, secuencial.** No es MySQL, no hay red y no hay 30 usuarios concurrentes. Mide
   el código antes y después; **no sustituye** la medición de extremo a extremo de
   [ESC-01](esc-01-linea-base.md). El costo de la consulta adicional sobre MySQL no está medido.
2. **ESC-03 está cubierto por pruebas, no medido con tráfico.** Igual que en la tabla de
   [aspectos](../../aspectos.md#cómo-leer-la-columna-evidencia).
3. **El defecto era de diseño, no de seguridad:** la versión con `JOIN` tampoco filtraba mal. Por eso la prueba que lo detecta es estructural.

## Cómo reproducirlo

```bash
pytest -v test/test_limites_contexto.py test/test_vistas.py
python -m scripts.medir_mis_tareas            # 300 peticiones; --peticiones N
git stash && python -m scripts.medir_mis_tareas   # el «antes» (con el cambio guardado aparte)
```
