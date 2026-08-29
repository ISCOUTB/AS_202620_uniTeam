# UniTeam — Instrucciones del repositorio

Proyecto académico de arquitectura de software (semestre 2026-20). UniTeam centraliza la
gestión de tareas de equipos universitarios. Ver [`docs/ficha.md`](docs/ficha.md).

## Regla obligatoria: registro en `docs/ia.md`

**Toda** intervención asistida por IA generativa en este repositorio debe quedar registrada en
[`docs/ia.md`](docs/ia.md) antes de hacer commit. En concreto:

1. **Bitácora de uso de IA** — una fila por sesión de trabajo: qué se pidió, qué produjo la
   herramienta y qué revisó o cambió el equipo.
2. **Decisiones tomadas por el equipo** — las decisiones de alcance, arquitectura o tecnología
   se registran como decisiones **del equipo**, nunca como decisiones de la IA. La IA propone;
   el equipo decide. Si una propuesta generada por IA se adopta, se registra como decisión del
   equipo con la fecha en que la aprobó.
3. **Bitácora de cambios en la aplicación** — todo cambio funcional del prototipo, indicando
   si hubo asistencia de IA.

El propósito es dejar clara la autoría del trabajo: la IA no hace el trabajo por el equipo.

## Convenciones de documentación

- Documentación en español, en Markdown, dentro de `docs/`.
- Diagramas como código, en Mermaid, para que puedan revisarse en un *diff*. No se usan
  herramientas de diagramación propietarias.
- La estructura arc42 vive en [`docs/arc42/arc42-uniteam.md`](docs/arc42/arc42-uniteam.md).
  La plantilla original en inglés no se modifica.
- Las decisiones de arquitectura se registran como ADR en `docs/adr/`, numeradas
  `ADR-00N-titulo.md`.
- Los escenarios de calidad tienen anclas estables (`#esc-01` … `#esc-05`); los enlaces desde
  `docs/aspectos.md` y desde arc42 dependen de ellas, así que no se renumeran.
- Cada aspecto declarado en `docs/aspectos.md` debe enlazar a su escenario de calidad.

## Restricciones vigentes

- Stack acotado a **NestJS o FastAPI** (backend) y **Flutter o Next.js** (frontend). La
  elección concreta está pendiente en [0001-acotar-el-stack-a-cuatro-opciones.md).
- **No** se desarrolla aplicación móvil nativa: el objetivo es navegador web y/o escritorio.
- Sin presupuesto: solo herramientas gratuitas o de código abierto.
