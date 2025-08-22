# 🚀 LinkedIn Job Manager - Deployment Guide

## 📋 Overview

This guide covers how to deploy the LinkedIn Job Manager React app with Material-UI frontend and FastAPI backend to various hosting platforms.

## 🏗️ Architecture

- **Frontend**: React + TypeScript + Material-UI (Vite build)
- **Backend**: FastAPI + Python (job scraper + API)
- **Database**: JSON file storage
- **Scraping**: Selenium WebDriver with Chrome/Firefox

---

## 🔧 Local Development Setup

### Prerequisites
```bash
# Backend requirements
- Python 3.8+
- Chrome or Firefox browser
- Virtual environment (recommended)

# Frontend requirements  
- Node.js 18+
- npm or yarn
```

### Setup Steps

1. **Clone and setup backend**:
```bash
cd python-job
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

pip install -r requirements-fastapi.txt
```

2. **Setup frontend**:
```bash
cd job-manager-ui
npm install
```

3. **Development servers**:
```bash
# Terminal 1: Backend
python fastapi_server.py
# Runs on http://localhost:8000

# Terminal 2: Frontend  
cd job-manager-ui
npm run dev
# Runs on http://localhost:5173
```

---

## ☁️ Hosting Options

### 1. 🌐 **Vercel** (Recommended for Frontend + API)

**Best for**: Quick deployment, serverless functions, free tier

#### Frontend Deployment
```bash
cd job-manager-ui
npm run build
npm install -g vercel
vercel --prod
```

#### Backend as Serverless Functions
Create `api/` folder in React project:
```bash
mkdir job-manager-ui/api
# Move FastAPI endpoints to serverless functions
```

**Vercel Config** (`vercel.json`):
```json
{
  "builds": [
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ]
}
```

### 2. 🐳 **Railway** (Recommended for Full Stack)

**Best for**: Full Python backend support, automatic deployments

#### Setup
1. Connect GitHub repo to Railway
2. Add environment variables:
   ```
   PORT=8000
   PYTHON_VERSION=3.11
   ```
3. Create `railway.toml`:
   ```toml
   [build]
   builder = "nixpacks"
   buildCommand = "cd job-manager-ui && npm install && npm run build && cd .. && pip install -r requirements-fastapi.txt"
   
   [deploy]
   startCommand = "python fastapi_server.py"
   ```

### 3. 🌊 **DigitalOcean App Platform**

**Best for**: Managed hosting, multiple services

#### Setup
```yaml
name: linkedin-job-manager
services:
- name: api
  source_dir: /
  github:
    repo: your-username/python-job
    branch: main
  run_command: python fastapi_server.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  
- name: frontend  
  source_dir: /job-manager-ui
  github:
    repo: your-username/python-job
    branch: main
  build_command: npm install && npm run build
  run_command: npm run preview
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
```

### 4. 🚀 **Heroku**

**Best for**: Traditional hosting, add-ons ecosystem

#### Setup
```bash
# Install Heroku CLI
npm install -g heroku

# Login and create app
heroku login
heroku create your-job-manager

# Add buildpacks
heroku buildpacks:add heroku/nodejs
heroku buildpacks:add heroku/python

# Deploy
git push heroku main
```

**Procfile**:
```
web: python fastapi_server.py
release: cd job-manager-ui && npm install && npm run build
```

### 5. 📦 **Docker Deployment**

**Best for**: Containerized deployment, any cloud provider

#### Multi-stage Dockerfile
```dockerfile
# Build React app
FROM node:18-alpine as frontend-build
WORKDIR /app/frontend
COPY job-manager-ui/package*.json ./
RUN npm install
COPY job-manager-ui/ ./
RUN npm run build

# Python backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
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

EXPOSE 8000
CMD ["python", "fastapi_server.py"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  job-manager:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./jobs_database.json:/app/jobs_database.json
    environment:
      - NODE_ENV=production
```

### 6. ⚡ **AWS Lambda + S3**

**Best for**: Serverless, pay-per-use

#### Backend (Lambda)
```python
# lambda_handler.py
import json
from mangum import Mangum
from fastapi_server import app

handler = Mangum(app)
```

#### Frontend (S3 + CloudFront)
```bash
cd job-manager-ui
npm run build
aws s3 sync dist/ s3://your-bucket-name
```

---

## 🛠️ Environment Configuration

### Production Environment Variables

Create `.env` file:
```bash
# API Configuration
API_URL=https://your-api-domain.com
PORT=8000
NODE_ENV=production

# Scraper Configuration
HEADLESS=true
LOCATION="Dublin, County Dublin, Ireland"

# Security (if needed)
SECRET_KEY=your-secret-key
```

### Build Scripts

**package.json** updates:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "build:docker": "docker build -t job-manager ."
  }
}
```

---

## 🔒 Security Considerations

### Production Checklist
- [ ] **HTTPS only** in production
- [ ] **CORS configuration** restricted to your domain
- [ ] **Environment variables** for sensitive data
- [ ] **Rate limiting** on API endpoints
- [ ] **Input validation** on all endpoints
- [ ] **Error handling** without exposing internals

### FastAPI Security Updates
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

---

## 📊 Monitoring & Analytics

### Add Health Checks
```python
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "jobs_count": len(load_jobs())
    }
```

### Logging Configuration
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

---

## 🚨 Troubleshooting

### Common Issues

1. **Selenium WebDriver Issues**:
   ```bash
   # Install Chrome in Docker
   RUN apt-get update && apt-get install -y google-chrome-stable
   ```

2. **CORS Errors**:
   ```python
   # Update allowed origins
   allow_origins=["https://yourdomain.com"]
   ```

3. **Build Errors**:
   ```bash
   # Clear cache and rebuild
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

4. **Port Issues**:
   ```python
   # Use environment port
   port = int(os.environ.get("PORT", 8000))
   uvicorn.run(app, host="0.0.0.0", port=port)
   ```

---

## 🎯 Recommended Deployment

For most use cases, I recommend:

1. **Railway** for backend (full Python support)
2. **Vercel** for frontend (fast global CDN)  
3. **Docker** for self-hosting

This provides the best balance of:
- ✅ Easy deployment
- ✅ Selenium support  
- ✅ Cost-effective
- ✅ Scalable
- ✅ Fast performance

---

## 📞 Support

If you encounter issues:
1. Check the logs in your hosting platform
2. Verify environment variables are set
3. Test API endpoints manually
4. Check browser console for frontend errors

---

**Happy Deploying! 🚀**