# Resultado del análisis de dependencias

Herramientas (workflow `.github/workflows/seguridad.yml`, también ejecutable manualmente con *Run workflow*):
- API (Python): `pip-audit`
- Web (Node): `npm audit --omit=dev`
- Actualizaciones automáticas: Dependabot (`.github/dependabot.yml`)

**Run de referencia:** <PEGAR_URL_DEL_RUN_DE_ACTIONS>  (fecha: <AAAA-MM-DD>, commit: <HASH>)

## Hallazgos y decisión

| Componente | Paquete | Versión | Severidad | Hallazgo | Decisión |
|------------|---------|---------|-----------|----------|----------|
| <api/web> | <paquete> | <ver> | <alta/media/baja> | <CVE o resumen> | <actualizado a X / no explotable porque… / aceptado, ver arc42 §11> |

Si el run no reporta vulnerabilidades, indicarlo aquí: «El run <URL> no reportó hallazgos en API ni Web».
