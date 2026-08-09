# Aspecto declarado

## Control de acceso y autorización por roles (RBAC)

UniTeam implementará un mecanismo de autorización basado en roles, para restringir el acceso a las funcionalidades
y recursos según el tipo de usuario.

### Roles

- Estudiante
- Profesor
- Administrador

### Objetivo

Garantizar que cada usuario solamente pueda ejecutar las operaciones
correspondientes a sus permisos.

### Evidencia en el prototipo

El backend implementará autenticación y autorización mediante roles,
aplicando restricciones sobre los endpoints según el usuario autenticado.
