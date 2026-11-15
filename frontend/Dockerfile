FROM node:24-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
# npm ci when the lockfile is present; fall back to npm install for deploys without it
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY frontend/ ./
RUN npm run build

FROM node:24-alpine AS runtime
WORKDIR /app
# Amvera routes the project domain to container port 80; let USER node bind it
RUN apk add --no-cache libcap && setcap cap_net_bind_service=+ep /usr/local/bin/node
ENV NODE_ENV=production HOST=0.0.0.0 PORT=80
COPY --from=build --chown=node:node /app/.output/ ./.output/
USER node
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1:80/healthz || exit 1
CMD ["node", ".output/server/index.mjs"]
