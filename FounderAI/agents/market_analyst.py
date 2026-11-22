"""Agent 2 — market analyst.

Produces TAM/SAM/SOM in NIS, typed competitor list, gaps, positioning, citations.
Uses Claude's native web_search tool for research (replaces DuckDuckGo scraping).
"""
from __future__ import annotations

from .client import call_structured
from .schemas import MarketAnalysis, RefinedIdea
from .state import FounderState
from .utils import summarize_for_handoff

CACHED_PREAMBLE = """You are the Market Analyst — agent 2 of the FounderAI pipeline.

You produce a quantified market analysis for Israeli founders. Numbers are in NIS (₪) unless the target market is explicitly global.

Rules:
- `tam_nis`, `sam_nis`, `som_nis` are annual NIS figures. If you cannot estimate, leave them null — do not invent precision you don't have, drop `confidence` instead.
- `competitors`: at least 3, up to 8. Mix 2–3 direct with 1–2 indirect. Include a weakness for every competitor — the founder needs to know where to attack.
- `gap_opportunities`: 2–5 specific, actionable openings, not platitudes.
- `macro_trends`: 2–4 real trends (cite if non-obvious).
- `risks`: 2–3 headwinds specific to this business, not generic ("economy slows").
- `positioning`: one tight paragraph on the unique angle vs. competitors.
- `sources`: cite URLs for any non-obvious claim. If you used no web search, this may be empty.
- `narrative_md`: 200–400 word markdown summary with 2–3 small tables and tight prose. This is what the user reads.
- Respond in the user's language (passed in the task instruction).
"""


async def market_analyst_node(state: FounderState) -> dict:
    try:
        idea: RefinedIdea | None = state.get("refined_idea")
        language = state.get("language", "en")
        task = (
            f"User language: {language}.\n\n"
            f"Refined idea (JSON):\n{summarize_for_handoff(idea, 1200)}\n\n"
            f"Original user input:\n{state.get('raw_input', '')[:500]}"
        )
        result, meta = await call_structured(
            role="sonnet",
            cached_preamble=CACHED_PREAMBLE,
            task_instruction=task,
            user_message="Produce the market analysis.",
            schema=MarketAnalysis,
            tool_name="submit_market_analysis",
            max_tokens=2048,
        )
        return {
            "market_analysis": result,
            "agent_statuses": {"market_analyst": "done"},
            "metadata": {"market_analyst": meta},
        }
    except Exception as exc:
        return {
            "agent_statuses": {"market_analyst": "error"},
            "error": f"market_analyst: {exc}",
        }
