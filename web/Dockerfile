# Imagen de producción del sitio estático Next.js.
# output: export genera ficheros y nginx los sirve; no se necesita next start.
FROM node:22.14.0-alpine3.21 AS dependencies

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts


FROM node:22.14.0-alpine3.21 AS builder

WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .

ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_OIDC_EMISOR
ARG NEXT_PUBLIC_OIDC_CLIENTE
ARG NEXT_PUBLIC_OIDC_AUDIENCIA
ARG NEXT_PUBLIC_OIDC_CLAIM_USUARIO
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_OIDC_EMISOR=$NEXT_PUBLIC_OIDC_EMISOR \
    NEXT_PUBLIC_OIDC_CLIENTE=$NEXT_PUBLIC_OIDC_CLIENTE \
    NEXT_PUBLIC_OIDC_AUDIENCIA=$NEXT_PUBLIC_OIDC_AUDIENCIA \
    NEXT_PUBLIC_OIDC_CLAIM_USUARIO=$NEXT_PUBLIC_OIDC_CLAIM_USUARIO

RUN npm run build


FROM nginx:1.27.4-alpine3.21 AS runtime

ENV PORT=3000
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=builder /app/out /usr/share/nginx/html
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -q -O /dev/null "http://127.0.0.1:${PORT}/" || exit 1
