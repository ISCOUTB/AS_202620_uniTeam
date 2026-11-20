"use client";

import { useSesion } from "@/lib/sesion";
import { AnilloProgreso } from "./anillo-progreso";
import { Avatar } from "./avatar";
import { IconoCheck, IconoFlechaDerecha } from "./iconos";

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
          <span className="portada-etiqueta">
            <span aria-hidden="true" /> Organización para equipos universitarios
          </span>
          <h1>
            Organiza el trabajo de tu equipo <em>universitario</em>
          </h1>
          <p className="portada-entrada">
            UniTeam reúne en un solo sitio qué hay que hacer, quién se encarga, qué es urgente y cómo va el
            proyecto. Sin hilos de chat interminables ni hojas de cálculo desactualizadas.
          </p>
          <div className="portada-acciones">
            <button className="grande" onClick={() => void entrar()}>
              Empezar con tu cuenta
              <IconoFlechaDerecha tamano={19} />
            </button>
          </div>
          <p className="nota">Entra con Google o con tu correo. UniTeam no guarda contraseñas.</p>
        </div>

        <div
          className="portada-ilustracion"
          role="img"
          aria-label="Vista ilustrada de un tablero de tareas organizado por columnas, con avance del proyecto y el equipo asignado"
        >
          <div className="ilustracion-resplandor" aria-hidden="true" />
          <div className="ilustracion-orbita" aria-hidden="true" />
          <div className="ilustracion-lienzo" aria-hidden="true">
            <div className="ilustracion-tablero">
              <div className="ilustracion-barra">
                <i />
                <i />
                <i />
                <span className="ilustracion-barra-titulo" />
              </div>
              <div className="ilustracion-columnas">
                <div className="ilustracion-columna">
                  <span className="ilustracion-columna-titulo">Por hacer</span>
                  <div className="ilustracion-tarea alta">
                    <b />
                    <span />
                    <span />
                  </div>
                  <div className="ilustracion-tarea">
                    <b />
                    <span />
                  </div>
                </div>
                <div className="ilustracion-columna">
                  <span className="ilustracion-columna-titulo">En curso</span>
                  <div className="ilustracion-tarea media">
                    <b />
                    <span />
                    <span />
                  </div>
                </div>
                <div className="ilustracion-columna">
                  <span className="ilustracion-columna-titulo">Hecho</span>
                  <div className="ilustracion-tarea baja hecha">
                    <b />
                    <span />
                  </div>
                </div>
              </div>
            </div>

            <div className="ilustracion-flotante ilustracion-progreso">
              <AnilloProgreso porcentaje={68} tamano={46} />
              <span>
                <b>68%</b>
                <small>del proyecto</small>
              </span>
            </div>

            <div className="ilustracion-flotante ilustracion-equipo">
              <Avatar usuario="ana.perez@utb.edu.co" tamano={24} />
              <Avatar usuario="bruno.diaz@utb.edu.co" tamano={24} />
              <Avatar usuario="carla.ruiz@utb.edu.co" tamano={24} />
              <small>+3</small>
            </div>

            <div className="ilustracion-flotante ilustracion-listo">
              <IconoCheck tamano={15} />
              <span>Tarea terminada</span>
            </div>
          </div>
        </div>
      </section>

      <section className="portada-ventajas" aria-label="Qué ofrece UniTeam">
        {VENTAJAS.map((v, i) => (
          <article key={v.titulo} className="tarjeta ventaja">
            <span className="ventaja-numero" aria-hidden="true">
              {String(i + 1).padStart(2, "0")}
            </span>
            <h2>{v.titulo}</h2>
            <p>{v.texto}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
