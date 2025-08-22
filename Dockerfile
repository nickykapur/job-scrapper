# Multi-stage build for React + Python app
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend
COPY job-manager-ui/package*.json ./
RUN npm ci --only=production --silent
COPY job-manager-ui/ ./
RUN npm run build

# Python backend stage - minimal for Railway
FROM python:3.11-slim

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python requirements and install
COPY requirements-railway.txt .
RUN pip install --no-cache-dir -r requirements-railway.txt

# Copy backend code
COPY *.py ./
COPY jobs_database.json ./

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./job-manager-ui/dist

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENV PYTHONPATH=/app
ENV RAILWAY_ENVIRONMENT=production

CMD ["python", "fastapi_server.py"]