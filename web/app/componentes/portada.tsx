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
        <h1>Organiza el trabajo de tu equipo universitario</h1>
        <p>
          UniTeam reúne en un solo sitio qué hay que hacer, quién se encarga, qué es urgente y cómo va el
          proyecto. Sin hilos de chat interminables ni hojas de cálculo desactualizadas.
        </p>
        <button className="grande" onClick={() => void entrar()}>
          Empezar con tu cuenta
        </button>
        <p className="nota">Entra con Google o con tu correo. UniTeam no guarda contraseñas.</p>
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
