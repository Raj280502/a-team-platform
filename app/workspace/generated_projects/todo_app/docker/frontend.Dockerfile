# Updated frontend Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY frontend . /app/
RUN npm install
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
