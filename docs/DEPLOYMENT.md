# Deployment Guide

This guide explains how to deploy the Nutrition Scanner to a production environment.

## Overview
The application is split into three main deployable artifacts:
1. **Frontend** (Next.js)
2. **Backend API** (FastAPI)
3. **Inference Service** (FastAPI)

## 1. Cloud Infrastructure (AWS / GCP / Free Tier)

### Free-Tier Optimized Architecture
- **Frontend**: Vercel (Free)
- **Backend API**: Render / Railway / Google Cloud Run (Free Tier)
- **Database**: Supabase PostgreSQL (Free Tier)
- **Storage**: Supabase Storage (Free Tier)
- **Inference**: Hugging Face Spaces / Modal / RunPod (Low Cost Serverless GPU)

## 2. Environment Variables

### Backend API (`apps/api/.env`)
```env
DATABASE_URL=postgresql+asyncpg://user:pass@db-host/dbname
INFERENCE_SERVICE_URL=https://my-inference-service.com
STORAGE_PROVIDER=supabase
STORAGE_LOCAL_DIR=./uploads
LOG_LEVEL=INFO
ENV=production
MAX_IMAGE_SIZE_MB=5
```

### Frontend (`apps/web/.env`)
```env
NEXT_PUBLIC_API_URL=https://api.my-domain.com
```

### Inference Service (`apps/inference/.env`)
```env
ENV=production
# Add specific model keys if using API fallback
```

## 3. Docker Swarm / Compose Deployment
If deploying on a single VPS (e.g., DigitalOcean Droplet, AWS EC2):
1. Clone the repo.
2. Edit `.env` files.
3. Run `docker-compose -f docker-compose.prod.yml up -d --build`.

## 4. CI/CD Integration
A GitHub Action is configured in `.github/workflows/main.yml`.
On push to `main`, it will lint, test, and build the Docker images.
To enable auto-deployment, configure your container registry (e.g., Docker Hub, ECR) and add push steps.
