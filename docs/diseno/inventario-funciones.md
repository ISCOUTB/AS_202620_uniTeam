# Inventario de funciones de la Aplicación Web

Este inventario responde a una pregunta concreta: **¿la reconstrucción visual cambió
alguna función?** La respuesta es no. Cada capacidad que existía antes sigue existiendo,
en el mismo lugar y con el mismo efecto; lo único que cambió es cómo se ve.

- **Antes:** `master` en `1c171a1` (checkpoint previo a la reconstrucción).
- **Después:** rama `feat/reconstruccion-visual`.
- **Regla aplicada:** no se añade ni se quita ninguna función de producto. Se permiten
  afinidades de presentación (enlace de salto, barra de navegación inferior, página 404
  con la identidad de la marca, restauración del foco), que no son funciones nuevas.

## 1. Sesión y acceso

| # | Función | Antes | Después | Estado |
|---|---|---|---|---|
| 1 | Iniciar sesión con el proveedor OIDC desde la cabecera | `barra-usuario.tsx` | Igual, con botón rediseñado | Intacta |
| 2 | Iniciar sesión desde la portada | `portada.tsx` | Igual, con nueva portada | Intacta |
| 3 | Error visible si el proveedor no responde, con el emisor configurado | `barra-usuario.tsx` | Igual | Intacta |
| 4 | Completar el flujo en `/callback/` y volver a la página pedida | `callback/page.tsx` | Igual | Intacta |
| 5 | Cerrar sesión | `barra-usuario.tsx` | Igual | Intacta |
| 6 | Caducidad del token: aviso y limpieza de la sesión | `lib/sesion.tsx`, `lib/api.ts` | Igual (no se tocó la lógica) | Intacta |
| 7 | Modo demostración (`NEXT_PUBLIC_DEMO_MODE=1`) | `lib/sesion.tsx` | Igual | Intacta |

## 2. Proyectos

| # | Función | Antes | Después | Estado |
|---|---|---|---|---|
| 8 | Listar los proyectos de los que se es miembro | `page.tsx` | Igual | Intacta |
| 9 | Resumen por proyecto: total, terminadas y vencidas | `page.tsx`, `lib/api.ts` | Igual, con anillo y barra | Intacta |
| 10 | Avatares del equipo y conteo de integrantes | `page.tsx` | Igual, con grupo de avatares | Intacta |
| 11 | Crear proyecto con nombre | `page.tsx` | Igual | Intacta |
| 12 | Añadir integrantes al crear, separados por coma o espacio, con validación de correo | `page.tsx`, `lib/lento.ts` | Igual, con error asociado al campo | Intacta |
| 13 | Estado vacío con acción para crear el primer proyecto | `page.tsx` | Igual, ilustrado | Intacta |
| 14 | Aviso de servidor despertando cuando la carga tarda | `page.tsx`, `lib/lento.ts` | Igual | Intacta |
| 15 | Esqueletos de carga | `page.tsx` | Igual, con brillo | Intacta |
| 16 | Error de carga con `role="alert"` | `page.tsx` | Igual | Intacta |

## 3. Tablero

| # | Función | Antes | Después | Estado |
|---|---|---|---|---|
| 17 | Cargar proyecto, tareas, progreso y flujo de estados | `tablero.tsx` | Igual (mismas cuatro llamadas en paralelo) | Intacta |
| 18 | Columnas construidas desde `GET /flujo-estados` | `tablero.tsx`, `lib/flujo.ts` | Igual | Intacta |
| 19 | Cambiar de estado con los botones de flecha | `tarjeta-tarea.tsx` | Igual | Intacta |
| 20 | Arrastrar y soltar con destinos válidos e inválidos resaltados | `tablero.tsx` | Igual, con clases `destino-valido` / `destino-invalido` | Intacta |
| 21 | Crear tarea desde el diálogo | `dialogo-tarea.tsx` | Igual, con prioridad segmentada | Intacta |
| 22 | Editar título, prioridad, responsable y fecha límite | `dialogo-tarea.tsx` | Igual | Intacta |
| 23 | Alta rápida al pie de cada columna (prioridad media) | `tablero.tsx` | Igual | Intacta |
| 24 | Eliminar con «Deshacer» durante 6 s y borrado real al vencer o al salir | `tablero.tsx`, `lib/avisos.tsx` | Igual (mismo temporizador y `pagehide`) | Intacta |
| 25 | Reasignar responsable desde la tarjeta | `tarjeta-tarea.tsx` | Igual | Intacta |
| 26 | Filtrar por responsable (incluido «sin responsable») | `tablero.tsx` | Igual | Intacta |
| 27 | Filtrar por prioridad | `tablero.tsx` | Igual | Intacta |
| 28 | Buscar tareas por título | `tablero.tsx` | Igual | Intacta |
| 29 | Atajos `N` (nueva tarea) y `/` (buscar), ignorados al escribir | `tablero.tsx` | Igual | Intacta |
| 30 | Aviso cuando el tablero alcanza el límite de 200 tareas | `tablero.tsx` | Igual | Intacta |
| 31 | Progreso: porcentaje, barra, anillo y métricas de total, en curso, sin responsable y vencidas | `resumen-proyecto.tsx` | Igual, extraído del tablero | Intacta |
| 32 | Fechas relativas y estado de vencimiento (vencida, hoy, pronto, a tiempo) | `lib/fechas.ts` | Igual | Intacta |
| 33 | Marcar visualmente las tareas hechas | `tarjeta-tarea.tsx` | Igual | Intacta |
| 34 | Bloqueo visual de una tarjeta mientras se guarda | `tablero.tsx` | Igual | Intacta |
| 35 | Ver integrantes y rol | `panel-miembros.tsx` | Igual, con avatares | Intacta |
| 36 | Añadir integrante (solo líder) | `panel-miembros.tsx` | Igual | Intacta |
| 37 | Mensaje para quien no es líder | `panel-miembros.tsx` | Igual | Intacta |

## 4. Mis tareas

| # | Función | Antes | Después | Estado |
|---|---|---|---|---|
| 38 | Listar las tareas asignadas al usuario en todos sus proyectos | `mis-tareas/page.tsx` | Igual | Intacta |
| 39 | Agrupar por vencidas, hoy, próximos 7 días, después y sin fecha | `mis-tareas/page.tsx`, `lib/fechas.ts` | Igual, con bandejas | Intacta |
| 40 | Mostrar u ocultar las terminadas | `mis-tareas/page.tsx` | Igual, con interruptor | Intacta |
| 41 | Enlace al proyecto de cada tarea | `mis-tareas/page.tsx` | Igual | Intacta |
| 42 | Estado vacío | `mis-tareas/page.tsx` | Igual, ilustrado | Intacta |

## 5. Transversal

| # | Función | Antes | Después | Estado |
|---|---|---|---|---|
| 43 | Tema claro/oscuro que sigue al sistema y recuerda la elección | `selector-tema.tsx` | Igual lógica, nuevo interruptor | Intacta |
| 44 | Avisos flotantes con acción y barra de duración | `lib/avisos.tsx` | Igual lógica, nuevos iconos y barra | Intacta |
| 45 | Navegación entre Proyectos y Mis tareas | `navegacion.tsx` | Igual | Intacta |
| 46 | Aplicación instalable: manifiesto e iconos | `layout.tsx`, `public/` | Igual, con los colores nuevos | Intacta |
| 47 | Diseño adaptable de 320 px a escritorio | `globals.css` | Reescrito, mismos puntos de corte | Intacta |
| 48 | Título de documento por página | `page.tsx`, `mis-tareas/page.tsx` | Igual | Intacta |

## 6. Lo que no se añadió

Estas capacidades se consideraron y **no** entraron, porque habrían sido funciones
nuevas o habrían exigido cambios de esquema o de despliegue:

- Descripción, comentarios, subtareas, etiquetas, adjuntos, recordatorios, orden manual
  y actividad del proyecto.
- Asistente con IA generativa (descartado en la [ADR-014](../adr/0014-no-incorporar-un-componente-generativo.md)).
- Filtros guardados, vistas por persona o notificaciones push.
- Cualquier dependencia nueva de ejecución. `web/package.json` no cambió.

## 7. Afinidades de presentación

No son funciones de producto; son la consecuencia de reconstruir la interfaz:

| Afinidad | Por qué |
|---|---|
| Enlace «Saltar al contenido» | Accesibilidad; no altera el flujo. |
| Barra de navegación inferior en pantallas estrechas | Repite los dos enlaces que ya existían en la cabecera. |
| Restauración del foco al cerrar el diálogo | Accesibilidad; el diálogo ya existía. |
| Página 404 con la identidad de la marca | Antes era la página por defecto de Next.js; la ruta no existía como función. |
| Ilustración de la portada en HTML y CSS | Sustituye a la composición anterior; no añade contenido nuevo. |
| Iconos SVG en línea | Sustituyen a los emojis y caracteres usados antes. |

## 8. Cómo se verificó

1. **Lectura completa** de cada página y componente antes de reescribirlo, con la lista
   de clases y de llamadas a la API a la vista.
2. **Auditoría de paridad** sobre `git diff HEAD -- web/`: se revisó que no
   desapareciera ningún manejador, condición, efecto ni llamada a `api.*`.
3. **Compilación:** `npx tsc --noEmit` sin errores y `npm run build` con las rutas
   `/`, `/callback/`, `/mis-tareas/`, `/proyecto/` y `404.html`.
4. **Cobertura de clases:** 164 clases usadas en TSX, todas con regla CSS o variante
   dinámica documentada.
5. **Recorrido visual** con Edge headless sobre el sitio exportado y una API simulada
   con la misma forma que la real: portada, proyectos, tablero y mis tareas, en claro y
   oscuro, a 1440 px y 390 px.
