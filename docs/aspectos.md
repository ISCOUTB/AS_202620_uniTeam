# Aspectos Declarados

## Gestión colaborativa de tareas

UniTeam implementará un sistema de gestión colaborativa de tareas para facilitar la
organización del trabajo dentro de equipos universitarios.

El aspecto se evidencia en el prototipo mediante la creación, asignación, actualización y
consulta de tareas dentro de un proyecto.

## Tabla de trazabilidad

Una fila por aspecto, con la cadena completa **aspecto → requisito → C4 → ADR → código →
pruebas → evidencia de calidad**. Cada celda enlaza a su destino.

| ID | Aspecto | Requisito | C4 | ADR | Código | Pruebas | Evidencia |
|----|---------|-----------|----|-----|--------|---------|-----------|
| A-01 | Crear tareas | [RF-01](arc42/arc42-uniteam.md#11-resumen-de-requisitos) | [Aplicación Web](c4/nivel2-contenedores.md) → [API](c4/nivel2-contenedores.md) | [0002](adr/0002-usar-fastapi-y-nextjs.md) | [`page.tsx`](../web/app/proyectos/[id]/page.tsx) · [`rutas_tareas.py`](../app/api/rutas_tareas.py) · [`servicio_tareas.py`](../app/application/servicio_tareas.py) | [`test_recorrido_completo_de_una_tarea`](../test/test_corte_vertical.py) | [ESC-02](calidad/escenarios-calidad.md#esc-02): ≤ 5 min sin capacitación |
| A-02 | Asignar tareas a integrantes | [RF-02](arc42/arc42-uniteam.md#11-resumen-de-requisitos) | [API](c4/nivel2-contenedores.md) | [0003](adr/0003-usar-eventos-de-dominio-en-proceso.md) | [`servicio_tareas.py`](../app/application/servicio_tareas.py) (`asignar_tarea`) | [`test_no_se_asigna_una_tarea_a_alguien_ajeno_al_proyecto`](../test/test_corte_vertical.py) | [ESC-03](calidad/escenarios-calidad.md#esc-03): 100 % denegado con 403 |
| A-03 | Establecer prioridades | [RF-03](arc42/arc42-uniteam.md#11-resumen-de-requisitos) | [API](c4/nivel2-contenedores.md) | [0002](adr/0002-usar-fastapi-y-nextjs.md) | [`modelos.py`](../app/domain/modelos.py) (`Prioridad`) | [`test_recorrido_completo_de_una_tarea`](../test/test_corte_vertical.py) | [ESC-02](calidad/escenarios-calidad.md#esc-02): flujo completo sin errores irrecuperables |
| A-04 | Definir estados de las tareas | [RF-04](arc42/arc42-uniteam.md#11-resumen-de-requisitos) | [API](c4/nivel2-contenedores.md) | [0003](adr/0003-usar-eventos-de-dominio-en-proceso.md) | [`modelos.py`](../app/domain/modelos.py) (`TRANSICIONES`) | [`test_transicion_invalida_se_rechaza`](../test/test_corte_vertical.py) | [ESC-05](calidad/escenarios-calidad.md#esc-05): ≤ 2 componentes por estado nuevo |
| A-05 | Establecer fechas límite | [RF-05](arc42/arc42-uniteam.md#11-resumen-de-requisitos) | [Base de datos](c4/nivel2-contenedores.md) | [0004](adr/0004-usar-mysql-como-base-de-datos.md) | [`tablas.py`](../app/infrastructure/tablas.py) (`fecha_limite`) | [`test_recorrido_completo_de_una_tarea`](../test/test_corte_vertical.py) | [ESC-04](calidad/escenarios-calidad.md#esc-04): 0 escrituras confirmadas perdidas |
| A-06 | Consultar el progreso | [RF-06](arc42/arc42-uniteam.md#11-resumen-de-requisitos) | [API](c4/nivel2-contenedores.md) → [Base de datos](c4/nivel2-contenedores.md) | [0004](adr/0004-usar-mysql-como-base-de-datos.md) | [`repositorios.py`](../app/infrastructure/repositorios.py) (`resumir_progreso`) · [`rutas_progreso.py`](../app/api/rutas_progreso.py) | [`test_el_progreso_resume_el_avance_del_proyecto`](../test/test_tablero.py) · [`test_la_paginacion_acota_el_tablero`](../test/test_tablero.py) | [ESC-01](calidad/escenarios-calidad.md#esc-01): **medido**, p95 de 762 ms frente a 2 s ([línea base](calidad/mediciones/esc-01-linea-base.md)) |
| A-07 | Aislar la información entre proyectos | [RF-02](arc42/arc42-uniteam.md#11-resumen-de-requisitos) | [API](c4/nivel2-contenedores.md) | [0003](adr/0003-usar-eventos-de-dominio-en-proceso.md) | [`servicio_tareas.py`](../app/application/servicio_tareas.py) (`_autorizar`) · [`consumidores.py`](../app/events/consumidores.py) | [`test_esc03_usuario_ajeno_no_accede_y_queda_auditado`](../test/test_corte_vertical.py) | [ESC-03](calidad/escenarios-calidad.md#esc-03): auditoría en ≤ 1 s |
| A-09 | Autenticar a los usuarios sin guardar contraseñas | [RF-02](arc42/arc42-uniteam.md#11-resumen-de-requisitos) | [Proveedor de identidad](c4/nivel2-contenedores.md) | [0005](adr/0005-delegar-la-autenticacion-en-un-proveedor-oidc.md) | [`seguridad.py`](../app/api/seguridad.py) · [`oidc.ts`](../web/lib/oidc.ts) | [`test_autenticacion.py`](../test/test_autenticacion.py) | [ESC-03](calidad/escenarios-calidad.md#esc-03): la identidad sale del token, no del cliente |
| A-08 | Gestionar los miembros de un proyecto | [RF-02](arc42/arc42-uniteam.md#11-resumen-de-requisitos) | [API](c4/nivel2-contenedores.md) | [0003](adr/0003-usar-eventos-de-dominio-en-proceso.md) | [`servicio_proyectos.py`](../app/application/servicio_proyectos.py) (`agregar_miembro`) | [`test_solo_el_lider_agrega_miembros`](../test/test_proyectos.py) | [ESC-03](calidad/escenarios-calidad.md#esc-03): solo el líder modifica la pertenencia |

### Cómo leer la columna Evidencia

Cada aspecto se cierra contra la **medida** de un escenario de calidad, no contra una opinión.
Conviene ser preciso sobre qué está realmente demostrado:

| Escenario | Estado de su medida |
|-----------|--------------------|
| [ESC-01](calidad/escenarios-calidad.md#esc-01) | **Medido.** p95 de 762 ms frente al umbral de 2 s, con el procedimiento reproducible en [la ficha de la medición](calidad/mediciones/esc-01-linea-base.md). Falta repetirlo de extremo a extremo sobre el despliegue real. |
| [ESC-03](calidad/escenarios-calidad.md#esc-03) | **Cubierto por pruebas automatizadas** que se ejecutan en cada `push` ([`ci.yml`](../.github/workflows/ci.yml)): denegación con 403, ausencia de datos en la respuesta y registro de auditoría. |
| [ESC-02](calidad/escenarios-calidad.md#esc-02) | **Sin medir.** Exige una prueba de usabilidad con 10 participantes ajenos al equipo. |
| [ESC-04](calidad/escenarios-calidad.md#esc-04) | **Sin medir.** La prueba enlazada en A-05 verifica que la escritura persiste, **no** que el sistema se recupere de una caída: falta la prueba de resiliencia que describe el escenario. |
| [ESC-05](calidad/escenarios-calidad.md#esc-05) | **Sin medir.** La prueba enlazada en A-04 cubre las transiciones de estado, no el costo de añadir uno nuevo. La medida se obtendrá al ejecutar realmente ese cambio. |

## Documentos relacionados

- [Mapa de interesados](calidad/interesados.md)
- [Escenarios de calidad](calidad/escenarios-calidad.md)
- [Árbol de utilidad](calidad/arbol-utilidad.md)
- [Documentación de arquitectura (arc42)](arc42/arc42-uniteam.md)
- [C4 nivel 1 — Contexto](c4/nivel1-contexto.md) · [C4 nivel 2 — Contenedores](c4/nivel2-contenedores.md)
- [Decisiones de arquitectura](adr/)
