FROM node:22-alpine AS frontend
WORKDIR /src
COPY atividade-2/frontend/package*.json ./
RUN npm ci
COPY atividade-2/frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY atividade-2/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY atividade-2/backend/app ./app
COPY --from=frontend /src/dist ./frontend/dist
EXPOSE 8002
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
