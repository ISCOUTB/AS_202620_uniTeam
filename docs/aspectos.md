# Aspectos Declarados

## Gestión colaborativa de tareas

UniTeam implementará un sistema de gestión colaborativa de tareas para facilitar la
organización del trabajo dentro de equipos universitarios.

El aspecto será evidenciado en el prototipo mediante la creación, asignación, actualización y
consulta de tareas dentro de un proyecto.

## Aspectos y su escenario de calidad

Cada aspecto declarado se enlaza con el requisito funcional que lo formaliza en
[arc42 §1.1](arc42/arc42-uniteam.md#11-resumen-de-requisitos), con el atributo de calidad que
lo condiciona y con el [escenario de calidad](calidad/escenarios-calidad.md) que lo hace
verificable.

| ID | Aspecto declarado | RF | Atributo de calidad determinante | Escenario de calidad | Por qué ese escenario |
|----|------------------|----|----------------------------------|---------------------|----------------------|
| A-01 | Crear tareas | RF-01 | Usabilidad | [ESC-02](calidad/escenarios-calidad.md#esc-02) | Crear la primera tarea es el punto donde el usuario nuevo decide si la herramienta le sirve o vuelve al chat del grupo. |
| A-02 | Asignar tareas a integrantes del equipo | RF-02 | Seguridad | [ESC-03](calidad/escenarios-calidad.md#esc-03) | Asignar exige saber quién pertenece al proyecto; ahí es donde el control de acceso entre proyectos se pone a prueba. |
| A-03 | Establecer prioridades | RF-03 | Usabilidad | [ESC-02](calidad/escenarios-calidad.md#esc-02) | La prioridad se fija durante el mismo flujo de creación y asignación medido en el escenario. |
| A-04 | Definir estados de las tareas | RF-04 | Modificabilidad | [ESC-05](calidad/escenarios-calidad.md#esc-05) | El flujo de estados es lo que más va a cambiar: cada equipo trabaja distinto. |
| A-05 | Establecer fechas límite | RF-05 | Disponibilidad | [ESC-04](calidad/escenarios-calidad.md#esc-04) | El valor de la fecha límite se concentra en la semana de entregas, que es cuando el sistema no puede estar caído. |
| A-06 | Consultar el progreso de las actividades | RF-06 | Rendimiento | [ESC-01](calidad/escenarios-calidad.md#esc-01) | Consultar el avance debe ser más rápido que preguntar por el chat; si no, el aspecto no aporta valor. |

## Documentos relacionados

- [Mapa de interesados](calidad/interesados.md)
- [Escenarios de calidad](calidad/escenarios-calidad.md)
- [Árbol de utilidad](calidad/arbol-utilidad.md)
- [Documentación de arquitectura (arc42)](arc42/arc42-uniteam.md)
- [C4 nivel 1 — Contexto](c4/nivel1-contexto.md)
