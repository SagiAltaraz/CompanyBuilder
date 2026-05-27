.PHONY: up down logs build test test-unit dev-backend dev-frontend install

# Docker Compose
up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f backend

build:
	docker compose build

# Development (local, no Docker)
dev-backend:
	cd backend && PYTHONPATH=.. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

# Testing
test:
	pytest tests/ -v --tb=short

test-unit:
	pytest tests/unit/ -v --tb=short

test-watch:
	pytest tests/ -v --tb=short -f

# Linting
lint:
	ruff check agents/ backend/ data/ tests/
	cd frontend && npx tsc --noEmit

# Cleanup
clean:
	docker compose down -v
	find . -type d -name __pycache__ | xargs rm -rf
	find . -name "*.pyc" | xargs rm -f
