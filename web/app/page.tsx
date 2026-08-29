"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api, ErrorApi, type Proyecto } from "@/lib/api";
import { useUsuario } from "@/lib/usuario";

export default function PaginaProyectos() {
  const { usuario, cargado } = useUsuario();
  const [proyectos, establecerProyectos] = useState<Proyecto[]>([]);
  const [error, establecerError] = useState<string | null>(null);
  const [cargando, establecerCargando] = useState(false);
  const [nombre, establecerNombre] = useState("");
  const [miembros, establecerMiembros] = useState("");

  const recargar = useCallback(async () => {
    if (!usuario) return;
    establecerCargando(true);
    try {
      establecerProyectos(await api.listarProyectos(usuario));
      establecerError(null);
    } catch (e) {
      establecerError(
        e instanceof ErrorApi ? e.message : "No se pudo contactar con la API.",
      );
    } finally {
      establecerCargando(false);
    }
  }, [usuario]);

  useEffect(() => {
    void recargar();
  }, [recargar]);

  async function crear(evento: React.FormEvent) {
    evento.preventDefault();
    if (!usuario || !nombre.trim()) return;
    const lista = miembros
      .split(",")
      .map((m) => m.trim())
      .filter(Boolean);
    try {
      await api.crearProyecto(usuario, nombre.trim(), lista);
      establecerNombre("");
      establecerMiembros("");
      await recargar();
    } catch (e) {
      establecerError(
        e instanceof ErrorApi ? e.message : "No se pudo crear el proyecto.",
      );
    }
  }

  if (!cargado) return null;

  if (!usuario) {
    return (
      <>
        <h1>Tus proyectos</h1>
        <p className="subtitulo">
          Indica tu usuario en la barra superior para empezar.
        </p>
        <div className="aviso">
          La identidad es provisional mientras no se integra el proveedor de
          identidad: se escribe a mano y viaja en la cabecera <code>X-Usuario</code>.
          El control de acceso sí es real y lo aplica el backend.
        </div>
      </>
    );
  }

  return (
    <>
      <h1>Tus proyectos</h1>
      <p className="subtitulo">
        Solo aparecen los proyectos de los que eres miembro.
      </p>

      {error && <div className="aviso error">{error}</div>}

      <section className="tarjeta" style={{ marginBottom: 24 }}>
        <form onSubmit={crear}>
          <div className="fila">
            <div style={{ flex: "2 1 220px" }}>
              <label className="etiqueta" htmlFor="nombre">
                Nombre del proyecto
              </label>
              <input
                id="nombre"
                value={nombre}
                onChange={(e) => establecerNombre(e.target.value)}
                placeholder="Proyecto de Arquitectura"
                style={{ width: "100%" }}
                required
              />
            </div>
            <div style={{ flex: "2 1 220px" }}>
              <label className="etiqueta" htmlFor="miembros">
                Integrantes, separados por comas
              </label>
              <input
                id="miembros"
                value={miembros}
                onChange={(e) => establecerMiembros(e.target.value)}
                placeholder="bruno, carla"
                style={{ width: "100%" }}
              />
            </div>
            <button type="submit" style={{ alignSelf: "flex-end" }}>
              Crear proyecto
            </button>
          </div>
        </form>
      </section>

      {cargando && proyectos.length === 0 ? (
        <p className="vacio">Cargando…</p>
      ) : proyectos.length === 0 ? (
        <p className="vacio">
          Todavía no perteneces a ningún proyecto. Crea el primero arriba.
        </p>
      ) : (
        <div className="rejilla rejilla-proyectos">
          {proyectos.map((p) => (
            <Link key={p.id} href={`/proyectos/${p.id}`} className="tarjeta">
              <strong>{p.nombre}</strong>
              <div className="fila" style={{ marginTop: 10 }}>
                {p.miembros.map((m) => (
                  <span key={m.usuario} className="pastilla">
                    {m.usuario}
                    {m.rol === "lider" ? " · líder" : ""}
                  </span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
