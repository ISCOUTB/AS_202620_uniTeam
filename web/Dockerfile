# Aplicación Web de UniTeam como sitio estático.
#
# Next.js compila a ficheros (`out/`) y un nginx mínimo los sirve. En el
# despliegue no se usa esta imagen: Render sirve `out/` desde su CDN como
# sitio estático (render.yaml). Esta imagen es la del arranque local con
# `docker compose up`, para que ambos sirvan exactamente la misma compilación.
FROM node:22-alpine AS constructor
WORKDIR /app
COPY package.json package-lock.json ./
# `npm ci` instala exactamente lo que fija package-lock.json, y falla si el
# manifiesto y el cierre no concuerdan; --ignore-scripts evita ejecutar los
# scripts de instalación de las dependencias al construir la imagen.
RUN npm ci --ignore-scripts
COPY . .
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_OIDC_EMISOR=http://localhost:9000
ARG NEXT_PUBLIC_OIDC_CLIENTE=uniteam-web
ARG NEXT_PUBLIC_OIDC_AUDIENCIA=
ARG NEXT_PUBLIC_OIDC_CLAIM_USUARIO=email
ENV NEXT_TELEMETRY_DISABLED=1 \
    NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_OIDC_EMISOR=$NEXT_PUBLIC_OIDC_EMISOR \
    NEXT_PUBLIC_OIDC_CLIENTE=$NEXT_PUBLIC_OIDC_CLIENTE \
    NEXT_PUBLIC_OIDC_AUDIENCIA=$NEXT_PUBLIC_OIDC_AUDIENCIA \
    NEXT_PUBLIC_OIDC_CLAIM_USUARIO=$NEXT_PUBLIC_OIDC_CLAIM_USUARIO
RUN npm run build

FROM nginx:1.27-alpine AS ejecucion
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=constructor /app/out /usr/share/nginx/html
EXPOSE 3000
