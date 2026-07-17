FROM node:22-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
# `npm ci` is stricter but fails here: this lockfile was generated on Windows,
# and its optional-dependency entries (native bindings Tailwind v4's
# lightningcss pulls in) don't cover the linux/x64 target this image builds
# for. `npm install` resolves those platform-specific packages fresh instead
# of demanding an exact lockfile match.
RUN npm install --no-audit --no-fund

FROM node:22-slim AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:22-slim AS runtime
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# The node:22-slim base image already ships a non-root `node` user (uid
# 1000) — reuse it instead of creating another, which would collide.
# Next.js standalone output: a self-contained server plus only the node_modules it needs.
COPY --from=build /app/public ./public
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static

USER node

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
