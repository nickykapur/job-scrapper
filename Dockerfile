# Multi-stage build: React frontend + Python backend with browser support
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend

# Copy package files
COPY job-manager-ui/package.json job-manager-ui/package-lock.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps --silent

# Copy source code and build
COPY job-manager-ui/ ./
RUN npm run build

# Python backend stage with browser support
FROM python:3.11-slim

# Install system dependencies for Chrome and Selenium
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome using modern keyring approach
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all Python files including scraper and daily update scripts
COPY requirements.txt .
COPY fastapi_server.py .
COPY railway_server.py .
COPY main.py .
COPY linkedin_job_scraper.py .
COPY database_models.py .
COPY auth_routes.py .
COPY auth_utils.py .
COPY user_database.py .
COPY daily_dublin_update.py .
COPY daily_multi_country_update.py .
COPY sync_to_railway.py .
COPY jobs_database.json .
COPY database_migrations/ ./database_migrations/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy built React app from frontend stage
COPY --from=frontend-build /app/frontend/dist ./job-manager-ui/dist

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000
ENV RAILWAY_ENVIRONMENT=production
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV CHROME_PATH=/usr/bin/google-chrome-stable

# Expose port
EXPOSE 8000

# Start command with virtual display for headless browser
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 & python railway_server.py"]