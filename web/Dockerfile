FROM node:22-alpine AS constructor
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci || npm install
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
