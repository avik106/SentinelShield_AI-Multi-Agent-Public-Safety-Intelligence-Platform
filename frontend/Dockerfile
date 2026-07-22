# ==============================================================================
# SentinelShield AI Frontend Dockerfile
# ==============================================================================
# Stage 1: Build the React Application
FROM node:20-alpine AS build

WORKDIR /app

# Copy dependency manifests
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy all code files
COPY . .

# Build production distribution
RUN npm run build

# Stage 2: Serve using Nginx
FROM nginx:stable-alpine

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy build artifacts to Nginx server html path
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
