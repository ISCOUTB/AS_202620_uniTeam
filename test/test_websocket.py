#Autenticación, autorización y notificación confirmada por WebSocket.
import pytest
from starlette.websockets import WebSocketDisconnect


def _crear_proyecto(cliente, cab, lider="ana"):
    respuesta = cliente.post(
        "/proyectos",
        json={"nombre": "Proyecto en tiempo real", "miembros": ["bruno"]},
        headers=cab(lider),
    )
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def _autenticar(socket, usuario, cab):
    token = cab(usuario)["Authorization"].split(" ", 1)[1]
    socket.send_json({"tipo": "autenticar", "token": token})
    return socket.receive_json()


def test_websocket_rechaza_credencial_invalida(cliente, cab):
    proyecto_id = _crear_proyecto(cliente, cab)

    with cliente.websocket_connect(
        f"/proyectos/{proyecto_id}/eventos",
        headers={"origin": "http://localhost:3000"},
    ) as socket:
        with pytest.raises(WebSocketDisconnect) as desconexion:
            socket.send_json({"tipo": "autenticar", "token": "token-invalido"})
            socket.receive_json()

    assert desconexion.value.code == 4401


def test_websocket_rechaza_origen_no_permitido(cliente):
    with pytest.raises(WebSocketDisconnect) as desconexion:
        with cliente.websocket_connect(
            "/proyectos/no-importa/eventos",
            headers={"origin": "https://sitio-ajeno.example"},
        ) as socket:
            socket.receive_json()

    assert desconexion.value.code == 4403


def test_websocket_rechaza_y_audita_usuario_ajeno(cliente, cab, sesion):
    proyecto_id = _crear_proyecto(cliente, cab)

    with pytest.raises(WebSocketDisconnect) as desconexion:
        with cliente.websocket_connect(
            f"/proyectos/{proyecto_id}/eventos",
            headers={"origin": "http://localhost:3000"},
        ) as socket:
            _autenticar(socket, "intruso", cab)

    assert desconexion.value.code == 4403
    sesion.rollback()
    from app.infrastructure.tablas import AuditoriaTabla

    registros = (
        sesion.query(AuditoriaTabla)
        .filter_by(
            usuario="intruso",
            recurso=f"proyecto:{proyecto_id}",
            operacion="conectar_websocket",
            resultado="denegado",
        )
        .all()
    )
    assert len(registros) == 1


def test_websocket_notifica_cambios_solo_despues_del_commit(cliente, cab, sesion):
    proyecto_id = _crear_proyecto(cliente, cab)

    with cliente.websocket_connect(
        f"/proyectos/{proyecto_id}/eventos",
        headers={"origin": "http://localhost:3000"},
    ) as socket:
        assert _autenticar(socket, "bruno", cab) == {"tipo": "conectado"}
        respuesta = cliente.post(
            f"/proyectos/{proyecto_id}/tareas",
            json={"titulo": "Tarea en tiempo real"},
            headers=cab("ana"),
        )

        assert respuesta.status_code == 201
        notificacion = socket.receive_json()
        assert notificacion == {
            "tipo": "tareas_actualizadas",
            "proyecto_id": proyecto_id,
        }
        sesion.rollback()
        from app.infrastructure.tablas import TareaTabla

        assert sesion.get(TareaTabla, respuesta.json()["id"]) is not None
