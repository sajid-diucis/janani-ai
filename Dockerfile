
# ==========================================
# STAGE 1: Build Frontend (Next.js)
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Install dependencies first (Caching)
COPY frontend/package*.json ./
RUN npm install

# Copy source code
COPY frontend/ .

# Build Static Export (output -> /app/frontend/out)
RUN npm run build

# ==========================================
# STAGE 2: Build Backend (FastAPI + Python)
# ==========================================
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (FFmpeg for Audio)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY fastapi-app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Backend Code
COPY fastapi-app/ .

# Copy Built Frontend Assets from Stage 1
# 1. Copy _next static files
COPY --from=frontend-builder /app/frontend/out/_next ./static/_next
# 2. Copy index.html to templates
COPY --from=frontend-builder /app/frontend/out/index.html ./templates/index.html
# 3. Copy offline_rules.json (from public or out)
COPY --from=frontend-builder /app/frontend/public/offline_rules.json ./static/offline_rules.json

# Expose Port
EXPOSE 8000

# Run Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
