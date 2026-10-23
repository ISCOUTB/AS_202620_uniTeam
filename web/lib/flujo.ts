import type { EstadoFlujo } from "./api";

/**
 * Consultas sobre el flujo de estados que publica la API.
 *
 * La Aplicación Web no conoce ningún estado por su nombre: todo lo que sabe
 * —columnas, etiquetas, transiciones, cuál es el final— sale de aquí. Añadir un
 * estado en el dominio no exige tocar este contenedor (ESC-05, ADR 0012).
 */
export class Flujo {
  private readonly porId: Map<string, EstadoFlujo>;

  constructor(readonly estados: EstadoFlujo[]) {
    this.porId = new Map(estados.map((e) => [e.id, e]));
  }

  etiqueta(id: string): string {
    return this.porId.get(id)?.etiqueta ?? id;
  }

  siguientes(id: string): string[] {
    return this.porId.get(id)?.siguientes ?? [];
  }

  /** Posición de la columna: sirve para dibujar las flechas ← y →. */
  orden(id: string): number {
    return this.estados.findIndex((e) => e.id === id);
  }

  esFinal(id: string): boolean {
    return this.porId.get(id)?.final ?? false;
  }

  /** Clase CSS de la columna: el estado inicial y el final tienen color propio. */
  tipo(id: string): "inicial" | "final" | "intermedio" {
    const e = this.porId.get(id);
    if (e?.inicial) return "inicial";
    if (e?.final) return "final";
    return "intermedio";
  }

  get final(): EstadoFlujo | undefined {
    return this.estados.find((e) => e.final);
  }

  /** Estados en curso: ni el inicial ni el final. */
  get enCurso(): EstadoFlujo[] {
    return this.estados.filter((e) => !e.inicial && !e.final);
  }
}
