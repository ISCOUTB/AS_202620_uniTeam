# Escenarios de calidad — UniTeam

Cinco escenarios de calidad en formato de seis partes (Bass, Clements & Kazman, cap. 4).
Cada uno nace de un [interesado identificado](interesados.md) y tiene una **medida de
respuesta verificable**: un número que se puede comprobar, no una aspiración.

Las seis partes son: **fuente** del estímulo, **estímulo**, **artefacto** afectado,
**entorno** en que ocurre, **respuesta** del sistema y **medida de la respuesta**.

La prioridad de cada escenario se expresa como `(impacto en el negocio, riesgo técnico)` en
escala Alto / Medio / Bajo, y se justifica en el [árbol de utilidad](arbol-utilidad.md).

---

<a id="esc-01"></a>

## ESC-01 — Rendimiento: latencia de consulta del tablero

**Atributo:** Rendimiento · **Prioridad:** (Alto, Medio) · **Interesado:** I-02 Líder de equipo **ADR:**[ADR-003 — Selección del estilo arquitectónico](../adr/0003-usar-eventos-de-dominio-en-proceso.md)

| Parte | Contenido |
|-------|-----------|
| Fuente | Líder de equipo autenticado. |
| Estímulo | Solicita la vista de tablero de un proyecto para revisar el estado general del trabajo. |
| Artefacto | Servicio de consulta de tareas e interfaz del tablero. |
| Entorno | Operación normal, con un proyecto de 200 tareas y 30 usuarios concurrentes, sobre la infraestructura gratuita de despliegue (restricción T3). |
| Respuesta | El sistema devuelve y presenta el tablero completo, con estado, responsable, prioridad y fecha límite de cada tarea. |
| **Medida** | **Latencia de extremo a extremo ≤ 2 s en el percentil 95 y ≤ 4 s en el percentil 99; 0 errores en 100 solicitudes consecutivas.** |

**Por qué importa.** Si consultar el estado del proyecto es más lento que preguntar por el
chat del grupo, el equipo vuelve al chat y la herramienta pierde su razón de ser.

**Cómo se verifica.** Prueba de carga automatizada sobre un conjunto de datos sintético de
200 tareas, con 30 usuarios virtuales concurrentes, midiendo percentiles de latencia.

---

<a id="esc-02"></a>

## ESC-02 — Usabilidad: facilidad de aprendizaje en el primer uso

**Atributo:** Usabilidad · **Prioridad:** (Alto, Medio) · **Interesado:** I-01 Estudiante integrante

| Parte | Contenido |
|-------|-----------|
| Fuente | Estudiante que nunca ha usado UniTeam y no ha recibido capacitación. |
| Estímulo | Quiere crear su primer proyecto y repartir 3 tareas entre 3 compañeros. |
| Artefacto | Interfaz de usuario completa: registro, creación de proyecto, creación y asignación de tareas. |
| Entorno | Primer uso en tiempo de ejecución, sin manual, sin tutorial y sin ayuda de otro usuario. |
| Respuesta | El estudiante completa el flujo por su cuenta, sin bloquearse y sin cometer errores irrecuperables. |
| **Medida** | **Tiempo de la tarea ≤ 5 minutos; al menos 8 de cada 10 participantes de prueba completan el flujo; promedio ≤ 1 error recuperable por participante y 0 errores irrecuperables.** |

**Por qué importa.** La adopción es el negocio de esta herramienta. Un equipo universitario
no invierte una tarde en aprender a usar un gestor de tareas para un trabajo de una semana.

**Cómo se verifica.** Prueba de usabilidad cronometrada con 10 estudiantes ajenos al equipo
de desarrollo, observando sin intervenir y registrando tiempo, errores y abandonos.

---

<a id="esc-03"></a>

## ESC-03 — Seguridad: control de acceso entre proyectos

**Atributo:** Seguridad · **Prioridad:** (Alto, Alto) · **Interesados:** I-05 Universidad, I-06 Estudiante ajeno **ADR:** [ADR-003 — Selección del estilo arquitectónico](../adr/0003-usar-eventos-de-dominio-en-proceso.md)

| Parte | Contenido |
|-------|-----------|
| Fuente | Usuario autenticado que **no** es miembro del proyecto objetivo. |
| Estímulo | Solicita directamente por la API el detalle de una tarea de un proyecto ajeno, usando un identificador válido obtenido por enumeración o adivinación. |
| Artefacto | Capa de autorización de la API y registro de auditoría. |
| Entorno | Operación normal, sistema en producción. |
| Respuesta | El sistema deniega la solicitud, no devuelve ningún campo del recurso ni confirma su existencia, y registra el intento fallido. |
| **Medida** | **100 % de las solicitudes no autorizadas denegadas con HTTP 403; 0 campos del recurso presentes en la respuesta; evento de auditoría escrito en ≤ 1 s con usuario, recurso solicitado y marca de tiempo.** |

**Por qué importa.** Es el escenario de mayor riesgo del sistema: una fuga de información
entre equipos destruye la confianza en la herramienta y compromete al equipo frente a la
normativa de datos personales (restricción L1). Además, el control de acceso atraviesa todos
los endpoints, así que un error de diseño aquí se propaga a todo el sistema.

**Cómo se verifica.** Suite de pruebas automatizadas de control de acceso, con al menos un
caso negativo por cada endpoint que expone datos de un proyecto, ejecutada en integración
continua. La construcción es fallida si un solo caso devuelve datos.

---

<a id="esc-04"></a>

## ESC-04 — Disponibilidad: recuperación ante falla en periodo de entregas

**Atributo:** Disponibilidad · **Prioridad:** (Medio, Medio) · **Interesado:** I-03 Profesor, I-02 Líder de equipo **ADR:** [ADR-003 — Selección del estilo arquitectónico](../adr/0003-usar-eventos-de-dominio-en-proceso.md)

| Parte | Contenido |
|-------|-----------|
| Fuente | Falla interna del sistema: el proceso del backend termina de forma abrupta. |
| Estímulo | Caída no planificada del servicio. |
| Artefacto | Backend y almacenamiento persistente. |
| Entorno | Semana de entregas académicas, con el pico de uso del semestre, sobre infraestructura gratuita. |
| Respuesta | El sistema detecta la caída, reinicia automáticamente y restablece el servicio. Las tareas confirmadas antes de la caída siguen presentes y consistentes. |
| **Medida** | **Servicio disponible nuevamente en ≤ 2 minutos; 0 pérdidas de escrituras ya confirmadas al usuario; disponibilidad mensual ≥ 99 % (máximo 7 h 12 min de indisponibilidad al mes).** |

**Por qué importa.** La utilidad de la herramienta se concentra en las fechas de entrega. Una
caída en cualquier otro momento es una molestia; una caída la noche antes de entregar es la
razón por la que el equipo deja de usarla.

**Cómo se verifica.** Prueba de resiliencia: se termina el proceso del backend de forma
deliberada y se cronometra el restablecimiento, verificando después la integridad de los
datos. La disponibilidad se mide con un chequeo automático cada 5 minutos.

---

<a id="esc-05"></a>

## ESC-05 — Modificabilidad: extensión del flujo de estados

**Atributo:** Modificabilidad · **Prioridad:** (Medio, Alto) · **Interesado:** I-04 Equipo de desarrollo **ADR:** [ADR-003 — Selección del estilo arquitectónico](../adr/0003-usar-eventos-de-dominio-en-proceso.md)

| Parte | Contenido |
|-------|-----------|
| Fuente | Desarrollador del equipo. |
| Estímulo | Solicitud de agregar un nuevo estado de tarea —«En revisión»— al flujo de trabajo existente. |
| Artefacto | Modelo de dominio de la tarea, API y componentes de interfaz del tablero. |
| Entorno | Tiempo de desarrollo, sobre el código base del prototipo. |
| Respuesta | El cambio se implementa, se prueba y se integra sin romper la funcionalidad existente ni el contrato público de la API. |
| **Medida** | **≤ 2 componentes modificados, ≤ 1 día-persona de esfuerzo, 0 cambios incompatibles en la API pública y la suite de pruebas existente en verde.** |

**Por qué importa.** El flujo de estados es lo que más se va a mover: cada equipo trabaja
distinto. Si añadir un estado obliga a tocar medio sistema, el prototipo no sobrevive al
semestre con un equipo de dedicación parcial.

**Cómo se verifica.** Cuando el cambio se ejecute realmente, se cronometra el esfuerzo y se
cuentan los componentes tocados en el commit correspondiente.

---

## Resumen

| ID | Atributo | Medida de respuesta | Prioridad (impacto, riesgo) |ADR asociado|
|----|----------|--------------------|-----------------------------|-----|
| [ESC-01](#esc-01) | Rendimiento | p95 ≤ 2 s con 200 tareas y 30 usuarios concurrentes | (Alto, Medio) |[ADR-003 — Selección del estilo arquitectónico](../adr/0003-usar-eventos-de-dominio-en-proceso.md)|
| [ESC-02](#esc-02) | Usabilidad | ≤ 5 min, 8 de 10 participantes, sin ayuda | (Alto, Medio) |---|
| [ESC-03](#esc-03) | Seguridad | 100 % denegado con 403, 0 datos expuestos, auditoría ≤ 1 s | (Alto, Alto) |[ADR-003 — Selección del estilo arquitectónico](../adr/0003-usar-eventos-de-dominio-en-proceso.md)|
| [ESC-04](#esc-04) | Disponibilidad | Restablecimiento ≤ 2 min, 0 escrituras perdidas, ≥ 99 % mensual | (Medio, Medio) |[ADR-003 — Selección del estilo arquitectónico](../adr/0003-usar-eventos-de-dominio-en-proceso.md)|
| [ESC-05](#esc-05) | Modificabilidad | ≤ 2 componentes, ≤ 1 día-persona, API estable | (Medio, Alto) |[ADR-003 — Selección del estilo arquitectónico](../adr/0003-usar-eventos-de-dominio-en-proceso.md)|
