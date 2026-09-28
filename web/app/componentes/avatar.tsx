import { iniciales, tono } from "@/lib/formato";

/** Iniciales sobre un color estable por persona. El correo completo, en el título. */
export function Avatar({ usuario, tamano = 28 }: { usuario: string; tamano?: number }) {
  return (
    <span
      className="avatar"
      title={usuario}
      style={{
        width: tamano,
        height: tamano,
        fontSize: tamano * 0.4,
        background: `hsl(${tono(usuario)} 55% 45%)`,
      }}
    >
      {iniciales(usuario)}
    </span>
  );
}

/** Varios avatares solapados, con «+N» si no caben. */
export function GrupoAvatares({ usuarios, maximo = 5 }: { usuarios: string[]; maximo?: number }) {
  const visibles = usuarios.slice(0, maximo);
  const resto = usuarios.length - visibles.length;
  return (
    <span className="grupo-avatares">
      {visibles.map((u) => (
        <Avatar key={u} usuario={u} tamano={26} />
      ))}
      {resto > 0 && <span className="avatar avatar-resto">+{resto}</span>}
    </span>
  );
}
