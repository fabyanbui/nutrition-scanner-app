# Complete Codebase Guide

## Repository Structure & Packages

This repository is structured as a monorepo containing application services and reusable packages:

```
nutrition-scanner/
├── apps/
│   ├── api/                   # FastAPI Backend (Agent Orchestrator, Storage, DB, SSE)
│   ├── inference/             # FastAPI Inference Service (VLM Open-Source Model Host)
│   └── web/                   # Next.js App Router Frontend (UI & Next API Proxy)
├── packages/
│   ├── ai-agents/             # LangGraph Multi-Agent Workflows & Pydantic Schemas
│   ├── evaluation/            # Benchmark Pipeline & Accuracy Metrics Engine
│   ├── shared-types/          # Shared TypeScript & Python Interfaces
│   └── config/                # Common TypeScript & ESLint Configurations
├── docs/                      # Technical Documentation
│   ├── ARCHITECTURE.md        # System Architecture & Multi-Agent Diagrams
│   ├── CODEBASE_GUIDE.md      # Detailed Directory & Module Walkthrough
│   ├── DATABASE_SCHEMA.md     # PostgreSQL Schemas & ER Diagrams
│   ├── DEPLOYMENT.md          # Cloud Deployment & Docker Commands
│   ├── DESIGN.md              # UI/UX Design System & SSE Strategy
│   └── DOMAIN_REQUIREMENTS.md # Confidence Rules & Domain Constraints
├── .gitignore                 # Version Control Ignore Specs
├── docker-compose.yml         # Development Multi-Container Orchestration
└── package.json               # Root Monorepo Configuration
```

---

## Detailed Directory Breakdown

### 1. `apps/web/` (Frontend Application)
- **Framework**: Next.js (App Router), React, Tailwind CSS.
- **Key Files**:
  - `src/app/page.tsx`: Single-page interactive application featuring drag-and-drop image upload, real-time agent status tracker, and nutritional breakdown visualizer.
  - `src/app/api/v1/analyze/route.ts`: API route for initial image upload and proxying to FastAPI.
  - `src/app/api/v1/analyze/[jobId]/stream/route.ts`: SSE stream handler for real-time progress updates.
  - `src/app/api/v1/jobsStore.ts`: In-memory job state store for local dev fallback.

### 2. `apps/api/` (Backend Orchestrator)
- **Framework**: Python, FastAPI, SQLAlchemy (Async), LangGraph.
- **Key Files**:
  - `src/main.py`: Main FastAPI server exposing `/api/v1/analyze` and SSE stream routes.
  - `src/db/models.py`: SQLAlchemy models (`Job`, `User`, `FoodAnalysis`).
  - `src/db/database.py`: Async engine configuration and session dependency injections.
  - `src/storage.py`: Pluggable object storage adapter (`LocalStorageProvider`, `SupabaseStorageProvider`).
  - `src/image_quality.py`: Image size, resolution, and format validation helpers.
  - `src/logger.py`: Centralized structured JSON logger.

### 3. `apps/inference/` (Inference Engine)
- **Framework**: FastAPI, Open-Source VLM integration (Mock / HuggingFace Transformers adapter).
- **Key Files**:
  - `src/main.py`: Low-latency HTTP inference endpoint (`POST /infer`) for image-to-text JSON parsing.

### 4. `packages/ai-agents/` (AI Agent Engine)
- **Framework**: Python, LangGraph, Pydantic.
- **Key Modules**:
  - `ai_agents/graph/workflow.py`: LangGraph state machine constructing the 5-agent sequential graph.
  - `ai_agents/agents/`:
    - `food_recognition.py`: Food item identification node.
    - `ingredient_analysis.py`: Portion size & ingredient analysis node.
    - `nutrition_estimation.py`: Macro and micro estimation node.
    - `quality_control.py`: Mathematical consistency check node.
    - `response_formatter.py`: Output normalization node.
  - `ai_agents/schemas/nutrition.py`: Pydantic data schemas for strict type safety.

### 5. `packages/evaluation/` (AI Benchmark Suite)
- **Framework**: Python benchmarking package.
- **Key Modules**:
  - `evaluation/metrics/recognition.py`: Precision/Recall accuracy for food detection.
  - `evaluation/metrics/confidence.py`: Calibration error metrics.
  - `evaluation/metrics/nutrition.py`: Mean Absolute Error (MAE) for calorie/macro estimates.

---

## Local Development & Runnable Commands

### Running Next.js Frontend
```bash
npm run dev:web
```
Runs the web app on `http://localhost:3000`.

### Building Frontend Assets
```bash
npm run build:web
```

### Running Complete Monorepo via Docker Compose
```bash
docker-compose up --build
```
Spins up `web` (3000), `api` (8000), `inference` (8001), and PostgreSQL (5432) concurrently.
