"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ErrorApi, type ProyectoConResumen } from "@/lib/api";
import { useAvisos } from "@/lib/avisos";
import { pareceCorreo, useLento } from "@/lib/lento";
import { useSesion } from "@/lib/sesion";
import { EstadoVacio } from "./componentes/estado-vacio";
import { IconoMas, IconoUsuarios } from "./componentes/iconos";
import { Portada } from "./componentes/portada";
import { TarjetaProyecto } from "./componentes/tarjeta-proyecto";

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
  const campoNombre = useRef<HTMLInputElement>(null);
  const botonNuevo = useRef<HTMLButtonElement>(null);
  const [nombre, establecerNombre] = useState("");
  const [miembros, establecerMiembros] = useState("");
  const lento = useLento(token !== null && proyectos === null && !error);

  useEffect(() => {
    if (formularioAbierto) campoNombre.current?.focus();
  }, [formularioAbierto]);

  /** Cierra el alta y devuelve el foco al botón que la abrió. */
  function cerrarFormulario() {
    establecerFormulario(false);
    window.requestAnimationFrame(() => botonNuevo.current?.focus());
  }

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
          <p className="ceja">Panel</p>
          <h1>Mis proyectos</h1>
          <p className="subtitulo">Solo ves los proyectos de los que eres miembro.</p>
        </div>
        {!formularioAbierto && (
          <button ref={botonNuevo} onClick={() => establecerFormulario(true)}>
            <IconoMas tamano={18} />
            Nuevo proyecto
          </button>
        )}
      </div>

      {error && (
        <div className="aviso error" role="alert">
          {error}
        </div>
      )}

      {formularioAbierto && (
        <section className="tarjeta formulario" aria-label="Nuevo proyecto">
          <form onSubmit={crear}>
            <h2>Nuevo proyecto</h2>
            <p className="ayuda">Ponle nombre y añade a tu equipo por correo. Tú quedas como líder.</p>
            <div className="campos">
              <label className="campo">
                <span className="etiqueta">Nombre</span>
                <input
                  ref={campoNombre}
                  value={nombre}
                  onChange={(e) => establecerNombre(e.target.value)}
                  placeholder="Proyecto de Arquitectura"
                  maxLength={200}
                  required
                />
              </label>
              <label className="campo ancho">
                <span className="etiqueta">
                  <IconoUsuarios tamano={15} /> Integrantes (correos, separados por comas)
                </span>
                <input
                  value={miembros}
                  onChange={(e) => establecerMiembros(e.target.value)}
                  placeholder="bruno@utb.edu.co, carla@utb.edu.co"
                  inputMode="email"
                  autoComplete="off"
                  spellCheck={false}
                  aria-invalid={invalidos.length > 0}
                  aria-describedby={invalidos.length > 0 ? "error-integrantes" : "ayuda-integrantes"}
                />
                {invalidos.length > 0 ? (
                  <span className="ayuda error" id="error-integrantes">
                    No parece un correo: {invalidos.join(", ")}. Los integrantes entran con su correo.
                  </span>
                ) : (
                  <span className="ayuda" id="ayuda-integrantes">
                    Puedes añadir más integrantes después.
                  </span>
                )}
              </label>
            </div>
            <div className="acciones">
              <button type="button" className="secundario" onClick={cerrarFormulario}>
                Cancelar
              </button>
              <button type="submit" disabled={creando || !nombre.trim() || invalidos.length > 0}>
                {creando ? "Creando…" : "Crear proyecto"}
              </button>
            </div>
          </form>
        </section>
      )}

      {proyectos === null && !error && (
        <>
          <div className="rejilla rejilla-proyectos" aria-hidden="true">
            {[0, 1, 2].map((i) => (
              <div key={i} className="tarjeta esqueleto" style={{ height: 148 }} />
            ))}
          </div>
          {lento && (
            <p className="vacio">El servidor está despertando; la primera carga del día tarda un poco más.</p>
          )}
        </>
      )}

      {proyectos?.length === 0 && (
        <EstadoVacio
          titulo="Todavía no tienes proyectos"
          ilustracion="proyecto"
          accion={
            !formularioAbierto && (
              <button onClick={() => establecerFormulario(true)}>
                <IconoMas tamano={18} />
                Crear mi primer proyecto
              </button>
            )
          }
        >
          Crea el primero e invita a tu equipo con su correo.
        </EstadoVacio>
      )}

      {proyectos && proyectos.length > 0 && (
        <div className="rejilla rejilla-proyectos">
          {proyectos.map((p) => (
            <TarjetaProyecto key={p.id} proyecto={p} usuario={usuario} />
          ))}
        </div>
      )}
    </>
  );
}
