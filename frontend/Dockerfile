# Node.js base image kullan
FROM node:18-alpine AS base

# Dependencies yüklemek için
FROM base AS deps
# libc6-compat Alpine'de Node.js uygulamaları için gerekli
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Package manager lock dosyalarını kopyala
COPY package.json package-lock.json* ./
RUN \
  if [ -f package-lock.json ]; then npm ci; \
  else echo "Warning: package-lock.json not found." && npm install; \
  fi


# Builder stage - source kodu build et
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js telemetry'yi devre dışı bırak
ENV NEXT_TELEMETRY_DISABLED 1

# Production build yap
RUN npm run build

# Production image - sadece gerekli dosyaları kopyala
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Güvenlik için root olmayan kullanıcı oluştur
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Build çıktılarını kopyala
COPY --from=builder /app/public ./public

# Otomatik oluşturulan standalone dosyalarını kopyala
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Server'ı başlat
CMD ["node", "server.js"] 