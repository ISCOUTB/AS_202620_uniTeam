"""Tablero: filtros, paginación y resumen de progreso.

La paginación y el resumen agregado son las tácticas que arc42 §4.3 declara
para ESC-01. Estas pruebas comprueban que existen y se comportan.
"""
from datetime import date, timedelta


def _proyecto_con_tareas(cliente, cab, n=5, lider="ana"):
    proyecto_id = cliente.post(
        "/proyectos",
        json={"nombre": "Arquitectura", "miembros": ["bruno"]},
        headers=cab(lider),
    ).json()["id"]
    for i in range(n):
        cliente.post(
            f"/proyectos/{proyecto_id}/tareas",
            json={
                "titulo": f"Tarea {i}",
                "responsable": "bruno" if i % 2 == 0 else None,
            },
            headers=cab(lider),
        )
    return proyecto_id


def test_la_paginacion_acota_el_tablero(cliente, cab):
    proyecto_id = _proyecto_con_tareas(cliente, cab, n=5)
    cabeceras = cab("ana")

    primera = cliente.get(
        f"/proyectos/{proyecto_id}/tareas?limite=2", headers=cabeceras
    ).json()
    segunda = cliente.get(
        f"/proyectos/{proyecto_id}/tareas?limite=2&desplazamiento=2", headers=cabeceras
    ).json()

    assert [t["titulo"] for t in primera] == ["Tarea 0", "Tarea 1"]
    assert [t["titulo"] for t in segunda] == ["Tarea 2", "Tarea 3"]
    assert not set(t["id"] for t in primera) & set(t["id"] for t in segunda)


def test_el_limite_no_puede_superar_el_tamano_comprometido_en_esc01(cliente, cab):
    """ESC-01 compromete la latencia hasta 200 tareas; el límite lo respeta."""
    proyecto_id = _proyecto_con_tareas(cliente, cab, n=1)
    r = cliente.get(
        f"/proyectos/{proyecto_id}/tareas?limite=500", headers=cab("ana")
    )
    assert r.status_code == 422


def test_filtrar_por_estado_y_por_responsable(cliente, cab):
    proyecto_id = _proyecto_con_tareas(cliente, cab, n=4)
    cabeceras = cab("ana")
    todas = cliente.get(f"/proyectos/{proyecto_id}/tareas", headers=cabeceras).json()

    cliente.put(
        f"/proyectos/{proyecto_id}/tareas/{todas[0]['id']}/estado",
        json={"estado": "en_progreso"},
        headers=cabeceras,
    )

    en_progreso = cliente.get(
        f"/proyectos/{proyecto_id}/tareas?estado=en_progreso", headers=cabeceras
    ).json()
    de_bruno = cliente.get(
        f"/proyectos/{proyecto_id}/tareas?responsable=bruno", headers=cabeceras
    ).json()

    assert [t["id"] for t in en_progreso] == [todas[0]["id"]]
    assert len(de_bruno) == 2
    assert all(t["responsable"] == "bruno" for t in de_bruno)


def test_el_progreso_resume_el_avance_del_proyecto(cliente, cab):
    proyecto_id = _proyecto_con_tareas(cliente, cab, n=4)
    cabeceras = cab("ana")
    tareas = cliente.get(f"/proyectos/{proyecto_id}/tareas", headers=cabeceras).json()

    # Una tarea llega hasta completada
    cliente.put(
        f"/proyectos/{proyecto_id}/tareas/{tareas[0]['id']}/estado",
        json={"estado": "en_progreso"},
        headers=cabeceras,
    )
    cliente.put(
        f"/proyectos/{proyecto_id}/tareas/{tareas[0]['id']}/estado",
        json={"estado": "completada"},
        headers=cabeceras,
    )

    progreso = cliente.get(f"/proyectos/{proyecto_id}/progreso", headers=cabeceras).json()

    assert progreso["total"] == 4
    assert progreso["por_estado"] == {"pendiente": 3, "completada": 1}
    assert progreso["sin_responsable"] == 2
    assert progreso["porcentaje_completado"] == 25.0


def test_el_progreso_cuenta_las_tareas_vencidas(cliente, cab):
    cabeceras = cab("ana")
    proyecto_id = cliente.post(
        "/proyectos", json={"nombre": "Arquitectura", "miembros": []}, headers=cabeceras
    ).json()["id"]

    ayer = (date.today() - timedelta(days=1)).isoformat()
    manana = (date.today() + timedelta(days=1)).isoformat()
    for titulo, limite in [("Vencida", ayer), ("A tiempo", manana), ("Sin fecha", None)]:
        cliente.post(
            f"/proyectos/{proyecto_id}/tareas",
            json={"titulo": titulo, "fecha_limite": limite},
            headers=cabeceras,
        )

    progreso = cliente.get(f"/proyectos/{proyecto_id}/progreso", headers=cabeceras).json()
    assert progreso["vencidas"] == 1
    assert progreso["total"] == 3


def test_el_progreso_de_un_proyecto_ajeno_devuelve_403(cliente, cab):
    proyecto_id = _proyecto_con_tareas(cliente, cab, n=2)
    r = cliente.get(
        f"/proyectos/{proyecto_id}/progreso", headers=cab("intruso")
    )
    assert r.status_code == 403


def test_el_progreso_de_un_proyecto_vacio_no_divide_por_cero(cliente, cab):
    proyecto_id = cliente.post(
        "/proyectos", json={"nombre": "Vacío", "miembros": []},
        headers=cab("ana"),
    ).json()["id"]
    progreso = cliente.get(
        f"/proyectos/{proyecto_id}/progreso", headers=cab("ana")
    ).json()
    assert progreso == {
        "total": 0,
        "por_estado": {},
        "sin_responsable": 0,
        "vencidas": 0,
        "porcentaje_completado": 0.0,
    }
