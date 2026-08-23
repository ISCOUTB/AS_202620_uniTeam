# Matriz comparativa de estilos arquitectónicos

## Proyecto: UniTeam

Se comparan los tres estilos arquitectónicos solicitados para el problema concreto
de UniTeam: **arquitectura en capas, arquitectura hexagonal y monolito modular**.

La evaluación considera los escenarios de calidad priorizados y las restricciones
del proyecto.

**Escala:** 5 = muy favorable · 4 = favorable · 3 = aceptable · 2 = desfavorable · 1 = muy desfavorable.

| Criterio | Capas | Hexagonal | Monolito modular |
|---|---|---|---|
| **ESC-03 — Seguridad** | **4/5.** Permite centralizar autenticación y autorización en servicios y dependencias de FastAPI. Requiere asegurar que todos los endpoints apliquen las reglas de acceso al proyecto. | **5/5.** Las reglas de autorización pueden mantenerse en los casos de uso y dominio, reduciendo la dependencia de los controladores HTTP. | **5/5.** Cada módulo puede encapsular sus reglas de acceso y exponer únicamente las operaciones permitidas. |
| **ESC-01 — Rendimiento** | **4/5.** Tiene poca sobrecarga y permite utilizar índices, paginación y consultas optimizadas para las tareas y proyectos. | **4/5.** Permite optimizar la persistencia, aunque incorpora abstracciones adicionales entre dominio e infraestructura. | **4/5.** Al ejecutarse como una aplicación única evita costos de comunicación entre servicios y permite optimizar directamente las consultas. |
| **ESC-02 — Usabilidad** | **4/5.** Separa la API de FastAPI del frontend Next.js y facilita mantener organizada la aplicación, aunque la usabilidad depende principalmente del frontend. | **4/5.** El dominio independiente facilita evolucionar la API sin acoplarla a la interfaz, pero no mejora directamente la experiencia de usuario. | **4/5.** Permite desarrollar funcionalidades relacionadas dentro de módulos y mantener una API integrada con Next.js. |
| **ESC-05 — Modificabilidad** | **3/5.** La separación por capas ayuda a organizar el código, pero un cambio puede afectar presentación, aplicación, dominio y persistencia. | **5/5.** El dominio está aislado de frameworks e infraestructura, facilitando cambios y pruebas. | **5/5.** Los módulos permiten modificar una funcionalidad sin afectar directamente a las demás si se respetan sus límites e interfaces. |
| **ESC-04 — Disponibilidad** | **3/5.** Es sencillo de desplegar, pero un fallo en la aplicación puede afectar al sistema completo. | **3/5.** El aislamiento facilita sustituir componentes, pero no proporciona recuperación ante fallos por sí mismo. | **4/5.** Los módulos reducen el acoplamiento lógico, aunque el sistema continúa teniendo un único despliegue. |
| **Complejidad para el equipo** | **5/5.** Es fácil de entender y adecuado para un equipo pequeño con dedicación parcial. | **3/5.** Requiere comprender puertos, adaptadores e inversión de dependencias, aumentando el esfuerzo inicial. | **4/5.** Mantiene una aplicación única pero introduce límites claros entre módulos. |
| **Infraestructura y costo** | **5/5.** Puede funcionar con FastAPI, Next.js y una base de datos sin infraestructura adicional. | **5/5.** Los puertos y adaptadores son principalmente una organización interna del código y no requieren infraestructura adicional. | **5/5.** Puede desplegarse como una única aplicación, compatible con la restricción de infraestructura gratuita. |
| **Adecuación al prototipo UniTeam** | **5/5.** Es simple, conocida y suficiente para el alcance inicial del proyecto. | **3/5.** Aporta buenas propiedades de diseño, pero puede introducir abstracciones innecesarias para el tamaño del prototipo. | **5/5.** Ofrece un buen equilibrio entre simplicidad, organización y capacidad de evolución. |

## Conclusión de la comparación

| Estilo | Fortalezas para UniTeam | Limitaciones para UniTeam |
|---|---|---|
| **Capas** | Simplicidad, bajo costo, facilidad de aprendizaje y buena integración con FastAPI. | Los cambios pueden propagarse entre varias capas y aumentar el acoplamiento. |
| **Hexagonal** | Excelente aislamiento del dominio, seguridad, testabilidad y modificabilidad. | Mayor complejidad inicial para un equipo pequeño y un prototipo limitado. |
| **Monolito modular** | Buen equilibrio entre simplicidad, seguridad, modificabilidad y bajo costo de infraestructura. | Requiere disciplina para mantener los límites entre módulos y evitar dependencias indebidas. |

## Decisión final

La comparación de capas, arquitectura hexagonal y monolito modular permite identificar
sus ventajas y compromisos frente al problema concreto de UniTeam.

A partir de esta evaluación y de los escenarios de calidad priorizados, el equipo
selecciona **Event-Driven Architecture (EDA)** como estilo arquitectónico principal
para UniTeam.

Event-Driven se selecciona principalmente porque permite:

- **Desacoplar funcionalidades** mediante eventos de dominio.
- Favorecer la **modificabilidad (ESC-05)** al permitir agregar nuevos consumidores
  sin modificar necesariamente los productores.
- Ejecutar de forma **asíncrona** tareas secundarias como auditoría, notificaciones
  y actualización de estadísticas.
- Favorecer la **disponibilidad (ESC-04)** mediante desacoplamiento y reintentos.
- Mejorar la **trazabilidad (ESC-03)** mediante eventos de auditoría, manteniendo
  siempre la autorización antes de publicar eventos.
- Mantener el procesamiento principal sencillo y compatible con la infraestructura
  gratuita disponible para el proyecto.

La arquitectura orientada a eventos se aplicará de manera **pragmática**, evitando
introducir infraestructura distribuida innecesaria para el alcance del prototipo.

**resultado:** La matriz compara los tres estilos exigidos por la actividad. La selección
de Event-Driven se documenta como la decisión arquitectónica final en el ADR-003.