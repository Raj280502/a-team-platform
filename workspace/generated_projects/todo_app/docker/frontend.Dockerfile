FROM node:20-alpine
WORKDIR /app
COPY frontend /app/frontend
RUN npm install -g serve
CMD ["serve", "-s", "/app/frontend", "-l", "3000"]
