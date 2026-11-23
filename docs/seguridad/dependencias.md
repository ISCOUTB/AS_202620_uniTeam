# Resultado del análisis de dependencias

Herramientas (workflow `.github/workflows/seguridad.yml`, también ejecutable manualmente con *Run workflow*):

- API (Python): `pip-audit` sobre `requirements.lock.txt` (el cierre con huella que instala la CI y el Dockerfile).
- Web (Node): `npm audit --omit=dev --audit-level=high`.
- Actualizaciones automáticas: Dependabot (`.github/dependabot.yml`).

**Bloqueante:** ambos pasos usan `set -eo pipefail`, así que `pip-audit` y `npm audit` fallan el job cuando reportan hallazgos; el informe se conserva como artefacto con `tee` pero ya no oculta el código de salida.

**Run de referencia:** `PENDIENTE_RUN` (fecha: `<AAAA-MM-DD>`, commit: `<HASH>`). Reemplazar este marcador con la URL del run de `seguridad-dependencias` tras la próxima ejecución en `master`.

## Hallazgos y decisión

El informe del run `PENDIENTE_RUN` se revisará al publicarse; hasta entonces no se afirma ausencia de hallazgos.

| Componente | Paquete | Versión | Severidad | Hallazgo | Decisión |
|------------|---------|---------|-----------|----------|----------|
| `<api/web>` | `<paquete>` | `<ver>` | `<alta/media/baja>` | `<CVE o resumen>` | `<actualizado a X / no explotable porque… / aceptado, ver arc42 §11>` |

## Límites

- Un run verde del scanner **no equivale a ausencia de vulnerabilidades**: solo informa lo que las reglas de `pip-audit` y `npm audit` detectan en la fecha de ejecución.
- La revisión y decisión de cada hallazgo es un paso humano; ningún hallazgo se cierra en silencio (decisión D-009).
- El análisis de SonarCloud es *Automatic Analysis*: corre al hacer *push* sin job de CI, ignora `sonar-project.properties` y **no soporta cobertura** (`sonar.python.coverage.reportPaths` no se aplica). Su panel público está en [`docs/calidad/analisis-estatico.md`](../calidad/analisis-estatico.md) y el Quality Gate consultado el 2026-11-22 está en `OK`.
