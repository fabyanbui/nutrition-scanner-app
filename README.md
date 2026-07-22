# Nutrition Scanner

An AI-powered web application that analyzes food images to estimate nutritional information. This project is built as a production-oriented MVP showcasing a multi-agent AI pipeline using LangGraph, streamed to the client using Server-Sent Events (SSE).

## Phase 3: Productization & Streaming

This phase transforms the synchronous proof-of-concept into a robust streaming architecture. It improves user experience, system observability, and handles long-running AI pipelines gracefully.

### Streaming Architecture & SSE Explanation
The application uses **Server-Sent Events (SSE)** for unidirectional real-time communication from the server to the client. When an image is uploaded, the frontend opens an `EventSource` connection to the `/api/v1/analyze/{job_id}/stream` endpoint.
SSE was chosen over WebSockets because the data flow is strictly unidirectional (server -> client progress updates), making SSE a lighter, more appropriate, and easier-to-scale choice.

### Job Lifecycle
To prevent HTTP timeouts and allow asynchronous processing:
1. **Job Created**: Image is uploaded to `POST /api/v1/analyze`. The server performs basic heuristics, writes a new `Job` record to PostgreSQL, and returns a `job_id` immediately.
2. **Queue**: The job enters the processing queue (managed by FastAPI `BackgroundTasks` in this MVP).
3. **Running**: The LangGraph agent pipeline executes. As each node starts and finishes, it pushes events into an asynchronous queue mapped to the `job_id`.
4. **Completed / Failed**: The final state (or error) is recorded in PostgreSQL.

### Agent Execution Flow
The AI pipeline utilizes LangGraph to coordinate multiple specialized agents:
1. **Food Recognition Agent**: Detects food items in the image.
2. **Ingredient Analysis Agent**: Extracts and lists possible ingredients.
3. **Nutrition Estimation Agent**: Estimates macronutrients and calories.
4. **Quality Control Agent**: Validates consistency across agents and flags issues (e.g., unrealistic calorie counts).
5. **Response Formatting Agent**: Structures the final output.

### Frontend State Management
The Next.js frontend maintains a structured state for the `Agent Timeline` and `Partial Results`.
As SSE events arrive, they update a `stages` array (tracking `pending`, `running`, `completed` states for each agent) and a `partialData` object that incrementally populates the "Analysis Results" UI with confidence badges.

### Observability Strategy
Every agent execution logs its latency. The timeline events emitted over SSE contain `latency_ms` properties, which are then rendered on the client timeline. The overall pipeline latency, errors, and success rates are recorded in the PostgreSQL `jobs` table to feed into future dashboard analytics.
