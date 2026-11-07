# Railway image for the Perpustakaan Hati storefront (Next.js standalone).
FROM node:22-bookworm-slim AS deps
WORKDIR /app
# Toolchain only as a fallback if no prebuilt better-sqlite3 binary matches.
RUN apt-get update && apt-get install -y --no-install-recommends python3 make g++ \
    && apt-get clean
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-bookworm-slim AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:22-bookworm-slim AS run
WORKDIR /app
ENV NODE_ENV=production \
    HOSTNAME=0.0.0.0 \
    PORT=8080 \
    NEXT_TELEMETRY_DISABLED=1 \
    DATA_DIR=/data
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public
# Railway mounts the persistent volume at /data (signups live in /data/subscribers.db).
EXPOSE 8080
CMD ["node", "server.js"]
