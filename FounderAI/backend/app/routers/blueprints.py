"""
Blueprint API routes:
  POST /blueprints       — Submit a business idea, kick off the pipeline
  GET  /blueprints/:id   — Poll blueprint status + agent statuses + report
"""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

logger = logging.getLogger(__name__)

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from ..db.postgres import get_pool
from ..db.redis_client import publish
from agents.graph import founder_graph
from agents.state import FounderState

router = APIRouter(prefix="/blueprints", tags=["blueprints"])


class BlueprintRequest(BaseModel):
    idea: str


async def _run_pipeline(blueprint_id: str, idea: str) -> None:
    """Execute the agent graph and persist every intermediate state to Redis + Postgres."""
    pool = await get_pool()

    async def _emit(event: dict[str, Any]) -> None:
        await publish(f"blueprint:{blueprint_id}", json.dumps(event))

    try:
        initial_state: FounderState = {
            "task_id": blueprint_id,
            "raw_input": idea,
            "language": "en",
            "refined_idea": "",
            "market_analysis": "",
            "legal_compliance": "",
            "location_analysis": "",
            "team_structure": "",
            "financial_plan": "",
            "alternatives": "",
            "final_report": "",
            "current_agent": "",
            "agent_statuses": {},
            "error": None,
            "metadata": {},
        }

        async for step in founder_graph.astream(initial_state):
            node_name = list(step.keys())[0]
            node_state: FounderState = step[node_name]
            logger.info("Step completed: node=%s keys=%s", node_name, list(node_state.keys()))

            agent_status = node_state.get("agent_statuses", {}).get(node_name, "running")

            # Persist agent run to Postgres
            output_field_map = {
                "idea_refiner": "refined_idea",
                "market_analyst": "market_analysis",
                "legal_agent": "legal_compliance",
                "location_analyst": "location_analysis",
                "team_architect": "team_structure",
                "financial_planner": "financial_plan",
                "alternatives_optimizer": "alternatives",
                "report_synthesizer": "final_report",
            }
            output_text = node_state.get(output_field_map.get(node_name, ""), "") or ""
            meta = node_state.get("metadata", {}).get(node_name, {})

            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO agent_runs (blueprint_id, agent_name, status, duration_ms, tokens_used, model_used, output)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT DO NOTHING
                    """,
                    uuid.UUID(blueprint_id),
                    node_name,
                    agent_status,
                    meta.get("duration_ms"),
                    meta.get("tokens_used"),
                    meta.get("model_used"),
                    output_text[:50000],  # cap text length
                )

            # Publish live update to Redis pub/sub (WebSocket consumers listen here)
            await _emit({
                "type": "agent_update",
                "agent": node_name,
                "status": agent_status,
                "output": output_text[:3000],  # truncate for socket
            })

        # Pipeline complete — write report and update blueprint status
        final_state = node_state  # last yielded state
        final_report = final_state.get("final_report", "")
        language = final_state.get("language", "en")

        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE blueprints SET status='completed', completed_at=NOW() WHERE id=$1",
                uuid.UUID(blueprint_id),
            )
            await conn.execute(
                "INSERT INTO reports (blueprint_id, content, language) VALUES ($1, $2, $3)",
                uuid.UUID(blueprint_id),
                final_report,
                language,
            )

        await _emit({"type": "completed", "report": final_report})

    except Exception as exc:
        logger.exception("Pipeline failed for blueprint %s: %s", blueprint_id, exc)
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE blueprints SET status='error' WHERE id=$1",
                uuid.UUID(blueprint_id),
            )
        await _emit({"type": "error", "message": str(exc)})


@router.post("", status_code=202)
async def create_blueprint(body: BlueprintRequest, background_tasks: BackgroundTasks):
    """Submit a business idea. Returns a blueprint_id to track progress."""
    if not body.idea.strip():
        raise HTTPException(status_code=422, detail="idea cannot be empty")

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO blueprints (raw_input) VALUES ($1) RETURNING id, created_at",
            body.idea,
        )
    blueprint_id = str(row["id"])

    background_tasks.add_task(_run_pipeline, blueprint_id, body.idea)

    return {"blueprint_id": blueprint_id, "status": "pending"}


@router.get("/{blueprint_id}")
async def get_blueprint(blueprint_id: str):
    """Get blueprint status, agent run details, and final report (when ready)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        blueprint = await conn.fetchrow(
            "SELECT id, raw_input, language, status, created_at, completed_at FROM blueprints WHERE id=$1",
            uuid.UUID(blueprint_id),
        )
        if not blueprint:
            raise HTTPException(status_code=404, detail="blueprint not found")

        agent_runs = await conn.fetch(
            "SELECT agent_name, status, duration_ms, tokens_used, model_used FROM agent_runs WHERE blueprint_id=$1 ORDER BY id",
            uuid.UUID(blueprint_id),
        )
        report = await conn.fetchrow(
            "SELECT content, language FROM reports WHERE blueprint_id=$1",
            uuid.UUID(blueprint_id),
        )

    return {
        "id": blueprint_id,
        "raw_input": blueprint["raw_input"],
        "language": blueprint["language"],
        "status": blueprint["status"],
        "created_at": blueprint["created_at"].isoformat(),
        "completed_at": blueprint["completed_at"].isoformat() if blueprint["completed_at"] else None,
        "agents": [dict(r) for r in agent_runs],
        "report": report["content"] if report else None,
    }
