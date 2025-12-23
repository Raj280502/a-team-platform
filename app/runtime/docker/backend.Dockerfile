FROM python:3.10-slim

WORKDIR /app

COPY backend /app/backend

RUN pip install flask

EXPOSE 5000

CMD ["python", "backend/app.py"]
