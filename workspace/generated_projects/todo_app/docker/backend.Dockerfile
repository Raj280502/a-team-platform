FROM python:3.10-slim
WORKDIR /app
COPY backend /app/backend
RUN pip install flask
CMD ["python", "/app/backend/app.py"]
