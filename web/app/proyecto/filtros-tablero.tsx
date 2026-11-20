import {
  ETIQUETA_PRIORIDAD,
  PRIORIDADES,
  type Miembro,
  type Prioridad,
} from "@/lib/api";
import { nombreCorto } from "@/lib/formato";
import { IconoBuscar, IconoFiltro } from "../componentes/iconos";

interface Props {
  texto: string;
  alCambiarTexto: (valor: string) => void;
  responsable: string;
  alCambiarResponsable: (valor: string) => void;
  prioridad: Prioridad | "";
  alCambiarPrioridad: (valor: Prioridad | "") => void;
  miembros: Miembro[];
  usuario: string | null;
  filtrando: boolean;
  alLimpiar: () => void;
  refBusqueda: React.Ref<HTMLInputElement>;
}

/**
 * Barra de filtros del tablero. Filtra en el navegador sobre las tareas ya
 * cargadas: la API no se vuelve a consultar al escribir.
 */
export function FiltrosTablero({
  texto,
  alCambiarTexto,
  responsable,
  alCambiarResponsable,
  prioridad,
  alCambiarPrioridad,
  miembros,
  usuario,
  filtrando,
  alLimpiar,
  refBusqueda,
}: Props) {
  return (
    <div className="filtros">
      <div className="campo-busqueda">
        <IconoBuscar tamano={18} />
        <input
          ref={refBusqueda}
          type="search"
          value={texto}
          onChange={(e) => alCambiarTexto(e.target.value)}
          placeholder="Buscar tareas…  ( / )"
          aria-label="Buscar tareas por título"
        />
      </div>

      <div className="filtros-selectores">
        <label className="filtro">
          <IconoFiltro tamano={16} />
          <span className="solo-lectores">Filtrar por responsable</span>
          <select
            value={responsable}
            onChange={(e) => alCambiarResponsable(e.target.value)}
            aria-label="Filtrar por responsable"
          >
            <option value="">Todos los responsables</option>
            <option value="-">Sin asignar</option>
            {usuario && miembros.some((m) => m.usuario === usuario) && (
              <option value={usuario}>Mis tareas</option>
            )}
            {miembros
              .filter((m) => m.usuario !== usuario)
              .map((m) => (
                <option key={m.usuario} value={m.usuario}>
                  {nombreCorto(m.usuario)}
                </option>
              ))}
          </select>
        </label>

        <label className="filtro">
          <span className="solo-lectores">Filtrar por prioridad</span>
          <select
            value={prioridad}
            onChange={(e) => alCambiarPrioridad(e.target.value as Prioridad | "")}
            aria-label="Filtrar por prioridad"
          >
            <option value="">Todas las prioridades</option>
            {PRIORIDADES.map((p) => (
              <option key={p} value={p}>
                {ETIQUETA_PRIORIDAD[p]}
              </option>
            ))}
          </select>
        </label>

        {filtrando && (
          <button className="enlace" onClick={alLimpiar}>
            Quitar filtros
          </button>
        )}
      </div>
    </div>
  );
}
