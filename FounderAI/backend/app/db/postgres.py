"""
PostgreSQL async client using asyncpg.
"""
from __future__ import annotations

import asyncpg
from ..config import settings

_pool: asyncpg.Pool | None = None

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS blueprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_input TEXT NOT NULL,
    language VARCHAR(5) NOT NULL DEFAULT 'en',
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blueprint_id UUID NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'waiting',
    duration_ms INTEGER,
    tokens_used INTEGER,
    model_used VARCHAR(50),
    output TEXT
);

CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blueprint_id UUID NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    language VARCHAR(5) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            settings.postgres_url,
            min_size=2,
            max_size=10,
        )
        async with _pool.acquire() as conn:
            await conn.execute(CREATE_TABLES_SQL)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
