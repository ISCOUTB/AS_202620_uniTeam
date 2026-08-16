# Mapa de interesados — UniTeam

Este documento identifica a los interesados de UniTeam y deriva, para cada uno, los
atributos de calidad que le importan. Es la entrada del [árbol de utilidad](arbol-utilidad.md)
y de los [escenarios de calidad](escenarios-calidad.md).

El método sigue a Bass, Clements & Kazman (cap. 3): primero se identifica **quién** tiene
algo en juego, luego **qué le importa**, y solo entonces se traduce ese interés a un
atributo de calidad que pueda medirse.

## Interesados identificados

| ID | Interesado | Rol | Qué le importa | Atributo(s) de calidad derivado(s) | Influencia | Interés |
|----|-----------|-----|----------------|-----------------------------------|-----------|---------|
| I-01 | Estudiante integrante | Usuario final principal | Que registrar y consultar una tarea no le cueste más esfuerzo que escribirla en el chat del grupo. Si la herramienta le estorba, vuelve al chat. | Usabilidad, Rendimiento | Media | Alto |
| I-02 | Líder de equipo | Usuario final con responsabilidad de coordinación | Ver de un vistazo el estado real del proyecto: qué falta, quién responde y qué está atrasado, sin tener que preguntar uno por uno. | Rendimiento, Disponibilidad, Usabilidad | Alta | Alto |
| I-03 | Profesor del curso | Observador y evaluador | Disponer de evidencia confiable del avance del equipo, sobre todo en las fechas de entrega. | Disponibilidad, Trazabilidad | Alta | Medio |
| I-04 | Equipo de desarrollo (4 integrantes) | Constructores y mantenedores del prototipo | Poder cambiar el sistema sin romperlo, con dedicación parcial y en un semestre. | Modificabilidad, Testeabilidad | Alta | Alto |
| I-05 | Universidad — área de TI y protección de datos | Responsable del cumplimiento | Que el manejo de datos personales de estudiantes cumpla la normativa y que no haya fugas de información entre equipos. | Seguridad, Privacidad | Alta (poder de veto) | Bajo hasta que ocurre un incidente |
| I-06 | Estudiante ajeno al proyecto | Interesado indirecto / fuente de amenaza | No debería poder acceder a la información de un equipo del que no forma parte. Es la fuente del estímulo en [ESC-03](escenarios-calidad.md#esc-03). | Seguridad | Baja | — |

## Conflictos entre interesados

Los atributos de calidad entran en conflicto entre sí, y resolverlos es una decisión del
equipo, no un resultado técnico automático. Estos son los conflictos detectados y cómo se
resolvieron:

**Seguridad (I-05) frente a Usabilidad (I-01).** El área de datos quiere control estricto de
acceso; el estudiante quiere entrar y registrar una tarea sin fricción. Un control de
permisos por tarea sería más seguro pero volvería tedioso el uso diario.
*Decisión del equipo:* el control de acceso se aplica **a nivel de proyecto**, no de tarea
individual. Es suficiente para impedir la fuga entre equipos —el riesgo real— y mantiene el
flujo de trabajo ligero.

**Rendimiento (I-02) frente a las restricciones de infraestructura.** El líder quiere el
tablero al instante, pero el prototipo se despliega en infraestructura gratuita con recursos
limitados (restricción T3).
*Decisión del equipo:* se acota la meta de rendimiento a un tamaño realista de proyecto
—200 tareas, 30 usuarios concurrentes— y se asume paginación en la vista. Prometer latencia
baja con volúmenes arbitrarios sería una aspiración, no un requisito.

**Modificabilidad (I-04) frente a velocidad de entrega (I-03).** El equipo quiere una
separación limpia en capas; el calendario de entregas semanales presiona por avanzar rápido.
*Decisión del equipo:* se acepta deuda técnica de forma consciente y se registra en la
sección 11 de arc42, en lugar de sobre-diseñar desde el inicio.

## Trazabilidad

Cada interesado tiene al menos un escenario de calidad que representa su interés:

| Interesado | Escenario que lo representa |
|-----------|----------------------------|
| I-01 | [ESC-02 — Usabilidad](escenarios-calidad.md#esc-02) |
| I-02 | [ESC-01 — Rendimiento](escenarios-calidad.md#esc-01) |
| I-03 | [ESC-04 — Disponibilidad](escenarios-calidad.md#esc-04) |
| I-04 | [ESC-05 — Modificabilidad](escenarios-calidad.md#esc-05) |
| I-05, I-06 | [ESC-03 — Seguridad](escenarios-calidad.md#esc-03) |
