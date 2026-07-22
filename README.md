# Nutrition Scanner

Nutrition Scanner is an AI-powered web application that analyzes food images and estimates nutritional information. This project is built using a modern modular monorepo structure, setting the foundation for robust AI integrations using LangGraph.

## Architecture Overview

*   **Frontend**: Next.js with React and Tailwind CSS.
*   **Backend API**: FastAPI (Python) for processing images and orchestrating AI agents.
*   **AI Agent Pipeline**: A Python package using LangGraph with an open-source Vision Language Model.
*   **Database**: PostgreSQL using SQLAlchemy (Asyncio) to store food analysis schemas (versioned outputs, processing times).
*   **Infrastructure**: Fully containerized with Docker and Docker Compose.

## AI Architecture (Phase 2)

The core analysis pipeline is managed by LangGraph to orchestrate multiple specialized agents:

```text
Image Input
    |
    v
Food Recognition Agent
    |
    v
Ingredient Analysis Agent
    |
    v
Nutrition Estimation Agent
    |
    v
Quality Control Agent
    |
    v
Response Formatting Agent
```

### Agent Responsibilities
- **Food Recognition Agent**: Detects food items/dishes in the image and provides confidence scores.
- **Ingredient Analysis Agent**: Given the detected food, infers probable ingredients and estimates amounts.
- **Nutrition Estimation Agent**: Takes ingredients and estimates macronutrients (calories, protein, carbs, fat, fiber, sugar, sodium).
- **Quality Control Agent**: Validates macro consistencies (e.g., checks if protein/carbs/fat values align with total calories).
- **Response Formatting Agent**: Finalizes structured JSON output for the frontend.

### Model Selection
For Phase 2, we have chosen **llava-1.5-7b** (or alternatives like Qwen2-VL-7B) via an Ollama local deployment integration. 
* **Why**: It is open-source, supports vision and structured output tasks, operates under the 8B parameter threshold, and allows cost-efficient local or low-tier cloud inference without relying on proprietary APIs like OpenAI or Gemini.

### Replacing the VLM Provider
To swap out the LLM provider, you simply need to create a new class extending `BaseVisionModel` in `packages/ai-agents/ai_agents/models/llm_provider.py` and pass it to the `NutritionScannerWorkflow`.

```python
# Example: Using a custom Qwen provider
class QwenVisionModel(BaseVisionModel):
    async def analyze_image(self, image_bytes, prompt, schema=None):
        # Implementation here
        pass

workflow = NutritionScannerWorkflow(model=QwenVisionModel())
```

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
