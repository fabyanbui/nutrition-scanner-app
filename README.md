# Nutrition Scanner - Phase 1 MVP

Nutrition Scanner is an AI-powered web application that analyzes food images and estimates nutritional information. This project is built using a modern modular monorepo structure, setting the foundation for robust AI integrations using LangGraph in future phases.

## Architecture Overview

*   **Frontend**: Next.js with React and Tailwind CSS.
*   **Backend API**: FastAPI (Python) for processing images and orchestrating AI agents.
*   **Mock AI Layer**: A Python package defining interfaces for `FoodRecognitionAgent`, `IngredientAgent`, `NutritionAgent`, and `QualityAgent`. Currently returns mocked confidence-scored structured outputs.
*   **Database**: PostgreSQL using SQLAlchemy (Asyncio) to store food analysis schemas (versioned outputs, processing times).
*   **Infrastructure**: Fully containerized with Docker and Docker Compose.

## Repository Structure

```
nutrition-scanner/
├── apps/
│   ├── web/                # Next.js frontend
│   └── api/                # FastAPI backend
├── packages/
│   ├── ai-agents/          # Mock AI pipeline & interfaces
│   ├── shared-types/       # Shared TypeScript types
│   └── config/             # Shared tooling config
├── docker-compose.yml
└── README.md
```

## Setup & Running Instructions

### Prerequisites
* Docker and Docker Compose installed.

### Environment Variables
For local Docker development, no `.env` file is strictly required as defaults are provided in `docker-compose.yml`.
If running natively:
* `API_URL` (Frontend): URL to the backend API (default: `http://127.0.0.1:8000`)
* `DATABASE_URL` (Backend): Connection string for PostgreSQL (default: `sqlite+aiosqlite:///./test.db` for local mock)

### Run with Docker

1. Clone the repository and navigate to the root directory.
2. Build and start the services:

   ```bash
   docker compose up --build
   ```

3. Access the application:
   * Frontend Web UI: [http://localhost:3000](http://localhost:3000)
   * FastAPI Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Features in Phase 1
- Modular monorepo setup.
- Image upload and preview UI.
- Simulated processing endpoint reflecting real AI output schemas.
- Confidence scores generated for every prediction field.
- Database schema setup for tracking AI processing results.
