# FounderAI — Strategic Business Blueprint Platform

A multi-agent AI platform that turns a single business idea into a complete company blueprint. Eight specialized AI agents collaborate — three running in parallel — to deliver market analysis, legal setup, location strategy, team planning, financials, and a 12-month execution roadmap, in Hebrew or English.

> The application lives in [`FounderAI/`](FounderAI). All commands below assume you `cd FounderAI` first.

---

## How It Works

```
Business Idea
     │
     ▼
┌─────────────────┐
│  Idea Refiner   │   Agent 1 — Refines and structures the concept
└────────┬────────┘
         │ parallel fork (LangGraph fan-out)
   ┌─────┼─────┐
   ▼     ▼     ▼
┌──────┐┌──────┐┌──────────┐
│Market││Legal ││ Location │   Agents 2, 3 & 4 — Run simultaneously
│      ││&Comp.││ Analyst  │
└───┬──┘└──┬───┘└────┬─────┘
    └─────┼─────────┘
          ▼  (fan-in — graph waits for all three)
┌──────────────────┐
│ Team Architect   │   Agent 5 — Hiring plan with Israeli salary data
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Financial Planner│   Agent 6 — Costs, runway, revenue projections
└────────┬─────────┘
         ▼
┌──────────────────┐
│   Alternatives   │   Agent 7 — Budget alternatives & cost savings
│    Optimizer     │
└────────┬─────────┘
         ▼
┌──────────────────┐
│Report Synthesizer│   Agent 8 — Final blueprint with action items
└──────────────────┘
```

The three-way parallel fan-out (market / legal / location) cuts roughly 30–60 seconds off each run versus a strictly sequential pipeline.

---

## What's in the Blueprint

- **Immediate Action Items** — 7 concrete tasks for week one (what, where, cost, time)
- **Market Opportunity** — TAM/SAM/SOM, top competitors with pricing, market gaps
- **Legal Setup Roadmap** — Company registration, licenses, VAT / osek murshe checklist
- **Location Strategy** — Best areas/cities to launch, rent comparisons, competition map, expansion roadmap
- **Grants & Funding** — Innovation Authority programs, eligibility, priority order
- **Team Plan** — Hiring stages with gross salaries and Israeli employer costs (bituach leumi, pension)
- **Equipment & Tools** — What to buy, estimated cost, where to source (Yad2, Alibaba, etc.)
- **Financial Overview** — Setup costs, monthly burn, break-even, 12-month revenue projection
- **Budget Alternatives** — Cheaper software, services, offshore options
- **12-Month Roadmap** — Month-by-month milestones, revenue, team size, budget
- **KPIs** — Metrics per stage with targets
- **Post-Report Chat** — Follow-up questions to an AI advisor with your blueprint as context

---

## Tech Stack

| Layer            | Technology |
|------------------|------------|
| AI Orchestration | LangGraph 0.2 (parallel agent graph) |
| LLMs             | OpenAI GPT-4o (synthesis) + GPT-4o-mini (analysis agents) |
| Backend          | FastAPI + uvicorn (async) |
| Real-time        | WebSocket + Redis Pub/Sub |
| Database         | PostgreSQL 15 (asyncpg) |
| Event Streaming  | Kafka + Zookeeper |
| Vector Store     | ChromaDB |
| Frontend         | React 18 + TypeScript + Vite + Tailwind CSS |
| Infrastructure   | Docker Compose |

---

## Project Structure

```
FounderAI/
├── agents/                       # AI agent pipeline
│   ├── graph.py                  # LangGraph DAG (parallel fan-out/fan-in)
│   ├── state.py                  # Shared state with parallel-safe reducers
│   ├── idea_refiner.py           # Agent 1
│   ├── market_analyst.py         # Agent 2  ┐
│   ├── legal_compliance.py       # Agent 3  ├─ run in parallel
│   ├── location_analyst.py       # Agent 4  ┘
│   ├── team_architect.py         # Agent 5
│   ├── financial_planner.py      # Agent 6
│   ├── alternatives_optimizer.py # Agent 7
│   ├── report_synthesizer.py     # Agent 8
│   ├── tools/                    # Shared tools (memory, search)
│   └── utils.py
│
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app, CORS, lifespan
│   │   ├── config.py
│   │   ├── routers/
│   │   │   ├── blueprints.py     # POST /blueprints, GET /blueprints/:id
│   │   │   ├── ws.py             # WebSocket /ws/:id (live progress)
│   │   │   └── chat.py           # POST /blueprints/:id/chat
│   │   └── db/
│   │       ├── postgres.py
│   │       └── redis_client.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx     # Input form + examples
│   │   │   └── Blueprint.tsx     # Report view + chat panel
│   │   ├── components/
│   │   │   ├── IdeaInput.tsx     # Idea entry form
│   │   │   ├── AgentProgress.tsx # Live agent status sidebar
│   │   │   ├── ChatPanel.tsx     # Post-report advisor chat
│   │   │   ├── ReportRenderer.tsx# Markdown → styled HTML
│   │   │   └── MetricsBar.tsx    # Token / time metrics
│   │   └── hooks/
│   │       └── useWebSocket.ts   # WebSocket (React 18 StrictMode-safe)
│   └── Dockerfile
│
├── data/                         # Kafka producer & event schemas
├── tests/
│   └── unit/                     # 38 unit tests (mocked LLMs)
├── docker-compose.yml
├── Makefile
└── .env.example
```

---

## Getting Started

### Prerequisites

- Docker Desktop
- Anthropic API key (Claude)

### 1. Clone & configure

```bash
git clone <repo-url>
cd CompanyBuilder/FounderAI

cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
```

### 2. Run with Docker

```bash
make build    # First time only
make up       # Start all services
```

App URLs:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### 3. Stop

```bash
make down
```

---

## Local Development (no Docker)

```bash
make install            # Python deps + npm install
make dev-backend        # FastAPI on :8000 with hot reload
make dev-frontend       # Vite dev server on :5173
```

> PostgreSQL and Redis still need to be running — start them via `docker compose up -d postgres redis`.

---

## Environment Variables

| Variable            | Purpose                              | Default in Docker                |
|---------------------|--------------------------------------|----------------------------------|
| `ANTHROPIC_API_KEY` | **Required.** Anthropic (Claude) key | —                                |
| `POSTGRES_URL`      | Postgres connection string           | `postgresql://…@postgres:5432/…` |
| `REDIS_URL`         | Redis connection string              | `redis://redis:6379`             |

When running via `make up`, every variable except `ANTHROPIC_API_KEY` is wired automatically by `docker-compose.yml`.

---

## API Reference

| Method | Endpoint                       | Description                          |
|--------|--------------------------------|--------------------------------------|
| `POST` | `/blueprints`                  | Submit a business idea, start pipeline |
| `GET`  | `/blueprints/:id`              | Status + typed outputs + report      |
| `POST` | `/blueprints/:id/cancel`       | Cancel an in-flight pipeline         |
| `WS`   | `/ws/:id`                      | Live agent progress stream           |
| `POST` | `/blueprints/:id/chat`         | Chat with AI advisor about blueprint |
| `GET`  | `/health`                      | Health check                         |

**Submit a blueprint:**
```bash
curl -X POST http://localhost:8000/blueprints \
  -H "Content-Type: application/json" \
  -d '{"idea": "Coffee cart in Tel Aviv targeting tech workers"}'
```

**Chat with your blueprint:**
```bash
curl -X POST http://localhost:8000/blueprints/{id}/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What should I do in week one?"}'
```

---

## Running Tests

```bash
make test          # All tests
make test-unit     # Unit tests only
make test-watch    # Watch mode
```

38 unit tests cover the original 7 agents with mocked LLM responses. (A test suite for `location_analyst` is still TODO.)

---

## Make Commands

| Command            | Description                                  |
|--------------------|----------------------------------------------|
| `make up`          | Start all services                           |
| `make down`        | Stop all services                            |
| `make build`       | Rebuild Docker images                        |
| `make logs`        | Tail backend logs                            |
| `make dev-backend` | Run backend locally with hot reload          |
| `make dev-frontend`| Run frontend locally                         |
| `make test`        | Run all tests                                |
| `make lint`        | Lint Python (ruff) + TypeScript (`tsc --noEmit`) |
| `make clean`       | Remove containers, volumes, `__pycache__`    |
