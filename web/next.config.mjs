/**
 * El sitio se exporta como ficheros estáticos (`out/`): no hay servidor de
 * Next.js en ejecución. Todo el trabajo lo hace el navegador contra la API,
 * así que el sitio puede servirse desde un CDN, sin arranque en frío ni horas
 * de instancia (ADR 0007).
 *
 * `trailingSlash` genera `callback/index.html` en lugar de `callback.html`,
 * que cualquier servidor estático sirve sin reglas de reescritura.
 *
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  reactStrictMode: true,
  output: "export",
  trailingSlash: true,
};

export default nextConfig;
