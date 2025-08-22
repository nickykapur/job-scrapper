# Multi-stage build: React frontend + Python backend
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend

# Copy package files
COPY job-manager-ui/package*.json ./
RUN npm ci --only=production --silent

# Copy source code and build
COPY job-manager-ui/ ./
RUN npm run build

# Python backend stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python files
COPY requirements.txt .
COPY fastapi_server.py .
COPY jobs_database.json .

# Install Python dependencies
RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0

# Copy built React app from frontend stage
COPY --from=frontend-build /app/frontend/dist ./job-manager-ui/dist

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE 8000

# Run the FastAPI server (which serves React app)
CMD ["python", "fastapi_server.py"]