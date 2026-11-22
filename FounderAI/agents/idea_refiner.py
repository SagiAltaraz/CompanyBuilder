"""Agent 1 — idea refiner.

Reads raw user input, returns a typed RefinedIdea: concept, industry, model,
target market, stage, detected language, confidence, open questions.
"""
from __future__ import annotations

from .client import call_structured
from .schemas import RefinedIdea
from .state import FounderState
from .utils import detect_language

CACHED_PREAMBLE = """You are the Idea Refiner — the first agent in the FounderAI pipeline for Israeli founders.

Your single job: take raw user input (one sentence to a paragraph, Hebrew or English) and classify it into a strict structured form so every downstream agent has unambiguous inputs.

Rules:
- Pick exactly ONE enum value for each field. If the input is genuinely ambiguous, pick the most likely value and lower `confidence`.
- `concept` is ONE sentence, the clearest reading of what the business is.
- `industry` is a short noun phrase (e.g., "F&B mobile cart", "digital marketing for SMB"). Not a sector code.
- `open_questions` are the 1–4 things you'd ask the founder next to make the plan sharper. Leave empty only when the input is already specific.
- `narrative_md` is a 3–5 line markdown summary: the concept, the model, the market, and the top open question. This is what the user reads.
- Respond in the SAME language as the input (detected and returned as `language`).
"""


async def idea_refiner_node(state: FounderState) -> dict:
    try:
        raw = state["raw_input"]
        language_hint = detect_language(raw)
        task = f"Language hint from heuristic: {language_hint}. Trust the hint unless the text is clearly in the other language."

        result, meta = await call_structured(
            role="haiku",
            cached_preamble=CACHED_PREAMBLE,
            task_instruction=task,
            user_message=raw,
            schema=RefinedIdea,
            tool_name="submit_refined_idea",
            max_tokens=1024,
        )
        return {
            "refined_idea": result,
            "language": result.language,
            "current_agent": "idea_refiner",
            "agent_statuses": {"idea_refiner": "done"},
            "metadata": {"idea_refiner": meta},
        }
    except Exception as exc:
        return {
            "current_agent": "idea_refiner",
            "agent_statuses": {"idea_refiner": "error"},
            "error": f"idea_refiner: {exc}",
        }
