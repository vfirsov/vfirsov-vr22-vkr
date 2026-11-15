FROM node:24-alpine AS build

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM nginx:1.28-alpine AS runtime

RUN apk add --no-cache ca-certificates \
    && mkdir -p /etc/nginx/snippets
COPY frontend/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY frontend/docker-entrypoint.d/40-configure-api.sh /docker-entrypoint.d/40-configure-api.sh
RUN chmod 755 /docker-entrypoint.d/40-configure-api.sh
COPY --from=build /app/dist/ /usr/share/nginx/html/

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1/healthz || exit 1

