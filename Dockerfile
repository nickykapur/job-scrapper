# Minimal Dockerfile for Railway - just Python FastAPI
FROM python:3.11-slim

WORKDIR /app

# Copy only the essential files
COPY requirements.txt .
COPY simple_server.py .
COPY jobs_database.json .

# Install minimal Python requirements (only 2 packages!)
RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE 8000

# Run the simple server
CMD ["python", "simple_server.py"]