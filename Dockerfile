# Multi-stage build for React + Python app
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend
COPY job-manager-ui/package*.json ./
RUN npm ci --only=production --silent
COPY job-manager-ui/ ./
RUN npm run build

# Python backend stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Selenium (optimized)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg2 \
    unzip \
    curl \
    xvfb \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python requirements and install
COPY requirements-fastapi.txt .
RUN pip install --no-cache-dir -r requirements-fastapi.txt

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
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

CMD ["python", "fastapi_server.py"]