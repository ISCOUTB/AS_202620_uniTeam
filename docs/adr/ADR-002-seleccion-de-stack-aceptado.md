# ADR-002 — Selección del stack de desarrollo

- **Estado:** Aceptada
- **Fecha:** 2026-08-22
- **Decide:** el equipo de desarrollo (I-04)

## Contexto

La restricción [T1](../arc42/arc42-uniteam.md#21-restricciones-técnicas) acota el stack
a un conjunto cerrado de opciones: **NestJS o FastAPI** para el backend y **Flutter o
Next.js** para el frontend. La restricción limita las alternativas disponibles, pero no
determina por sí sola cuál combinación se utilizará.

La restricción [T2](../arc42/arc42-uniteam.md#21-restricciones-técnicas) establece que
el prototipo se entregará para **navegador web y/o escritorio**, descartando la necesidad
de una aplicación móvil nativa. Por este motivo, el frontend debe priorizar la experiencia
web y mantener un costo de desarrollo compatible con las capacidades del equipo.

Además, los escenarios de calidad [ESC-01](../calidad/escenarios-calidad.md#esc-01) y
[ESC-05](../calidad/escenarios-calidad.md#esc-05) establecen como aspectos relevantes la
latencia sobre infraestructura limitada y el costo de extender el flujo de estados.

A partir de estas restricciones y criterios, el equipo evaluó las alternativas disponibles
y decidió utilizar **FastAPI como backend y Next.js como frontend**.

## Opciones consideradas

### Backend

| Opción | A favor | En contra |
|--------|---------|-----------|
| **FastAPI (Python)** | Rápido de desarrollar y de arrancar. Buen rendimiento para una API ligera. Facilita una futura incorporación de analítica, procesamiento de datos o funcionalidad de IA. | Requiere mantener Python además de JavaScript/TypeScript utilizado en el frontend. |
| NestJS (TypeScript) | Comparte lenguaje con Next.js. Proporciona una estructura modular explícita y facilita mantener un único lenguaje en el proyecto. | Mayor ceremonia inicial y menor conveniencia si posteriormente se incorporan componentes de analítica, procesamiento de datos o IA basados en Python. |

### Frontend

| Opción | A favor | En contra |
|--------|---------|-----------|
| **Next.js** | Orientado a aplicaciones web. Ecosistema amplio basado en React y despliegue sencillo en infraestructura gratuita [T3](../arc42/arc42-uniteam.md#21-restricciones-técnicas). Permite desarrollar el prototipo directamente para navegador. | No proporciona soporte de escritorio nativo sin utilizar mecanismos de empaquetado adicionales. |
| Flutter | Permite reutilizar código para web y escritorio. | Introduce Dart como tercer lenguaje si se combina con FastAPI. Las aplicaciones web pueden ser más pesadas, lo que puede afectar la latencia definida en [ESC-01](../calidad/escenarios-calidad.md#esc-01). |

## Criterios de decisión

La decisión se tomó considerando, en este orden:

1. Cobertura de los canales exigidos por T2, priorizando el navegador web.
2. Impacto en [ESC-01](../calidad/escenarios-calidad.md#esc-01) — latencia sobre
   infraestructura limitada.
3. Impacto en [ESC-05](../calidad/escenarios-calidad.md#esc-05) — costo de extender el
   flujo de estados.
4. Facilidad para incorporar posteriormente capacidades de analítica, procesamiento de
   datos o IA.
5. Complejidad y costo de aprendizaje y mantenimiento del stack por parte del equipo.

## Decisión

Se selecciona **FastAPI como framework de backend y Next.js como framework de frontend**.

El backend se implementará utilizando **Python y FastAPI**, exponiendo las APIs necesarias
para que el frontend pueda consumir los servicios de la aplicación.

El frontend se implementará utilizando **Next.js**, priorizando la entrega del prototipo
para navegador web de acuerdo con la restricción T2.

La combinación resultante será:

```text
┌─────────────────────┐
│      Next.js        │
│   Frontend Web      │
└──────────┬──────────┘
           │ HTTP/HTTPS
           ▼
┌─────────────────────┐
│      FastAPI        │
│    Backend / API    │
└─────────────────────┘