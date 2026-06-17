FROM node:26-alpine AS build

WORKDIR /app

ARG PUBLIC_API_URL=https://api.rubennmg.cloud
ENV PUBLIC_API_URL=${PUBLIC_API_URL}

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
