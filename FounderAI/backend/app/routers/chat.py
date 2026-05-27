"""
POST /blueprints/:id/chat
Allows the user to ask follow-up questions about their blueprint.
Uses the full report as context.
"""
from __future__ import annotations

import uuid
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..db.postgres import get_pool

router = APIRouter(prefix="/blueprints", tags=["chat"])

CHAT_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You are FounderAI, a strategic business advisor. You have already produced a comprehensive "
    "company blueprint for the user's business. The full blueprint is provided below.\n\n"
    "Answer the user's follow-up questions concisely and specifically — always reference concrete "
    "numbers, names, or steps from the blueprint. If the blueprint doesn't cover something, "
    "give your best strategic advice and say you're advising beyond the blueprint.\n"
    "Use the same language as the user's question (Hebrew or English).\n"
    "Format your answer clearly — use bullet points or numbered lists when listing steps.\n\n"
    "Blueprint:\n{report}"
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

    report_text = row["content"]
    system = SYSTEM_PROMPT.format(report=report_text[:8000])  # cap to stay in context

    llm = ChatOpenAI(model=CHAT_MODEL, temperature=0.3, max_tokens=800)
    response = await llm.ainvoke([
        SystemMessage(content=system),
        HumanMessage(content=body.message),
    ])

    return {"answer": response.content.strip()}
