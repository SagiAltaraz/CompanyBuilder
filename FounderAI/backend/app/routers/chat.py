"""POST /blueprints/:id/chat — follow-up Q&A over the finished blueprint."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.client import MODELS, get_client

from ..db.postgres import get_pool

router = APIRouter(prefix="/blueprints", tags=["chat"])

SYSTEM_PROMPT = (
    "You are FounderAI, a strategic business advisor. The user has already generated a complete "
    "blueprint for their business, included below as reference. Answer their follow-up concisely "
    "and specifically — quote concrete numbers, names, and steps from the blueprint when relevant. "
    "If a question goes beyond the blueprint, give your best strategic advice and say so. "
    "Respond in the user's language. Use short lists and tables when they help."
)


class ChatRequest(BaseModel):
    message: str


@router.post("/{blueprint_id}/chat")
async def chat_with_blueprint(blueprint_id: str, body: ChatRequest):
    if not body.message.strip():
        raise HTTPException(status_code=422, detail="message cannot be empty")

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT content FROM reports WHERE blueprint_id=$1 ORDER BY created_at DESC LIMIT 1",
            uuid.UUID(blueprint_id),
        )
    if not row:
        raise HTTPException(status_code=404, detail="Blueprint report not found. Run the pipeline first.")

    client = get_client()
    resp = await client.messages.create(
        model=MODELS["haiku"],
        max_tokens=1024,
        temperature=0.3,
        system=[
            {"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": f"Blueprint document:\n\n{row['content'][:12000]}",
             "cache_control": {"type": "ephemeral"}},
        ],
        messages=[{"role": "user", "content": body.message}],
    )
    text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    return {"answer": text.strip()}
