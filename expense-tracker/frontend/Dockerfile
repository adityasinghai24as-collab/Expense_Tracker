# TODO: Task 35 - Add Frontend to Docker Compose
# Use a node base image for building the app, then Nginx to serve it
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
# RUN npm install
# COPY . .
# RUN npm run build

# FROM nginx:alpine
# COPY --from=builder /app/dist /usr/share/nginx/html
# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]
