# Estimación del costo mensual

El costo sale del **volumen del escenario**, no del catálogo del proveedor: primero se fija
cuánto se usa UniTeam, luego cuánto consume eso de cada recurso que se factura, y por último en
qué punto se agota cada capa gratuita.

**Resultado: 0 USD/mes al volumen supuesto.** El primer límite que se rompe no es de volumen
sino de calidad: la API de la capa gratuita se duerme y su arranque en frío incumple ESC-01 en la
primera visita tras 15 minutos de inactividad. Evitarlo cuesta **7 USD/mes**.

Precios y límites consultados el 2026-09-27; las fuentes están en cada ADR.

---

## 1. Supuestos de volumen

| # | Supuesto | Valor | De dónde sale |
|---|----------|-------|---------------|
| S1 | Usuarios activos al mes | **50** (10 equipos de 5) | Uso piloto en un curso durante el semestre |
| S2 | Concurrencia máxima | **30 usuarios** | [ESC-01](../calidad/escenarios-calidad.md#esc-01) |
| S3 | Tamaño del proyecto mayor | **200 tareas** | ESC-01 |
| S4 | Consultas del tablero | 10 por usuario y día lectivo, 20 días al mes → **10 000 al mes** | Supuesto del equipo |
| S5 | Peticiones a la API por consulta del tablero | **3** (detalle, tareas y progreso) | [`web/app/proyecto/tablero.tsx`](../../web/app/proyecto/tablero.tsx) |
| S6 | Escrituras | 1 por cada 2 consultas → **5 000 al mes** | Supuesto del equipo |
| S7 | Sesiones (carga completa del sitio) | 2 por usuario y día lectivo → **2 000 al mes** | Supuesto del equipo |
| S8 | Horas con uso real | 8 h al día, 20 días al mes | Horario lectivo |

**Volumen resultante: unas 35 000 peticiones a la API al mes.**

## 2. Tamaños medidos

Medidos sobre el código de este commit, no estimados:

| Qué | Tamaño | Cómo |
|-----|--------|------|
| Respuesta del tablero con 200 tareas | 65,0 KB; **6,6 KB comprimida** | `GET /proyectos/{id}/tareas?limite=200`, la API comprime con gzip |
| Detalle y progreso de un proyecto | 0,3 KB | Ídem |
| Sitio completo (HTML, JS y CSS) | 760 KB; **221 KB comprimido** | `web/out/` tras `npm run build` |
| Una línea de log | ~280 bytes | Salida de `app/observabilidad.py` |

## 3. Consumo por pieza

| Pieza | Recurso facturable | Consumo al volumen supuesto | Capa gratuita | Uso | Costo |
|-------|-------------------|-----------------------------|---------------|-----|-------|
| Aplicación Web | Ancho de banda de salida | 2 000 sesiones × 221 KB ≈ **0,44 GB** | 100 GB/mes, compartidos | 0,4 % | 0 USD |
| API | Ancho de banda de salida | 10 000 × (6,6 + 0,3 + 1,5 de cabeceras) KB + escrituras ≈ **0,09 GB** | (mismos 100 GB) | 0,1 % | 0 USD |
| API | Horas de instancia | Despierta en horario de uso más 15 min de cola: ≈ **180–250 h** | 750 h/mes | ≤ 33 % | 0 USD |
| API + sitio | Minutos de compilación | ~40 despliegues × ~5 min ≈ **200 min** | 500 min/mes | 40 % | 0 USD |
| Base de datos | Almacenamiento | 5 000 escrituras + auditoría ≈ **4 MB al mes** con índices | 1 GB | 0,4 % al mes | 0 USD |
| Proveedor de identidad | Usuarios activos | **50** | 25 000 | 0,2 % | 0 USD |
| CI | Minutos de GitHub Actions | ~6 min por push | Ilimitados en repositorio público | — | 0 USD |
| Análisis estático | SonarCloud | 1 proyecto | Gratis para proyectos públicos | — | 0 USD |
| **Total** | | | | | **0 USD/mes** |

Los minutos por compilación son una estimación; el valor real se lee en *Render → Events* tras
los primeros despliegues y debe sustituir al de esta tabla.

## 4. Puntos de ruptura

Dónde deja de ser gratis cada pieza, ordenados por lo pronto que se alcanzan:

| # | Qué se rompe | Cuándo | Qué cuesta evitarlo |
|---|-------------|--------|---------------------|
| R1 | **ESC-01 en la primera visita.** La API se duerme tras 15 min sin tráfico y tarda ~1 min en despertar | **Ya.** Cualquier uso intermitente lo provoca | Render Starter: **7 USD/mes** |
| R2 | **ESC-04: disponibilidad del 99 %.** Aiven Free no tiene SLA y se apaga por inactividad | Ya, si se exige el 99 % mensual | Aiven Developer: **5 USD/mes** (sigue sin alta disponibilidad) |
| R3 | Horas de instancia | Al añadir **un segundo servicio siempre activo**: 2 × 744 h > 750 h | 7 USD/mes por servicio |
| R4 | Minutos de compilación | ~100 despliegues al mes | Plan de pago de Render |
| R5 | Ancho de banda | ≈ **9 400 usuarios activos** (10,6 MB por usuario y mes) | 15 USD por cada 100 GB adicionales |
| R6 | Almacenamiento de la base de datos | ≈ **20 años** al ritmo supuesto | — |
| R7 | Usuarios de Auth0 | **25 000** usuarios activos al mes | Plan de pago por tramos |

**Lectura.** Al volumen de un curso, ninguna capa gratuita se agota por volumen: sobran dos o
tres órdenes de magnitud. Lo que no da la capa gratuita es **calidad de servicio** —arranque en
frío y disponibilidad—, y eso es exactamente lo que miden ESC-01 y ESC-04. La decisión real no
es «¿cabe en lo gratis?» sino «¿cuánto vale que la primera consulta del día tarde 2 s y no 60?».

## 5. Frente a las alternativas

| Configuración | Costo mensual | ESC-01 en la 1.ª visita | ESC-04 (99 %) | Tarjeta |
|---------------|---------------|-------------------------|---------------|---------|
| **Elegida:** Render Free + Aiven Free + Auth0 Free | **0 USD** | No | No | Por verificar en Render |
| Mínima que cumple ESC-01: API en Render Starter | **7 USD** | Sí | No | Sí |
| La anterior + base de datos en Aiven Developer | **12 USD** | Sí | Mejor, sin garantía | Sí |
| Servidor del laboratorio con `docker compose up` | **0 USD** | Sí, no se duerme | Depende del laboratorio | No |
| API como función (FaaS) | ~0 USD a este volumen | Descartada: estado en memoria y conexiones a la BD ([ADR-008](../adr/0008-desplegar-la-api-como-contenedor-en-render.md)) | — | Sí (AWS) |

El servidor del laboratorio es la alternativa que cumple ESC-01 sin costo, pero **solo si es
accesible desde fuera de la universidad**, que es lo que exige la evaluación. Si lo es, es la
mejor opción para el API; si no, Render.

## 6. Cuándo revisar esta estimación

- Al conocer los minutos reales de compilación (sección 3).
- Si el uso real supera 5 veces el supuesto S1 o S4.
- Si ESC-01 pasa a exigirse también en la primera visita: entonces R1 deja de ser una
  consecuencia aceptada y se paga Starter.
