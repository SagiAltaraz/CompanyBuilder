"""Blueprint API routes.

  POST   /blueprints              — Submit a business idea, kick off the pipeline
  GET    /blueprints/:id          — Status + typed agent outputs + final report
  POST   /blueprints/:id/cancel   — Cancel an in-flight pipeline
"""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from agents.graph import founder_graph
from agents.schemas import AGENT_OUTPUT_SCHEMA
from agents.state import FounderState

from ..db.postgres import get_pool
from ..db.redis_client import publish

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/blueprints", tags=["blueprints"])

# Node name → state field it writes.
NODE_OUTPUT_FIELD = {
    "idea_refiner": "refined_idea",
    "market_analyst": "market_analysis",
    "legal_agent": "legal_compliance",
    "location_analyst": "location_analysis",
    "team_architect": "team_structure",
    "financial_planner": "financial_plan",
    "alternatives_optimizer": "alternatives",
    "report_synthesizer": "final_report",
    "critic": "critic",
}

# task_id → asyncio.Event for cancel support.
_cancel_events: dict[str, asyncio.Event] = {}


class BlueprintRequest(BaseModel):
    idea: str


def _serialize(obj) -> str:
    """Pydantic model → JSON string for DB / WS. None → empty string."""
    if obj is None:
        return ""
    if hasattr(obj, "model_dump_json"):
        return obj.model_dump_json(exclude_none=True)
    return str(obj)


async def _run_pipeline(blueprint_id: str, idea: str) -> None:
    pool = await get_pool()
    cancel = asyncio.Event()
    _cancel_events[blueprint_id] = cancel

    async def emit(event: dict[str, Any]) -> None:
        await publish(f"blueprint:{blueprint_id}", json.dumps(event, ensure_ascii=False))

    try:
        initial: FounderState = {
            "task_id": blueprint_id,
            "raw_input": idea,
            "agent_statuses": {},
            "metadata": {},
        }

        last_state: FounderState = initial
        async for step in founder_graph.astream(initial):
            if cancel.is_set():
                raise asyncio.CancelledError()

            node_name = next(iter(step))
            node_state: FounderState = step[node_name]
            last_state = {**last_state, **node_state}

            field = NODE_OUTPUT_FIELD.get(node_name)
            output_obj = node_state.get(field) if field else None
            output_json = _serialize(output_obj)
            narrative = getattr(output_obj, "narrative_md", "") if output_obj else ""

            meta = node_state.get("metadata", {}).get(node_name, {}) or {}
            status = node_state.get("agent_statuses", {}).get(node_name, "running")

            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO agent_runs
                        (blueprint_id, agent_name, status, duration_ms, tokens_used, model_used, output)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    uuid.UUID(blueprint_id),
                    node_name,
                    status,
                    meta.get("duration_ms"),
                    meta.get("tokens_used"),
                    meta.get("model_used"),
                    output_json[:50000],
                )

            await emit({
                "type": "agent_update",
                "agent": node_name,
                "status": status,
                "output": output_json[:4000],
                "narrative": narrative[:4000],
                "metadata": meta,
            })

        final_report = last_state.get("final_report")
        narrative = getattr(final_report, "narrative_md", "") if final_report else ""
        language = last_state.get("language", "en")

        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE blueprints SET status='completed', completed_at=NOW(), language=$2 WHERE id=$1",
                uuid.UUID(blueprint_id),
                language,
            )
            await conn.execute(
                "INSERT INTO reports (blueprint_id, content, language) VALUES ($1, $2, $3)",
                uuid.UUID(blueprint_id),
                narrative,
                language,
            )

        await emit({"type": "completed", "report": narrative})

    except asyncio.CancelledError:
        logger.info("Pipeline cancelled: %s", blueprint_id)
        async with (await get_pool()).acquire() as conn:
            await conn.execute(
                "UPDATE blueprints SET status='cancelled' WHERE id=$1",
                uuid.UUID(blueprint_id),
            )
        await emit({"type": "cancelled"})
    except Exception as exc:
        logger.exception("Pipeline failed for %s: %s", blueprint_id, exc)
        async with (await get_pool()).acquire() as conn:
            await conn.execute(
                "UPDATE blueprints SET status='error' WHERE id=$1",
                uuid.UUID(blueprint_id),
            )
        await emit({"type": "error", "message": str(exc)})
    finally:
        _cancel_events.pop(blueprint_id, None)


@router.post("", status_code=202)
async def create_blueprint(body: BlueprintRequest, background_tasks: BackgroundTasks):
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
    pool = await get_pool()
    async with pool.acquire() as conn:
        blueprint = await conn.fetchrow(
            "SELECT id, raw_input, language, status, created_at, completed_at FROM blueprints WHERE id=$1",
            uuid.UUID(blueprint_id),
        )
        if not blueprint:
            raise HTTPException(status_code=404, detail="blueprint not found")

        agent_runs = await conn.fetch(
            "SELECT agent_name, status, duration_ms, tokens_used, model_used, output "
            "FROM agent_runs WHERE blueprint_id=$1 ORDER BY id",
            uuid.UUID(blueprint_id),
        )
        report = await conn.fetchrow(
            "SELECT content, language FROM reports WHERE blueprint_id=$1 ORDER BY created_at DESC LIMIT 1",
            uuid.UUID(blueprint_id),
        )

    # Decode typed outputs back to dicts for the UI.
    typed_outputs: dict[str, Any] = {}
    for r in agent_runs:
        field = NODE_OUTPUT_FIELD.get(r["agent_name"])
        if field and r["output"]:
            try:
                typed_outputs[field] = json.loads(r["output"])
            except json.JSONDecodeError:
                typed_outputs[field] = {"narrative_md": r["output"]}

    return {
        "id": blueprint_id,
        "raw_input": blueprint["raw_input"],
        "language": blueprint["language"],
        "status": blueprint["status"],
        "created_at": blueprint["created_at"].isoformat(),
        "completed_at": blueprint["completed_at"].isoformat() if blueprint["completed_at"] else None,
        "agents": [
            {k: v for k, v in dict(r).items() if k != "output"} for r in agent_runs
        ],
        "outputs": typed_outputs,
        "report": report["content"] if report else None,
    }


@router.post("/{blueprint_id}/cancel", status_code=202)
async def cancel_blueprint(blueprint_id: str):
    event = _cancel_events.get(blueprint_id)
    if event is None:
        raise HTTPException(status_code=404, detail="blueprint not running")
    event.set()
    return {"status": "cancelling"}
