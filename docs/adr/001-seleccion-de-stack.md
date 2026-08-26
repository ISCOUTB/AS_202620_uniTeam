# ADR-001 — Selección del stack de desarrollo

- **Estado:** Propuesta — pendiente de decisión del equipo
- **Fecha:** 2026-08-16
- **Decide:** el equipo de desarrollo (I-04)

## Contexto

La restricción [T1](../arc42/arc42-uniteam.md#21-restricciones-técnicas) acota el stack a un
conjunto cerrado de opciones: **NestJS o FastAPI** en el backend y **Flutter o Next.js** en el
frontend. Esa restricción no es una decisión —el equipo se limita a lo que conoce o puede
aprender dentro del semestre—, pero elegir *dentro* de ese conjunto sí lo es, y por eso se
registra aquí.

La restricción [T2](../arc42/arc42-uniteam.md#21-restricciones-técnicas) ya descartó la
aplicación móvil nativa: el prototipo se entrega para **navegador web y/o escritorio**. Eso
condiciona la elección del frontend, porque las dos opciones no cubren el mismo terreno.

## Opciones

**Backend**

| Opción | A favor | En contra |
|--------|---------|----------|
| NestJS (TypeScript) | Mismo lenguaje que Next.js, si se elige ese frontend: un solo lenguaje en todo el proyecto reduce el costo de cambio de contexto con dedicación parcial (O1). Estructura modular explícita, favorable a [ESC-05](../calidad/escenarios-calidad.md#esc-05). | Más ceremonia inicial. |
| FastAPI (Python) | Rápido de escribir y de arrancar. Mejor punto de partida si más adelante se incorpora analítica o funcionalidad de IA. | Introduce un segundo lenguaje si el frontend es Next.js. |

**Frontend**

| Opción | A favor | En contra |
|--------|---------|----------|
| Next.js | Web nativo, ecosistema amplio, despliegue sencillo en infraestructura gratuita (T3). Comparte lenguaje con NestJS. | No cubre escritorio sin empaquetado adicional. |
| Flutter | Un solo código para web y escritorio. | Tercer lenguaje del proyecto (Dart). Aplicaciones web más pesadas, lo que presiona la latencia de [ESC-01](../calidad/escenarios-calidad.md#esc-01). |

## Criterios de decisión

Se decidirá según, en este orden:

1. Cobertura de los canales exigidos por T2 (web y/o escritorio).
2. Impacto en [ESC-01](../calidad/escenarios-calidad.md#esc-01) — latencia sobre
   infraestructura limitada.
3. Impacto en [ESC-05](../calidad/escenarios-calidad.md#esc-05) — costo de extender el flujo
   de estados.
4. Número de lenguajes que el equipo debe sostener en paralelo (O1).

## Decisión

*Pendiente.* Se completa esta sección cuando el equipo tome la decisión, junto con sus
consecuencias y las alternativas descartadas. Hasta entonces, el diseño de la arquitectura se
mantiene independiente del framework.
