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
ENV NEXT_TELEMETRY_DISABLED=1 \
    NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_OIDC_EMISOR=$NEXT_PUBLIC_OIDC_EMISOR \
    NEXT_PUBLIC_OIDC_CLIENTE=$NEXT_PUBLIC_OIDC_CLIENTE
RUN npm run build

FROM node:22-alpine AS ejecucion
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000
COPY --from=constructor /app/package.json /app/package-lock.json* ./
COPY --from=constructor /app/node_modules ./node_modules
COPY --from=constructor /app/.next ./.next
COPY --from=constructor /app/public ./public
COPY --from=constructor /app/next.config.mjs ./
EXPOSE 3000
CMD ["npm", "start"]
