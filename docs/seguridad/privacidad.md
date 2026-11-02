# Privacidad: datos personales tratados y base de tratamiento

## Datos personales que trata UniTeam

| Dato | Origen | Dónde se almacena | Finalidad |
|------|--------|-------------------|-----------|
| Identificador de usuario (`sub`) | Proveedor OIDC | MySQL | Identificar al usuario y asociarlo a equipos |
| Nombre | Proveedor OIDC | MySQL | Mostrar responsables de tareas |
| Correo institucional | Proveedor OIDC | MySQL | Identificar al usuario e invitarlo a equipos |
| Pertenencia a equipos | Acciones del usuario | MySQL | Control de acceso a tareas |
| Tareas asignadas, prioridad y estado | Acciones del usuario | MySQL | Coordinación del trabajo; permite inferir la carga de cada persona |

UniTeam **no almacena contraseñas**: la autenticación se delega en el proveedor OpenID Connect (ADR 0005).
Aunque el sistema sea académico, el nombre y el correo son datos personales; no se afirma que no se traten.

## Base de tratamiento

- **Marco:** Ley 1581 de 2012 (habeas data) y Decreto 1377 de 2013, Colombia.
- **Base:** autorización del titular, otorgada al iniciar sesión mediante el proveedor OIDC, para la finalidad de coordinar tareas de equipos universitarios.
- **Minimización:** solo se guardan los datos que entrega el proveedor OIDC y los que el usuario crea; no se recolectan teléfono, documento ni dirección.
- **Acceso:** un usuario solo ve los datos de los equipos a los que pertenece (T1, ADR 0010).
- **Conservación:** los datos se conservan mientras dure el semestre académico del proyecto y se eliminan al cierre del mismo.
- **Derechos del titular:** consulta, corrección y supresión; se atienden solicitando al equipo de desarrollo (contacto en el README).
- **Terceros:** el proveedor de identidad (OIDC) recibe el inicio de sesión del usuario; no se comparten datos con otros terceros.
- **Repositorio público:** no deben subirse datos reales de usuarios; los datos de prueba son ficticios.
