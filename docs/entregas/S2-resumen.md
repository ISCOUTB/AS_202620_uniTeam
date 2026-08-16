# Entrega S2 — Interesados y escenarios de calidad

**UniTeam** · Arquitectura de Software · Semestre 2026-20 · 16 de agosto de 2026
**Equipo:** Julio César Emiliani · Ian Novoa Carrillo · Juan José Bustamante · Daniel Isaac Manjarrés
**Repositorio:** <https://github.com/ISCOUTB/AS_202620_uniTeam>

## Cómo hicimos el trabajo

**1. Primero el «para quién», no el «qué».** Antes de escribir un solo requisito de calidad
levantamos el mapa de interesados: seis interesados, desde el estudiante que usa la
herramienta a diario hasta el área de protección de datos de la universidad, incluyendo al
estudiante ajeno al proyecto como fuente de amenaza. De cada uno derivamos qué le importa y
qué atributo de calidad representa ese interés.

**2. Taller de reescritura.** Partimos de aspiraciones del tipo «el sistema debe ser rápido» y
las convertimos en escenarios de seis partes. La regla que nos impusimos fue simple: si no
podemos escribir el número con el que se comprueba, no es un escenario. Así salieron cinco
escenarios —rendimiento, usabilidad, seguridad, disponibilidad y modificabilidad— cada uno con
su método de verificación anotado.

**3. Árbol de utilidad para resolver el conflicto.** Los atributos se contradicen entre sí, así
que los ordenamos por impacto en el negocio y riesgo técnico. Seguridad quedó de primera
—(Alto, Alto)— porque una fuga entre equipos destruye la confianza en la herramienta y el
control de acceso atraviesa todo el sistema. Lo más útil del ejercicio fue escribir lo que
estamos dispuestos a **sacrificar**: no habrá alta disponibilidad, los permisos son por
proyecto y no por tarea, y el rendimiento se compromete solo hasta 200 tareas y 30 usuarios
concurrentes.

**4. Separar lo impuesto de lo elegido.** Clasificamos once restricciones en técnicas,
organizativas y legales, cada una con su justificación y su consecuencia arquitectónica, y las
mantuvimos separadas de los requisitos funcionales. Lo que todavía no está decidido no se
disfrazó de restricción: quedó como ADR pendiente.

## Decisiones que tomamos nosotros

- **Acotar el stack** a NestJS o FastAPI en backend y Flutter o Next.js en frontend. La
  elección concreta dentro de ese conjunto está abierta en ADR-001.
- **No desarrollar aplicación móvil.** El prototipo apunta a navegador web y/o escritorio, y
  eso condiciona la elección del frontend.
- **Priorizar seguridad** por encima de rendimiento y usabilidad, con las renuncias explícitas
  ya mencionadas.
- **Registrar en `docs/ia.md`** todo uso de IA generativa, los cambios de la aplicación y las
  decisiones del equipo. Usamos IA para redactar borradores y acelerar la escritura; el
  contenido lo revisamos y aprobamos nosotros antes de subirlo, y las decisiones quedan
  registradas como decisiones del equipo.

## Dónde está cada cosa

| Lo pedido | Ruta en el repositorio |
|-----------|------------------------|
| arc42 secciones 1–3 (y 10) | `docs/arc42/arc42-uniteam.md` |
| Árbol de utilidad | `docs/calidad/arbol-utilidad.md` |
| 5 escenarios de calidad con medida | `docs/calidad/escenarios-calidad.md` |
| Restricciones justificadas | `docs/arc42/arc42-uniteam.md` §2 |
| C4 de contexto (nivel 1) | `docs/c4/nivel1-contexto.md` |
| Mapa de interesados | `docs/calidad/interesados.md` |

Cada aspecto declarado en `docs/aspectos.md` enlaza con el escenario de calidad que lo hace
verificable.
