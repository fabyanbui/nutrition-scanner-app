# Database Schema Documentation

## Overview

The database uses **PostgreSQL** with support for structured relational records and flexible **JSONB** documents. This enables strict indexing for core job metadata while allowing extensible storage for complex AI pipeline outputs and multi-agent latency logs.

---

## Entity Relationship (ER) Diagram

```
+-------------------+        +-------------------+        +---------------------+
|       users       |        |       jobs        |        |    food_analyses    |
+-------------------+        +-------------------+        +---------------------+
| id (PK, String)   |<-------| id (PK, String)   |<-------| id (PK, Int)        |
| email (String)    | 1    * | user_id (FK)      | 1    * | job_id (FK)         |
| created_at (Date) |        | status (String)   |        | user_id (FK)        |
+-------------------+        | progress (Float)  |        | image_url (String)  |
                             | image_id (String) |        | result_json (JSONB) |
                             | result_json(JSONB)|        | model_ver (String)  |
                             | agent_meta (JSONB)|        | proc_time (Float)   |
                             | created_at (Date) |        | created_at (Date)   |
                             +-------------------+        +---------------------+
```

---

## Detailed Table Schemas

### 1. `jobs` Table
Stores asynchronous image analysis jobs, tracking real-time status, raw results, and execution metrics.

| Column Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR` | No | Primary Key (UUID / string ID). Indexed. |
| `user_id` | `VARCHAR` | Yes | Foreign Key referencing `users.id`. Optional for anonymous users. |
| `status` | `VARCHAR` | No | Status of execution (`queue`, `running`, `completed`, `failed`). |
| `progress` | `FLOAT` | No | Job completion percentage (`0.0` to `1.0`). |
| `image_id` | `VARCHAR` | Yes | Storage key/identifier for the uploaded image. |
| `image_metadata` | `JSONB` | Yes | Image metadata (resolution, byte size, format, mime-type). |
| `result_json` | `JSONB` | Yes | Final output payload containing foods, ingredients, nutrition, quality report. |
| `error_message` | `TEXT` | Yes | Diagnostic error details if job status is `failed`. |
| `agent_metadata` | `JSONB` | Yes | Latency and status per agent (`[{"agent": "food_recognition", "latency_ms": 420}]`). |
| `inference_metadata` | `JSONB` | Yes | Model identifier, temperature settings, token counts, inference backend parameters. |
| `created_at` | `TIMESTAMP` | No | Job creation timestamp in UTC. |
| `completed_at` | `TIMESTAMP` | Yes | Completion timestamp in UTC. |

---

### 2. `food_analyses` Table
Historical query log for completed food analysis records. Optimized for analytical queries and historical user log views.

| Column Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | No | Primary Key (Auto-increment integer). |
| `job_id` | `VARCHAR` | Yes | Foreign Key referencing `jobs.id`. |
| `user_id` | `VARCHAR` | Yes | Foreign Key referencing `users.id`. |
| `image_url` | `VARCHAR` | Yes | Publicly accessible URL or storage path for the food photo. |
| `result_json` | `JSONB` | No | Complete structured nutrition and ingredient breakdown. |
| `model_version` | `VARCHAR` | No | Version tag of the Vision Language Model used for inference. |
| `processing_time` | `FLOAT` | No | Total end-to-end processing latency in milliseconds. |
| `created_at` | `TIMESTAMP` | No | Log creation timestamp in UTC. |

---

### 3. `users` Table
Stores user account details for future expansion (authentication, personal meal history, macro tracking).

| Column Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR` | No | Primary Key (UUID / Auth provider ID). Indexed. |
| `email` | `VARCHAR` | Yes | Unique user email address. Indexed. |
| `created_at` | `TIMESTAMP` | No | Registration timestamp in UTC. |

---

## JSONB Structure Specification

### `result_json` Schema Example
```json
{
  "foods": [
    {
      "name": "Pho Bo (Vietnamese Beef Noodle Soup)",
      "confidence": 0.92
    }
  ],
  "ingredients": [
    {
      "name": "Rice Noodles",
      "estimated_amount": "200g",
      "confidence": 0.89
    },
    {
      "name": "Beef Slices",
      "estimated_amount": "100g",
      "confidence": 0.85
    }
  ],
  "nutrition": {
    "calories": { "value": 550.0, "confidence": 0.85 },
    "protein": { "value": 30.0, "confidence": 0.82 },
    "carbs": { "value": 65.0, "confidence": 0.88 },
    "fat": { "value": 15.0, "confidence": 0.80 },
    "fiber": { "value": 3.0, "confidence": 0.75 },
    "sugar": { "value": 5.0, "confidence": 0.78 },
    "sodium": { "value": 1200.0, "confidence": 0.85 }
  },
  "quality": {
    "valid": true,
    "warnings": [],
    "adjusted_confidence": { "overall": 0.84 }
  },
  "processing_time_ms": 1850
}
```

---

## Database Migration & Local Development

- Database connections use **SQLAlchemy Async Session** (`postgresql+asyncpg://`).
- Automatic table creation is handled at application startup via `await conn.run_sync(Base.metadata.create_all)`.
- Fallback SQLite memory / file databases can be specified in `.env` (`DATABASE_URL=sqlite+aiosqlite:///./test.db`) during lightweight development when PostgreSQL is not running locally.
