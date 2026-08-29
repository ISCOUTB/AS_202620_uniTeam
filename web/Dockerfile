FROM node:22-alpine AS constructor
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci || npm install
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
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
