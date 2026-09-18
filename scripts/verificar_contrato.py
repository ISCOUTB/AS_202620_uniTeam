import yaml

with open("docs/api/openapi.yaml") as f:
    data = yaml.safe_load(f)

paths = list(data.get("paths", {}).keys())
schemas = list(data.get("components", {}).get("schemas", {}).keys())
responses = list(data.get("components", {}).get("responses", {}).keys())

print(f"openapi.yaml: válido")
print(f"  Rutas: {len(paths)}")
print(f"  Esquemas: {len(schemas)}")
print(f"  Respuestas: {len(responses)}")

required_paths = [
    "/proyectos",
    "/proyectos/{proyecto_id}",
    "/proyectos/{proyecto_id}/tareas",
    "/proyectos/{proyecto_id}/tareas/{tarea_id}",
    "/proyectos/{proyecto_id}/progreso",
]
for p in required_paths:
    assert p in paths, f"Falta ruta: {p}"
    print(f"  Ruta verificada: {p}")

required_schemas = [
    "CrearProyecto", "CrearTarea", "AsignarTarea", "CambiarEstado",
    "TareaSalida", "ProyectoSalida", "ProyectoDetalle",
    "MiembroSalida", "ProgresoSalida", "AgregarMiembro",
]
for s in required_schemas:
    assert s in schemas, f"Falta esquema: {s}"
    print(f"  Esquema verificado: {s}")

required_responses = [
    "NoAutenticado", "Prohibido", "NoEncontrado", "Conflicto",
    "SolicitudIncorrecta", "NoProcesable",
]
for r in required_responses:
    assert r in responses, f"Falta respuesta: {r}"
    print(f"  Respuesta verificada: {r}")

print("\nopenapi.yaml: TODO VERIFICADO")
