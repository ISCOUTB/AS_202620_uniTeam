# Documento guía · entrega del proyecto final (S16)

**UniTeam — Gestión colaborativa de tareas para equipos universitarios**
Arquitecturas de Software, semestre 2026-20 · Universidad Tecnológica de Bolívar

---

## 1. Qué se entrega

| Elemento | Valor |
|----------|-------|
| Repositorio | `github.com/ISCOUTB/AS_202620_uniTeam`, rama `master` |
| Commit calificado | `469517a5` (último antes del cierre de S16; HEAD del entregable) |
| URL del sistema | <https://uniteam-web.iscoutb.dev> |
| URL de la API | <https://uniteam-api.iscoutb.dev> |
| Health check | <https://uniteam-api.iscoutb.dev/health> |
| Métrica ESC-01 | <https://uniteam-api.iscoutb.dev/metricas/esc-01> |
| Pipeline CI | <https://github.com/ISCOUTB/AS_202620_uniTeam/actions/workflows/ci.yml> |
| SonarCloud | <https://sonarcloud.io/summary/overall?id=ISCOUTB_AS_202620_uniTeam> |

El sistema está desplegado en **Dokploy sobre un servidor institucional cedido por el docente** (ADR-0021): cuatro servicios (`web`, `api`, `migrate`, `db` con MySQL 8.4), dominio público `iscoutb.dev` con Traefik/TLS, y 0 USD de costo para el equipo. La versión calificada es el último commit de `master` anterior o igual al cierre, sin etiquetas.

---

## 2. Respuesta al desafío final asignado

**Desafío:** delegar la autenticación en un proveedor OpenID Connect, retirando la cabecera `X-Usuario` que cualquiera podía falsificar.

- **Antes (línea base):** `app/api/dependencias.py` tomaba el usuario de `Header(..., alias="X-Usuario")`; `app/main.py` permitía la cabecera. Cualquier correo suplantaba a cualquier miembro. **100 % de identidades suplantables.**
- **Después (commit `984922e`):** la API valida el token en cada petición contra el JWKS del emisor (firma, `iss`, `aud`, `exp`); la identidad sale del token, no del cliente. Se eliminó `X-Usuario` del código y de las pruebas.
- **Evidencia reproducible:** 11 pruebas negativas en `test/test_autenticacion.py` (todas en 401), incluidas la nueva `test_la_cabecera_x_usuario_sola_no_autentica` que envía solo `X-Usuario` y exige `401`. Suite: **160 pruebas, 160 pasadas**. Comprobación en despliegue real: 7 identidades con `X-Usuario` → `401` (2026-11-22).

La medición completa está en `docs/calidad/mediciones/desafio-autenticacion.md`, con la cifra de antes (100 %) y después (0 %), que es lo que separa un resultado competente de uno sobresaliente.

---

## 3. Alcance entregado frente al comprometido

Lo prometido en el segundo corte (S10) se entregó: corte vertical con las tres capas, arranque con un solo comando, CI en verde, tabla de aspectos con enlaces navegables, medición de ESC-01 con línea base, modelo de amenazas STRIDE, autenticación OIDC y notificaciones WebSocket.

Lo **no hecho se declara explícitamente** (un alcance recortado y declarado puntúa mejor que uno recortado en silencio):

- **ESC-02 (usabilidad):** sin medir; exige una prueba con 10 participantes ajenos al equipo.
- **ESC-04 (disponibilidad):** sin prueba de resiliencia ante caída; la base de datos gratuita no tiene SLA (riesgo R-05).
- **T4/T5 (CSP, escapado, cookie httpOnly):** parciales; falta implementar.
- **T8 (límite de peticiones):** ADR-020 propuesto, no implementado.
- **T9 (CORS lista blanca):** pendiente de verificar en `app/main.py`.
- **T11 (no filtrar datos en logs):** pendiente de verificar.
- **Medición de WebSocket y de la nueva interfaz sobre el despliegue real:** pendiente (S15).
- **Invalidación de JWKS y tabla de garantías por operación:** pendiente (S12).
- **Auditoría de dependencias bloqueante:** el workflow ya falla si hay hallazgos (`pipefail`); el informe con hallazgos reales se rellena tras el próximo run (`PENDIENTE_RUN` en `docs/seguridad/dependencias.md`).

Todas las omisiones están declaradas en `docs/arc42/arc42-uniteam.md §11.1` y en `docs/seguridad/amenazas.md` con su estado real.

---

## 4. Decisiones y evolución

Los ADR permiten reconstruir por qué el sistema es como es. Decisiones clave:

- **Confirmada con evidencia:** ADR-0005/0010 (OIDC) — es el desafío final, medido con la línea base de antes/después.
- **Reemplazada con evidencia:** ADR-008/0009 (Render + Aiven) → ADR-0021 (Dokploy, servidor institucional), porque el entorno real cambió.
- **Mantenida:** ADR-0003 (eventos en proceso, sin broker), ADR-0004 (MySQL), ADR-0007 (sitio estático).

Lista completa y estados en `docs/arc42/arc42-uniteam.md §9` y en `docs/adr/`.

---

## 5. Calidad, resiliencia y seguridad verificadas

- **ESC-01 (rendimiento):** p95 762 ms frente al umbral de 2 s, reproducible con `scripts/medir_esc01.py` (línea base local; falta repetir en el despliegue real).
- **ESC-03 (seguridad):** 100 % de accesos denegados con 403 y auditoría, cubierto por pruebas automatizadas en cada push.
- **ESC-05 (modificabilidad):** añadir «En revisión» tocó 1 componente, suite en verde.
- **Modos de fallo:** derivas documentadas (consumidores y sesión compartida, WebSocket sin entrega durable, servidor sin SLA) con mitigaciones o aceptación explícita en arc42 §11.
- **Seguridad:** modelo de amenazas STRIDE (T1-T11) con dueño y estado; análisis de dependencias en CI con `pipefail`; sin credenciales en el repositorio (barrido sobre 69 commits, 0 coincidencias).

---

## 6. Demo y sustentación

La demostración se hace en vivo sobre <https://uniteam-web.iscoutb.dev>:
1. Iniciar sesión con cuenta institucional o Google.
2. Crear un proyecto, agregar un miembro y crear tres tareas.
3. Mover una tarea de estado (arrastrar y soltar) y verificar que el WebSocket notifica el cambio sin recargar.
4. Abrir una segunda sesión como usuario ajeno y verificar que recibe 403 al intentar entrar al proyecto.

**Preguntas contrafactuales preparadas para el jurado:**
1. ¿Qué pasa si el servidor institucional se reinicia en medio de una entrega? → El health check devuelve 503, Dokploy no enruta tráfico y se declara el riesgo R-08 (sin SLA).
2. ¿Qué pasa si se multiplica la carga por 10? → El p95 local da margen de 1,2 s sobre el umbral; se vigila con `/metricas/esc-01` y se reducen consultas si se acerca a 2 s.
3. ¿Qué pasa si cambia el proveedor de identidad? → Es solo configuración (`OIDC_EMISOR`, `OIDC_AUDIENCIA`), no código, por ADR-0005.

El resto de la documentación (arc42 secciones 1-12 con glosario, C4 niveles 1-3, contratos, tabla de aspectos, registro de IA) está en `docs/`.
