FROM node:18-alpine

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build for production
RUN npm run build

# Simple serve
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "3000"]
