# ADR-017 — Sistema visual editorial y CSS por capas

- **Estado:** Aceptada
- **Fecha:** 2026-11-19
- **Decisores:** Equipo de desarrollo
- **Relacionada:** [ADR-002](0002-usar-fastapi-y-nextjs.md) eligió el stack;
  [ADR-007](0007-servir-la-aplicacion-web-como-sitio-estatico.md) fijó el export
  estático; sirve a [ESC-02](../calidad/escenarios-calidad.md#esc-02) y
  [ESC-05](../calidad/escenarios-calidad.md#esc-05).

## Contexto

La Aplicación Web creció por capas de funcionalidad: primero el tablero, después la
edición y el borrado, luego Mis tareas, el modo oscuro y la instalación como aplicación.
Cada una añadió reglas al mismo `globals.css`, que llegó a 949 líneas. El resultado
funcionaba, pero tenía tres problemas medibles:

1. **No había una fuente de verdad del color.** Los hexadecimales estaban repartidos
   entre reglas y componentes; el modo oscuro duplicaba bloques de variables que podían
   desincronizarse.
2. **La precedencia se resolvía por orden de aparición.** Un ajuste de una página
   competía con el componente que quería ajustar, y la salida fácil era `!important`.
3. **La interfaz no tenía voz propia.** Los componentes eran correctos pero genéricos:
   el mismo lenguaje visual que cualquier panel de administración.

La reconstrucción de 2026-11-19 se planteó como un cambio **solo de presentación**. La
restricción fue explícita: ni una función nueva, ni una quitada, ni una dependencia
nueva de ejecución, y el export estático debía seguir compilando.

## Alternativas

| Alternativa | Ventajas | Costos y riesgos |
|---|---|---|
| **Mantener el CSS actual y retocarlo** | Cero riesgo de regresión; no hay que aprender nada. | Conserva la duplicación del tema oscuro, la precedencia implícita y la falta de tokens; cada ajuste futuro vuelve a competir con el resto. |
| **Adoptar un framework de utilidades (Tailwind)** | Ecosistema amplio y velocidad para prototipar. | Añade dependencia y un paso de construcción; obliga a reescribir todo el marcado; el repositorio ya declara «sin dependencias nuevas» y el equipo no lo domina. |
| **CSS-in-JS o CSS Modules** | Encapsula estilos por componente. | Añade dependencia y coste en tiempo de ejecución o de build; no resuelve la paleta ni la precedencia por sí solo. |
| **Tokens + capas de cascada + `light-dark()` (elegida)** | Una sola declaración de color con dos caras; precedencia explícita; cero dependencias; el export estático no cambia. | Exige disciplina de capas y un navegador moderno (§Consecuencias). |

## Decisión

Se adopta el sistema **«Editorial Campus»**:

1. **Tokens en `web/app/estilos/tokens.css`.** Color, tipografía, espacio, forma,
   elevación y movimiento se declaran una vez. La paleta usa `light-dark()` con
   `color-scheme`; el tema oscuro es la otra cara del mismo token, no un bloque paralelo.
   La preferencia explícita se resuelve con `:root[data-theme="light"|"dark"]`.
2. **Siete hojas con un oficio cada una** (`tokens`, `reset`, `base`, `layout`,
   `componentes`, `paginas`, `movimiento`), importadas desde `globals.css`, que solo
   declara el orden con `@layer`. Ninguna regla del proyecto usa `!important`.
3. **Tipografía con dos voces:** Fraunces (serif variable) para los títulos y Manrope
   para la interfaz, servidas por `next/font` desde el propio sitio.
4. **Componentes de presentación nuevos** —`iconos`, `estado-vacio`, `anillo-progreso`,
   `tarjeta-proyecto`, `nav-movil`, `resumen-proyecto`, `filtros-tablero`— que no
   contienen lógica de negocio: reciben datos y devuelven marcado.
5. **Se conservan los nombres de archivo y de clase** que enlazan
   [`docs/aspectos.md`](../aspectos.md) y las pruebas de contrato visual, para no romper
   la trazabilidad.

El equipo aprueba esta dirección y la registra como decisión **D-027** en
[`docs/ia.md`](../ia.md). La IA propuso y ejecutó la reconstrucción; la elección del
estilo, la paleta y la regla de «ninguna función nueva» son del equipo.

## Consecuencias y costo de reversión

- **Cero dependencias nuevas.** `web/package.json` no cambia; el sitio sigue siendo
  estático y las fuentes se sirven desde el mismo origen.
- **El color se cambia en un archivo.** Cambiar la marca es cambiar dos o tres tokens;
  no hay que recorrer componentes.
- **La precedencia se lee.** El orden de capas es una línea; una página puede ajustar un
  componente sin reescribirlo ni recurrir a `!important`.
- **Costo de aprendizaje.** Quien añada estilos debe saber en qué capa va cada regla.
  La guía está en [`sistema-visual.md`](../diseno/sistema-visual.md), §3 y §12.
- **Línea base de navegador.** `light-dark()` exige Chrome/Edge 123, Firefox 120 o
  Safari 17.5 (2024). Es aceptable para el prototipo y para los navegadores actuales,
  pero **no hay una segunda paleta de reserva**: si se necesitara soportar un navegador
  anterior, habría que añadir un bloque de variables de respaldo y volver a medir el
  contraste. Se deja escrito para que la decisión no se descubra tarde.
- **Costo de reversión.** Bajo en código —las hojas son archivos nuevos y el marcado
  conserva sus clases—, alto en trabajo: volver atrás significa recuperar la hoja única
  y perder la verificación de contraste y de paridad funcional que acompaña a esta
  decisión.

## Trazabilidad

- Sistema visual y reglas de extensión: [`docs/diseno/sistema-visual.md`](../diseno/sistema-visual.md).
- Inventario y verificación de que no cambió ninguna función:
  [`docs/diseno/inventario-funciones.md`](../diseno/inventario-funciones.md).
- Tokens y capas: [`web/app/estilos/`](../../web/app/estilos/) y
  [`web/app/globals.css`](../../web/app/globals.css).
- Escenarios: [ESC-02](../calidad/escenarios-calidad.md#esc-02) (usabilidad) y
  [ESC-05](../calidad/escenarios-calidad.md#esc-05) (modificabilidad).
- Export estático: [ADR-007](0007-servir-la-aplicacion-web-como-sitio-estatico.md).
- Registro de la decisión y del uso de IA: [`docs/ia.md`](../ia.md).
