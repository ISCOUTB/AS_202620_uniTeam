# ESC-05 — Añadir el estado «En revisión»

Primera medición del escenario [ESC-05](../escenarios-calidad.md#esc-05). A diferencia de los
de rendimiento, este escenario no se mide con una prueba de carga sino **ejecutando el cambio
que describe** y contando lo que costó. Así lo prevé el propio escenario: «cuando el cambio se
ejecute realmente, se cronometra el esfuerzo y se cuentan los componentes tocados en el commit
correspondiente».

## Qué se hizo

El estímulo tal como está escrito: **agregar el estado «En revisión» al flujo de trabajo
existente**, entre «En progreso» y «Completada».

El cambio va en **un commit propio** («ESC-05: estado «En revisión»»), separado de la táctica
que lo prepara ([ADR-012](../../adr/0012-publicar-el-flujo-de-estados-desde-el-dominio.md),
commit anterior). Separarlos es lo que permite medir el estímulo sin mezclarlo con la
preparación. Para auditarlo: `git show --stat` sobre ese commit.

## Resultado

| Medida del escenario | Resultado | Umbral | |
|----------------------|-----------|--------|---|
| Componentes modificados | **1**: el dominio de la API (`app/domain/modelos.py`) | ≤ 2 | Cumple |
| Esfuerzo | 1 min 17 s de reloj, de 01:18:49 a 01:20:06 UTC del 2026-09-28, hasta la suite en verde. Ver la salvedad | ≤ 1 día-persona | Cumple |
| Cambios incompatibles en la API pública | **0**: no se retira ninguna transición; el enum de `estado` solo crece | 0 | Cumple |
| Suite de pruebas existente | **107 de 107 en verde** sin tocarlas; 112 con las 5 nuevas del estado | En verde | Cumple |

**ESC-05 se cumple en sus cuatro medidas.**

### Qué tocó el commit, archivo a archivo

| Archivo | Contenedor (C4 nivel 2) | Naturaleza |
|---------|------------------------|------------|
| `app/domain/modelos.py` | API · dominio | **Código.** Un valor en `EstadoTarea`, su etiqueta y sus transiciones: 10 líneas |
| `test/test_flujo_estados.py` | — | Pruebas del estado nuevo |
| `docs/api/openapi.yaml`, `docs/api/contrato.md` | — | Contrato: el enum y el diagrama de estados |
| `docs/…` (esta ficha, escenarios, aspectos, registro de IA) | — | Documentación |

**No se tocaron** la Aplicación Web, la base de datos —`estado` es `VARCHAR(20)` y
`en_revision` cabe, así que no hay migración— ni la infraestructura. La cuarta columna del
tablero aparece sola, porque la Aplicación Web dibuja las columnas a partir de
`GET /flujo-estados`.

### Comprobación en navegador

El recorrido automático de 17 pasos, en Chromium contra la aplicación completa, incluye uno
nuevo: las columnas del tablero son `Pendiente | En progreso | En revisión | Completada`, y una
tarea pasa a «En revisión» con el botón que la tarjeta genera a partir de las transiciones.
Pasó sin errores de consola y **sin ningún cambio en `web/`**.

## Salvedades

1. **El esfuerzo no es el de un día-persona del equipo.** El cambio lo ejecutó un asistente de
   IA con el diseño ya preparado, y el minuto y pico mide eso. La medida que sí es transferible
   es la **estructural**: un componente, diez líneas, cero cambios incompatibles. Un integrante
   del equipo que repita el cambio sobre el mismo diseño debería medir su propio tiempo, y ese
   es el dato que conviene citar en la sustentación.
2. **El resultado depende de la táctica del commit anterior.** Sin el
   [ADR-012](../../adr/0012-publicar-el-flujo-de-estados-desde-el-dominio.md), el mismo cambio
   habría tocado **2 contenedores y al menos 5 archivos**: la guardia
   `test_la_aplicacion_web_no_escribe_estados_a_mano` encontraba 14 apariciones de estados
   escritos a mano en la Aplicación Web. Eso seguía cumpliendo el umbral de ≤ 2 componentes,
   pero justo en el límite y con dos copias del flujo que podían divergir en silencio.
3. **Compatibilidad hacia atrás, no hacia delante.** Un cliente que valide `estado` contra una
   lista cerrada de tres valores recibiría un valor que no conoce. La Aplicación Web no tiene ese
   problema, y el contrato lo documenta: los estados válidos son los que publica
   `/flujo-estados`.

## Cómo reproducirlo

```bash
git show --stat <commit «ESC-05: estado En revisión»>   # qué archivos tocó
pytest -v test/test_flujo_estados.py                     # el estado nuevo y la guardia
curl -s https://uniteam-api.onrender.com/flujo-estados   # el flujo publicado
```
