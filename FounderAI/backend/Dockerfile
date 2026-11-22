# Build context is the project root (FounderAI/)
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source packages. The `agents/` package is imported as `agents.*`
# from the backend app, so PYTHONPATH must include the repo root.
COPY agents/ ./agents/
COPY data/ ./data/
COPY backend/app/ ./app/

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
