# Estimación del costo mensual

**Estado vigente (2026-11-22):** UniTeam se despliega en Dokploy sobre un servidor institucional cedido por el docente ([ADR-0021](../adr/0021-desplegar-en-dokploy-en-un-servidor-institucional.md)). El costo para el equipo es **0 USD al mes**; no se necesita tarjeta. La contrapartida es que el servidor lo administra un tercero: no hay SLA, ni control de parches, ni garantía de disponibilidad ([riesgo R-08](../arc42/arc42-uniteam.md#11-riesgos-y-deuda-técnica)).

A continuación, el modelo de costo histórico (Render + Aiven + Auth0) se conserva como evidencia de alternativas evaluadas; el despliegue actual es Dokploy.

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

## 3. Consumo por pieza (despliegue actual, Dokploy)

| Pieza | Recurso | Consumo al volumen supuesto | Costo para el equipo |
|-------|---------|-----------------------------|----------------------|
| Aplicación Web | Ancho de banda de salida | 2 000 sesiones × 221 KB ≈ 0,44 GB | 0 USD |
| API | Ancho de banda de salida | ~0,1 GB | 0 USD |
| API | Horas de instancia | 24 h/día (sin hibernación) | 0 USD (servidor institucional) |
| Base de datos | Almacenamiento | 5 000 escrituras + auditoría ≈ 4 MB al mes | 0 USD |
| Proveedor de identidad | Usuarios activos | 50 | 0 USD |
| CI | Minutos de GitHub Actions | ~6 min por push | 0 USD (repositorio público) |
| Análisis estático | SonarCloud | 1 proyecto | Gratis para proyectos públicos |
| **Total** | | | **0 USD/mes** |

## 4. Puntos de ruptura (despliegue actual)

| # | Qué se rompe | Cuándo | Qué cuesta evitarlo |
|---|-------------|--------|---------------------|
| R1 | Disponibilidad del servidor institucional | Si el administrador lo apaga o reinicia | Depende del tercero (riesgo R-08); no hay plan de pago del equipo |
| R2 | ESC-04: 99 % mensual | El servidor institucional no garantiza SLA | No hay alternativa de pago del equipo |
| R3 | Almacenamiento de la base de datos | ≈ 20 años al ritmo supuesto | — |
| R4 | Usuarios del proveedor de identidad | 25 000 activos al mes | Plan de pago por tramos |

**Lectura.** Al volumen de un curso, ninguna capa se agota por volumen: sobran dos o tres órdenes de magnitud. Lo que no da el servidor institucional es **calidad de servicio** —disponibilidad sin SLA—, y eso es exactamente lo que miden ESC-01 y ESC-04. La decisión real no es «¿cabe en lo gratis?» sino «¿cuánto vale que el sistema esté disponible todo el mes?». Esa respuesta la da el servidor institucional, no el equipo.

## 5. Frente a las alternativas (historizado)

Esta tabla compara las alternativas evaluadas antes de elegir Dokploy; se conserva como evidencia de la decisión (ADR-0021).

| Configuración | Costo mensual | ESC-01 en la 1.ª visita | ESC-04 (99 %) | Tarjeta |
|---------------|---------------|-------------------------|---------------|---------|
| **Elegida:** Dokploy + servidor institucional | **0 USD** | Sí (no hay hibernación) | Depende del tercero | No |
| Render Free + Aiven Free + Auth0 Free; sondeo horario previsto | 0 USD | Solo si el sondeo está activo; se observó arranque en frío | No | No |
| Mínima que cumple ESC-01: API en Render Starter | 7 USD | Sí | No | Sí |
| Servidor del laboratorio con `docker compose up` | 0 USD | Sí | Depende del laboratorio | No |
| API como función (FaaS) | ~0 USD a este volumen | Descartada: estado en memoria y conexiones a la BD | — | Sí (AWS) |

## 6. Cuándo revisar esta estimación

- Si el uso real supera 5 veces el supuesto S1 o S4.
- Si el servidor institucional deja de estar disponible o exige pago: entonces se evalúa la alternativa del laboratorio o Render Free.
