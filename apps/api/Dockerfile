FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for postgres/asyncpg
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy API and mock agent package
COPY apps/api/src src/
COPY packages/ai-agents /packages/ai-agents/

# Ensure packages can be imported
ENV PYTHONPATH=/packages

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
