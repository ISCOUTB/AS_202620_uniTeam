"use client";

import { useSesion } from "@/lib/sesion";

const VENTAJAS = [
  {
    titulo: "Todo el trabajo en un tablero",
    texto: "Cada tarea en la columna de su estado: el equipo ve de un vistazo en qué punto está el trabajo.",
  },
  {
    titulo: "Cada tarea tiene responsable",
    texto: "Asigna, prioriza y pon fecha límite. UniTeam avisa de lo que vence hoy y de lo que ya venció.",
  },
  {
    titulo: "Solo tu equipo ve tu proyecto",
    texto: "Nadie ajeno accede a vuestras tareas, y cada intento queda registrado. Entras con tu cuenta, sin contraseñas nuevas.",
  },
];

/** Lo primero que ve quien no ha iniciado sesión. */
export function Portada() {
  const { entrar, motivoCierre } = useSesion();
  return (
    <div className="portada">
      {motivoCierre && <div className="aviso">{motivoCierre}</div>}
      <section className="portada-heroe">
        <div className="portada-copia">
          <span className="portada-etiqueta"><span /> Organización para equipos universitarios</span>
          <h1>Organiza el trabajo de tu equipo <span>universitario</span></h1>
          <p>
            UniTeam reúne en un solo sitio qué hay que hacer, quién se encarga, qué es urgente y cómo va el
            proyecto. Sin hilos de chat interminables ni hojas de cálculo desactualizadas.
          </p>
          <button className="grande" onClick={() => void entrar()}>
            Empezar con tu cuenta <span aria-hidden="true">→</span>
          </button>
          <p className="nota">Entra con Google o con tu correo. UniTeam no guarda contraseñas.</p>
        </div>
        <div className="portada-ilustracion" role="img" aria-label="Vista ilustrada de un tablero de tareas organizado">
          <div className="ilustracion-resplandor" />
          <div className="ilustracion-orbita" />
          <div className="ilustracion-tablero">
            <div className="ilustracion-barra"><i /><i /><i /></div>
            <div className="ilustracion-tareas">
              <div><span>✓</span><i /></div>
              <div><span>✓</span><i /></div>
              <div><span>✓</span><i /></div>
            </div>
          </div>
          <span className="ilustracion-flotante ilustracion-logo" aria-hidden="true">U</span>
          <span className="ilustracion-flotante ilustracion-equipo" aria-hidden="true">♧</span>
          <span className="ilustracion-flotante ilustracion-listo" aria-hidden="true">✓</span>
        </div>
      </section>
      <section className="portada-ventajas">
        {VENTAJAS.map((v) => (
          <article key={v.titulo} className="tarjeta">
            <h3>{v.titulo}</h3>
            <p>{v.texto}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
