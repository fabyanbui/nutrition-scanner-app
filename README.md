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

## ⚙️ Environment Configuration & Local Setup

All sensitive local environment configuration files (`.env`, `.env.local`) are ignored by Git (listed in `.gitignore`) to prevent credential leakage. Example template files (`.env.example`) have been created across all project locations.

### 📋 Environment Files Overview

| Environment File | Purpose | Location |
| :--- | :--- | :--- |
| `.env` (Root) | Global Compose variables for Docker stack | `/.env.example` |
| `apps/web/.env` | Next.js Frontend server/client settings | `/apps/web/.env.example` |
| `apps/api/.env` | FastAPI Backend & LangGraph settings | `/apps/api/.env.example` |
| `apps/inference/.env` | VLM Open-Source Inference settings | `/apps/inference/.env.example` |

---

### 🛠️ Step-by-Step Setup Guide

#### Option A: Running via Docker Compose (Recommended)

1. **Copy the Root Environment Template**:
   ```bash
   cp .env.example .env
   ```

2. **Launch Docker Stack**:
   ```bash
   docker compose up --build
   ```
   *The root `.env` file configures service-to-service hostnames (`http://api:8000`, `http://inference:8001`) automatically.*

---

#### Option B: Local NPM & Hybrid Debugging (Without Docker)

You can run and debug the frontend directly using **NPM commands** at the root of the workspace.

##### 1. Quick Local Web Debugging (With Next.js Local Gateway Fallback)
`apps/web` includes an in-memory local route handler gateway (`/app/api/v1/analyze/`). When the Python FastAPI backend is not running, the web app automatically falls back to simulating the real-time SSE multi-agent pipeline locally.
```bash
# Install root workspace dependencies
npm install

# Start Next.js development server on http://localhost:3000
npm run dev
```

##### 2. Debugging Next.js Web App with Workspace Workspaces
```bash
# Run web dev server
npm run dev:web

# Run linter across Next.js app
npm run lint

# Test production build locally
npm run build:web
npm run start:web
```

##### 3. Debugging FastAPI Backend & Inference Engine locally with NPM helper scripts
To debug the full end-to-end Python services alongside Next.js:

```bash
# Terminal 1: Run Next.js Frontend (Port 3000)
npm run dev:web

# Terminal 2: Run FastAPI Orchestrator (Port 8000)
# (Ensure your Python virtual environment is active and requirements installed)
npm run dev:api

# Terminal 3: Run Inference Service (Port 8001)
npm run dev:inference
```

---

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
├── docs/           # Technical Documentation
│   ├── ARCHITECTURE.md
│   ├── CODEBASE_GUIDE.md
│   ├── DATABASE_SCHEMA.md
│   ├── DEPLOYMENT.md
│   ├── DESIGN.md
│   └── DOMAIN_REQUIREMENTS.md
├── docker-compose.yml
└── docker-compose.prod.yml
```

## 📚 Documentation Index
- [System Architecture & Multi-Agent Diagrams](docs/ARCHITECTURE.md)
- [Codebase Guide & Directory Walkthrough](docs/CODEBASE_GUIDE.md)
- [Database Schemas & ER Diagrams](docs/DATABASE_SCHEMA.md)
- [Deployment & Cloud Infrastructure Guide](docs/DEPLOYMENT.md)
- [Frontend UI/UX & SSE Design Strategy](docs/DESIGN.md)
- [Domain Requirements & Anti-Hallucination Guidelines](docs/DOMAIN_REQUIREMENTS.md)

