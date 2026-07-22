# Nutrition Scanner

An AI-powered web application that analyzes food images to estimate nutritional information. This project is built as a production-oriented MVP showcasing a multi-agent AI pipeline using LangGraph.

## Phase 4: Cloud-Native Architecture

This phase transforms the MVP into a production-inspired, cost-aware, and cloud-native AI application.

### Key Architectural Improvements:
- **Separation of Services**: The system is split into three independent services:
  - **Frontend (Next.js)**: Scalable presentation layer.
  - **API Gateway (FastAPI)**: Orchestrates the LangGraph agents, handles database operations, caching, and storage.
  - **Inference Service (FastAPI)**: A dedicated, isolated service running the open-source VLM. The backend interacts with it via HTTP, allowing easy migration of inference tasks to serverless GPU clouds (e.g., RunPod, Modal) without altering core logic.
- **Containerization**: Fully containerized environment via `docker-compose`. Separate `docker-compose.dev.yml` and `docker-compose.prod.yml` configurations for deployment.
- **Robustness**: 
  - Centralized **JSON logging** and basic **metrics** endpoints.
  - Health checks (`/health`, `/ready`, `/status`) integrated into all services.
  - Expanded **PostgreSQL Database Schema** designed to track job pipelines, agent execution latency, model versioning, and future multi-tenant users without schema redesign.
  - Abstracted **Storage** (Local/Supabase) and **Caching** providers.
- **CI/CD Pipeline**: GitHub Actions configured to lint, test, and build Docker containers.

## 🚀 Quick Start (Local Development)

You can run the entire stack locally in under 10 minutes using Docker Compose.

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running.

### 1. Start the project
```bash
docker compose up --build
```

### 2. Access the application
- **Frontend App**: [http://localhost:3000](http://localhost:3000)
- **API Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Inference Service**: [http://localhost:8001/health](http://localhost:8001/health)

### 3. Stop the project
```bash
docker compose down
```

## 📁 Repository Structure
```
nutrition-scanner/
├── apps/
│   ├── web/        # Next.js Frontend
│   ├── api/        # FastAPI Backend (Agent Orchestrator)
│   └── inference/  # FastAPI Inference Service (VLM Runner)
├── packages/
│   ├── ai-agents/  # LangGraph Agent Workflows
│   ├── shared/     # Shared Utilities & Config
│   └── evaluation/ # Benchmarks & Metrics
├── docs/           # Architecture and Deployment Guides
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
├── docker-compose.yml
└── docker-compose.prod.yml
```

## 📚 Documentation
- [Architecture Details](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## Environment Configuration
Configuration is heavily abstracted via `pydantic-settings`. Template `.env.example` files are provided in respective app directories. By default, local docker-compose provides environment variables to run locally smoothly.
