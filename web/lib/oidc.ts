/**
 * Flujo de autorización OpenID Connect con PKCE.
 *
 * PKCE (RFC 7636) permite completar el intercambio sin secreto de cliente,
 * que es lo que corresponde a una aplicación que se ejecuta en el navegador:
 * cualquier secreto que se le entregara sería público.
 */

const EMISOR = (process.env.NEXT_PUBLIC_OIDC_EMISOR ?? "http://localhost:9000").replace(/\/$/, "");
const CLIENTE = process.env.NEXT_PUBLIC_OIDC_CLIENTE ?? "uniteam-web";

const CLAVE_TOKEN = "uniteam.token";
const CLAVE_VERIFICADOR = "uniteam.pkce";
const CLAVE_ESTADO = "uniteam.estado";

interface Descubrimiento {
  authorization_endpoint: string;
  token_endpoint: string;
}

let descubrimiento: Promise<Descubrimiento> | null = null;

function descubrir(): Promise<Descubrimiento> {
  descubrimiento ??= fetch(`${EMISOR}/.well-known/openid-configuration`)
    .then((r) => {
      if (!r.ok) throw new Error(`El emisor respondió ${r.status}`);
      return r.json();
    })
    .catch((e) => {
      descubrimiento = null;
      throw e;
    });
  return descubrimiento;
}

function aleatorio(bytes = 32): string {
  const datos = new Uint8Array(bytes);
  crypto.getRandomValues(datos);
  return base64url(datos);
}

function base64url(datos: Uint8Array | ArrayBuffer): string {
  const bytes = datos instanceof Uint8Array ? datos : new Uint8Array(datos);
  let texto = "";
  bytes.forEach((b) => (texto += String.fromCharCode(b)));
  return btoa(texto).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function reto(verificador: string): Promise<string> {
  const resumen = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(verificador),
  );
  return base64url(resumen);
}

export function redireccion(): string {
  return `${window.location.origin}/callback`;
}

/** Lleva al usuario al proveedor de identidad. */
export async function iniciarSesion(): Promise<void> {
  const { authorization_endpoint } = await descubrir();
  const verificador = aleatorio();
  const estado = aleatorio(16);
  sessionStorage.setItem(CLAVE_VERIFICADOR, verificador);
  sessionStorage.setItem(CLAVE_ESTADO, estado);

  const parametros = new URLSearchParams({
    response_type: "code",
    client_id: CLIENTE,
    redirect_uri: redireccion(),
    scope: "openid email profile",
    state: estado,
    code_challenge: await reto(verificador),
    code_challenge_method: "S256",
  });
  window.location.assign(`${authorization_endpoint}?${parametros}`);
}

/** Canjea el código por un token. Devuelve el token de acceso. */
export async function completarSesion(codigo: string, estado: string): Promise<string> {
  const esperado = sessionStorage.getItem(CLAVE_ESTADO);
  const verificador = sessionStorage.getItem(CLAVE_VERIFICADOR);
  sessionStorage.removeItem(CLAVE_ESTADO);
  sessionStorage.removeItem(CLAVE_VERIFICADOR);

  if (!esperado || esperado !== estado) {
    // Protege frente a un código inyectado por un tercero (CSRF).
    throw new Error("El estado de la sesión no coincide.");
  }
  if (!verificador) throw new Error("Falta el verificador PKCE.");

  const { token_endpoint } = await descubrir();
  const respuesta = await fetch(token_endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      code: codigo,
      redirect_uri: redireccion(),
      client_id: CLIENTE,
      code_verifier: verificador,
    }),
  });
  if (!respuesta.ok) throw new Error(`No se pudo canjear el código (${respuesta.status}).`);

  const datos = await respuesta.json();
  const token: string = datos.access_token ?? datos.id_token;
  if (!token) throw new Error("El emisor no devolvió ningún token.");
  guardarToken(token);
  return token;
}

export function guardarToken(token: string): void {
  // sessionStorage y no localStorage: el token se olvida al cerrar la pestaña.
  sessionStorage.setItem(CLAVE_TOKEN, token);
}

export function leerToken(): string | null {
  try {
    return sessionStorage.getItem(CLAVE_TOKEN);
  } catch {
    return null;
  }
}

export function cerrarSesion(): void {
  try {
    sessionStorage.removeItem(CLAVE_TOKEN);
  } catch {
    /* almacenamiento no disponible */
  }
}

/**
 * Identidad y caducidad que declara el token.
 *
 * Se lee sin verificar la firma **a propósito**: solo sirve para pintar la
 * interfaz. Quien verifica de verdad es la API, contra el JWKS del emisor.
 */
export function contenidoDelToken(
  token: string,
): { usuario: string; expira: number } | null {
  try {
    const carga = JSON.parse(
      atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")),
    );
    return {
      usuario: carga.email ?? carga.preferred_username ?? carga.sub ?? "usuario",
      expira: Number(carga.exp ?? 0) * 1000,
    };
  } catch {
    return null;
  }
}

export function caducado(token: string): boolean {
  const contenido = contenidoDelToken(token);
  return !contenido || contenido.expira <= Date.now();
}
