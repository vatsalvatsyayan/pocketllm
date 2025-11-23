# Multi-stage build for React frontend
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
# Vite needs environment variables at build time
# These are passed as build args and set as ENV vars
# Note: Use localhost since frontend runs in browser, not in Docker network
ARG VITE_API_BASE_URL=http://localhost:9000/api
ARG VITE_MOCK_AUTH=false
ARG VITE_MOCK_CHAT=false

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_MOCK_AUTH=$VITE_MOCK_AUTH
ENV VITE_MOCK_CHAT=$VITE_MOCK_CHAT

RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

