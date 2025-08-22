# Multi-stage build for React + Python app
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend
COPY job-manager-ui/package*.json ./
RUN npm install
COPY job-manager-ui/ ./
RUN npm run build

# Python backend stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

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

CMD ["python", "fastapi_server.py"]