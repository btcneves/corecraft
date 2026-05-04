# Multi-stage build for CoreCraft Atividade 3
# Optimized for small image size and fast builds
#
# Build arguments:
#   APP_PORT - Port the application listens on (default: 8003)

# ==============================================================================
# Stage 1: Build frontend assets
# ==============================================================================
FROM node:22-alpine AS frontend-builder

WORKDIR /src

# Copy package files first for better layer caching
COPY atividade-3/frontend/package*.json ./

# Install dependencies (including dev dependencies for build)
RUN npm ci

# Copy source code and build
COPY atividade-3/frontend/ ./
RUN npm run build

# ==============================================================================
# Stage 2: Runtime with FastAPI backend
# ==============================================================================
FROM python:3.12-alpine AS runtime

# Build arguments for port configuration
ARG APP_PORT=8003

# Install runtime dependencies
RUN apk add --no-cache \
    libffi \
    ca-certificates \
    tzdata

# Python environment configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_PORT=${APP_PORT} \
    PATH="/home/corecraft/.local/bin:$PATH"

WORKDIR /app

# Install shared corecraft package
COPY src/ ./src/
COPY pyproject.toml ./
RUN pip install --no-cache-dir ./

# Copy and install Python dependencies first for better layer caching
COPY atividade-3/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy application code
COPY atividade-3/backend/app ./app

# Copy built frontend assets from builder stage
COPY --from=frontend-builder /src/dist ./frontend/dist

# Create non-root user with specific UID/GID for security
RUN addgroup -S -g 1001 corecraft \
    && adduser -S -u 1001 -G corecraft -h /app corecraft \
    && chown -R corecraft:corecraft /app

# Switch to non-root user
USER corecraft

EXPOSE ${APP_PORT}

# Health check using wget (available in Alpine)
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:${APP_PORT}/health || exit 1

# Run with gunicorn for production
CMD gunicorn -b 0.0.0.0:${APP_PORT} -w 1 -k uvicorn.workers.UvicornWorker app.main:app