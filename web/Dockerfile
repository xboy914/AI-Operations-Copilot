FROM node:24-alpine AS dependencies
WORKDIR /app
COPY package*.json ./
RUN npm install

FROM node:24-alpine AS builder
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
WORKDIR /app
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:24-alpine AS runtime
ENV NODE_ENV=production
WORKDIR /app
RUN addgroup -S copilot && adduser -S copilot -G copilot
COPY --from=builder --chown=copilot:copilot /app ./
USER copilot
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD wget -qO- http://localhost:3000/ >/dev/null || exit 1
CMD ["npm", "start"]
