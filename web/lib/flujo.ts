import type { EstadoFlujo, EstadoTarea } from "./api";

/**
 * Consultas sobre el flujo de estados que publica la API.
 *
 * La Aplicación Web no conoce ningún estado por su nombre: todo lo que sabe
 * —columnas, etiquetas, transiciones, cuál es el final— sale de aquí. Añadir un
 * estado en el dominio no exige tocar este contenedor (ESC-05, ADR 0012).
 */
export class Flujo {
  private readonly porId: Map<EstadoTarea, EstadoFlujo>;

  constructor(readonly estados: EstadoFlujo[]) {
    this.porId = new Map(estados.map((e) => [e.id, e]));
  }

  etiqueta(id: EstadoTarea): string {
    return this.porId.get(id)?.etiqueta ?? id;
  }

  siguientes(id: EstadoTarea): EstadoTarea[] {
    return this.porId.get(id)?.siguientes ?? [];
  }

  /** Posición de la columna: sirve para dibujar las flechas ← y →. */
  orden(id: EstadoTarea): number {
    return this.estados.findIndex((e) => e.id === id);
  }

  esFinal(id: EstadoTarea): boolean {
    return this.porId.get(id)?.final ?? false;
  }

  /** Clase CSS de la columna: el estado inicial y el final tienen color propio. */
  tipo(id: EstadoTarea): "inicial" | "final" | "intermedio" {
    const e = this.porId.get(id);
    return e?.inicial ? "inicial" : e?.final ? "final" : "intermedio";
  }

  get final(): EstadoFlujo | undefined {
    return this.estados.find((e) => e.final);
  }

  /** Estados en curso: ni el inicial ni el final. */
  get enCurso(): EstadoFlujo[] {
    return this.estados.filter((e) => !e.inicial && !e.final);
  }
}
