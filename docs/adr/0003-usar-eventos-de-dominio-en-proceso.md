# ADR-003 — Selección del estilo arquitectónico

- **Estado:** Aceptado
- **Fecha:** 2026-08-22
- **Decisores:** Equipo de desarrollo (I-04)
- **Stack:** FastAPI + Next.js

## Contexto

UniTeam requiere seleccionar un estilo arquitectónico que responda a sus escenarios de
calidad y restricciones. El escenario prioritario es **ESC-03 — Control de acceso entre
proyectos**, seguido por ESC-01 — Rendimiento, ESC-02 — Usabilidad, ESC-05 —
Modificabilidad y ESC-04 — Disponibilidad.

De acuerdo con la actividad, se comparan tres estilos: **arquitectura en capas,
arquitectura hexagonal y monolito modular**. La comparación se realiza sobre el
problema concreto de UniTeam y sus escenarios de calidad.

La matriz de decisión con la evaluación detallada de las alternativas se encuentra en
`matriz-decision-adr-003.md`.

## Alternativas consideradas

### 1. Arquitectura en capas

Organiza el sistema en capas de presentación, aplicación, dominio y persistencia.

**Fortalezas para UniTeam:**
- Sencilla de comprender e implementar.
- Buena compatibilidad con FastAPI.
- Bajo costo de infraestructura.
- Facilita separar responsabilidades.

**Limitaciones:**
- Puede aumentar el acoplamiento entre capas.
- Los cambios pueden propagarse por varias capas.
- La modificabilidad puede deteriorarse a medida que crece el sistema.

### 2. Arquitectura hexagonal

Separa el núcleo de negocio de la infraestructura mediante puertos y adaptadores.

**Fortalezas para UniTeam:**
- Aísla las reglas de negocio.
- Favorece la testabilidad.
- Facilita sustituir tecnologías externas.
- Permite centralizar reglas de seguridad en los casos de uso.

**Limitaciones:**
- Mayor complejidad inicial.
- Requiere más interfaces y adaptadores.
- Puede resultar excesiva para el alcance del prototipo y el tamaño del equipo.

### 3. Monolito modular

Mantiene un único sistema desplegable, pero divide la solución en módulos funcionales
con responsabilidades y límites claros.

**Fortalezas para UniTeam:**
- Mantiene una infraestructura sencilla.
- Facilita el desarrollo incremental.
- Permite aislar funcionalidades.
- Favorece la modificabilidad sin introducir complejidad distribuida.

**Limitaciones:**
- Los módulos comparten el mismo proceso y despliegue.
- Es necesario controlar las dependencias entre módulos.
- Un fallo del proceso puede afectar al sistema completo.

## Decisión

Se selecciona **Arquitectura Orientada a Eventos (Event-Driven Architecture)** como
estilo arquitectónico para UniTeam.

Aunque capas, hexagonal y monolito modular presentan ventajas importantes, se considera
que Event-Driven ofrece mejores posibilidades para desacoplar funcionalidades que pueden
crecer durante el desarrollo, especialmente aquellas relacionadas con cambios de estado,
auditoría, notificaciones y seguimiento del progreso.

La decisión se toma considerando principalmente:

- **ESC-03 — Seguridad:** permite generar eventos de auditoría después de validar la
  autorización.
- **ESC-01 — Rendimiento:** permite procesar de forma asíncrona tareas secundarias que
  no requieren bloquear la respuesta principal.
- **ESC-05 — Modificabilidad:** permite agregar nuevos consumidores ante eventos existentes
  sin modificar necesariamente el productor.
- **ESC-04 — Disponibilidad:** permite desacoplar procesos secundarios y aplicar
  reintentos cuando la infraestructura lo permita.

La autorización de acceso continuará siendo **sincrónica y obligatoria antes de ejecutar
la operación protegida o publicar eventos derivados de ella**.

## Tácticas arquitectónicas

Para el escenario prioritario **ESC-03 — Seguridad** se adoptan:

- Autorización a nivel de proyecto.
- Verificación de pertenencia antes de acceder a recursos.
- Centralización de las reglas de autorización.
- Registro de intentos de acceso no autorizado mediante eventos de auditoría.
- Pruebas automatizadas de aislamiento entre proyectos.
- Validación de autorización antes de publicar eventos.

Para favorecer la modificabilidad se utilizarán:

- Eventos de dominio.
- Publicación y suscripción.
- Consumidores independientes.
- Bajo acoplamiento entre funcionalidades.
- Idempotencia de consumidores cuando sea necesario.

## Consecuencias

### Positivas

- Mayor desacoplamiento entre funcionalidades.
- Facilita agregar nuevos comportamientos sin modificar los productores existentes.
- Permite procesar tareas secundarias de forma asíncrona.
- Favorece la trazabilidad mediante eventos de auditoría.
- Facilita la evolución incremental del sistema.

### Negativas

- Introduce mayor complejidad que una arquitectura en capas o un monolito simple.
- Puede producir consistencia eventual en determinados procesos.
- Requiere controlar duplicación, orden y reintentos de eventos.
- Puede requerir infraestructura adicional.
- El equipo debe adquirir conocimientos sobre procesamiento asíncrono.

## Alternativas descartadas

**Arquitectura en capas:** se descarta como estilo principal por ofrecer menor
desacoplamiento para la evolución de funcionalidades, aunque algunas de sus tácticas
podrán utilizarse dentro de la solución.

**Arquitectura hexagonal:** se descarta como estilo principal debido a la mayor cantidad
de interfaces y adaptadores que introduce para el alcance del prototipo. Sus principios
de inversión de dependencias podrán utilizarse cuando aporten valor.

**Monolito modular:** se descarta como estilo principal porque, aunque ofrece un buen
equilibrio entre simplicidad y modificabilidad, mantiene la comunicación entre
funcionalidades principalmente dentro del mismo proceso. Event-Driven permite un mayor
desacoplamiento para auditoría, notificaciones y otras reacciones a eventos.


## Implementación inicial

La decisión se acompaña de un esqueleto ejecutable del proyecto, con una prueba
automatizada en verde. Las instrucciones para ejecutar el proyecto se encuentran
en `README.md`.

## Referencia

La evaluación detallada de las tres alternativas se encuentra en:

`matriz-decision-adr-003.md`