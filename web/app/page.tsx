"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, ErrorApi, type ProyectoConResumen } from "@/lib/api";
import { useAvisos } from "@/lib/avisos";
import { pareceCorreo, useLento } from "@/lib/lento";
import { useSesion } from "@/lib/sesion";
import { GrupoAvatares } from "./componentes/avatar";
import { Portada } from "./componentes/portada";

function mensaje(e: unknown, porDefecto: string): string {
  return e instanceof ErrorApi ? e.message : porDefecto;
}

export default function PaginaProyectos() {
  const { token, usuario, cargado } = useSesion();
  const { avisar } = useAvisos();
  const router = useRouter();

  const [proyectos, establecerProyectos] = useState<ProyectoConResumen[] | null>(null);
  const [error, establecerError] = useState<string | null>(null);
  const [creando, establecerCreando] = useState(false);
  const [formularioAbierto, establecerFormulario] = useState(false);
  const [nombre, establecerNombre] = useState("");
  const [miembros, establecerMiembros] = useState("");
  const lento = useLento(token !== null && proyectos === null && !error);

  useEffect(() => {
    document.title = "Mis proyectos · UniTeam";
  }, []);

  const recargar = useCallback(async () => {
    if (!token) return;
    try {
      establecerProyectos(await api.listarProyectos(token));
      establecerError(null);
    } catch (e) {
      establecerError(mensaje(e, "No se pudo contactar con la API."));
    }
  }, [token]);

  useEffect(() => {
    void recargar();
  }, [recargar]);

  const lista = miembros
    .split(/[,;\s]+/)
    .map((m) => m.trim().toLowerCase())
    .filter(Boolean);
  const invalidos = lista.filter((m) => !pareceCorreo(m));

  async function crear(evento: React.FormEvent) {
    evento.preventDefault();
    if (!token || !nombre.trim() || invalidos.length > 0 || creando) return;
    establecerCreando(true);
    try {
      const { id } = await api.crearProyecto(token, nombre.trim(), lista);
      avisar(`Proyecto «${nombre.trim()}» creado.`);
      router.push(`/proyecto/?id=${encodeURIComponent(id)}`);
    } catch (e) {
      avisar(mensaje(e, "No se pudo crear el proyecto."), "error");
      establecerCreando(false);
    }
  }

  if (!cargado) return null;
  if (!token) return <Portada />;

  return (
    <>
      <div className="encabezado-pagina">
        <div>
          <h1>Mis proyectos</h1>
          <p className="subtitulo">Solo ves los proyectos de los que eres miembro.</p>
        </div>
        {!formularioAbierto && (
          <button onClick={() => establecerFormulario(true)}>+ Nuevo proyecto</button>
        )}
      </div>

      {error && <div className="aviso error">{error}</div>}

      {formularioAbierto && (
        <section className="tarjeta formulario">
          <form onSubmit={crear}>
            <h2>Nuevo proyecto</h2>
            <div className="campos">
              <label className="campo">
                <span className="etiqueta">Nombre</span>
                <input
                  value={nombre}
                  onChange={(e) => establecerNombre(e.target.value)}
                  placeholder="Proyecto de Arquitectura"
                  maxLength={200}
                  autoFocus
                  required
                />
              </label>
              <label className="campo ancho">
                <span className="etiqueta">Integrantes (correos, separados por comas)</span>
                <input
                  value={miembros}
                  onChange={(e) => establecerMiembros(e.target.value)}
                  placeholder="bruno@utb.edu.co, carla@utb.edu.co"
                  aria-invalid={invalidos.length > 0}
                />
                {invalidos.length > 0 ? (
                  <span className="ayuda error">
                    No parece un correo: {invalidos.join(", ")}. Los integrantes entran con su correo.
                  </span>
                ) : (
                  <span className="ayuda">Tú quedas como líder. Puedes añadir más integrantes después.</span>
                )}
              </label>
            </div>
            <div className="acciones">
              <button type="button" className="secundario" onClick={() => establecerFormulario(false)}>
                Cancelar
              </button>
              <button type="submit" disabled={creando || !nombre.trim() || invalidos.length > 0}>
                {creando ? "Creando…" : "Crear proyecto"}
              </button>
            </div>
          </form>
        </section>
      )}

      {proyectos === null && !error ? (
        <>
          <div className="rejilla rejilla-proyectos">
            {[0, 1, 2].map((i) => (
              <div key={i} className="tarjeta esqueleto" style={{ height: 112 }} />
            ))}
          </div>
          {lento && (
            <p className="vacio">El servidor está despertando; la primera carga del día tarda un poco más.</p>
          )}
        </>
      ) : proyectos && proyectos.length === 0 ? (
        <div className="vacio-grande">
          <h2>Todavía no tienes proyectos</h2>
          <p>Crea el primero e invita a tu equipo con su correo.</p>
          {!formularioAbierto && (
            <button onClick={() => establecerFormulario(true)}>Crear mi primer proyecto</button>
          )}
        </div>
      ) : (
        <div className="rejilla rejilla-proyectos">
          {proyectos?.map((p) => {
            const lider = p.miembros.find((m) => m.rol === "lider")?.usuario === usuario;
            return (
              <Link
                key={p.id}
                href={`/proyecto/?id=${encodeURIComponent(p.id)}`}
                className="tarjeta tarjeta-proyecto"
              >
                <div className="fila separado">
                  <strong className="titulo-proyecto">{p.nombre}</strong>
                  {lider && <span className="insignia">Líder</span>}
                </div>
                <div className="avance-proyecto">
                  <div className="fila separado suave">
                    <span>
                      {p.resumen.total === 0
                        ? "Sin tareas todavía"
                        : `${p.resumen.terminadas} de ${p.resumen.total} tareas terminadas`}
                    </span>
                    {p.resumen.vencidas > 0 && (
                      <span className="vencidas-proyecto">
                        {p.resumen.vencidas} vencida{p.resumen.vencidas === 1 ? "" : "s"}
                      </span>
                    )}
                  </div>
                  <div className="barra fina">
                    <div
                      style={{
                        width: `${p.resumen.total ? (p.resumen.terminadas * 100) / p.resumen.total : 0}%`,
                      }}
                    />
                  </div>
                </div>
                <div className="fila separado pie-tarjeta">
                  <GrupoAvatares usuarios={p.miembros.map((m) => m.usuario)} />
                  <span className="suave">
                    {p.miembros.length} integrante{p.miembros.length === 1 ? "" : "s"}
                  </span>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </>
  );
}
