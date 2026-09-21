# Build stage
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Baked at build time; override with --build-arg for staging/demo.
ARG VITE_API_BASE_URL=/api/v1
ARG VITE_DEMO_PERSONAS=false
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL VITE_DEMO_PERSONAS=$VITE_DEMO_PERSONAS
RUN npm run build

# Serve stage
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
