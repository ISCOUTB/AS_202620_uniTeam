# 0004 — Usar MySQL como base de datos

- **Estado:** Aceptada
- **Fecha:** 2026-08-29
- **Decide:** el equipo de desarrollo (I-04)

## Contexto

El corte vertical de la semana 4 necesita persistencia real. Hasta ahora el motor de base de
datos no estaba decidido: [arc42 §3.2](../arc42/arc42-uniteam.md#32-contexto-técnico) hablaba
de «almacenamiento persistente» sin comprometerse, y el C4 de nivel 2 llegó a dibujar un motor
concreto **antes** de que existiera esta decisión, que es justo lo que el contrato del curso
pide evitar.

Las restricciones que acotan la elección son [T3](../arc42/arc42-uniteam.md#21-restricciones-técnicas)
—infraestructura gratuita— y [O3](../arc42/arc42-uniteam.md#22-restricciones-organizativas)
—sin presupuesto—, además de [O1](../arc42/arc42-uniteam.md#22-restricciones-organizativas):
cuatro estudiantes con dedicación parcial.

## Opciones evaluadas

| Opción | A favor | En contra |
|--------|---------|----------|
| **MySQL** | El equipo ya lo conoce del curso de bases de datos, lo que reduce el costo de aprendizaje bajo O1. Licencia libre (O3), imagen oficial de Docker para el arranque con un comando, y niveles gratuitos en los proveedores que contempla T3. | Menos rico que PostgreSQL en tipos y en funciones de ventana, que este prototipo no necesita. |
| PostgreSQL | Más funcionalidad y mejor comportamiento en consultas complejas. | Ninguna ventaja aprovechable en el alcance actual, y el equipo tiene menos práctica. |
| SQLite | Cero infraestructura. | Un solo escritor a la vez y sin servidor: no sostiene los 30 usuarios concurrentes de [ESC-01](../calidad/escenarios-calidad.md#esc-01). |

## Decisión

Se usa **MySQL 8.4** como motor de la base de datos en ejecución y en integración continua.

SQLite se conserva **solo** como valor por defecto de `DATABASE_URL` para que `pytest` funcione
en un clon recién hecho, sin levantar servicios. No es un entorno soportado: la persistencia que
se califica y se despliega es MySQL, y el pipeline ejecuta las pruebas contra MySQL.

El acceso se hace mediante SQLAlchemy, de modo que el motor queda detrás de los repositorios de
`app/infrastructure/` y no se filtra a los casos de uso.

## Consecuencias

**Positivas.** Persistencia con concurrencia real para ESC-01; arranque reproducible con
`docker compose up`; conocimiento previo del equipo aprovechado; sin costo.

**Negativas.** Añade un servicio que debe estar disponible, lo que resta margen a
[ESC-04](../calidad/escenarios-calidad.md#esc-04). Obliga a mantener el esquema compatible con
dos motores mientras SQLite siga siendo el valor por defecto de las pruebas locales: ya apareció
una diferencia real de aislamiento entre ambos, documentada en `test/test_corte_vertical.py`.

## Trazabilidad

| Eslabón | Dónde |
|---------|-------|
| Aspecto y requisito | [A-01 a A-06](../aspectos.md), RF-01 a RF-06 |
| Elemento C4 | Contenedor «Base de datos» en [C4 nivel 2](../c4/nivel2-contenedores.md) |
| Código | `app/infrastructure/db.py`, `app/infrastructure/tablas.py`, `app/infrastructure/repositorios.py` |
| Pruebas | `test/test_corte_vertical.py`, ejecutadas contra MySQL en `.github/workflows/ci.yml` |
| Escenario de calidad | [ESC-01](../calidad/escenarios-calidad.md#esc-01), [ESC-03](../calidad/escenarios-calidad.md#esc-03) |
