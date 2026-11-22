"""Agent 4 — location / geographic strategy (Israel-focused)."""
from __future__ import annotations

from .client import call_structured
from .schemas import LocationStrategy, RefinedIdea
from .state import FounderState
from .utils import summarize_for_handoff

AGENT_KEY = "location_analyst"

CACHED_PREAMBLE = """You are the Location Analyst — agent 4 of the FounderAI pipeline. You decide where this business should operate.

First decision: set `is_physical` — true for cafés, studios, retail, clinics, carts, physical services that need foot traffic; false for pure online/SaaS/remote services.

For physical businesses: `top_options` = 3–5 real Israeli neighborhoods (not whole cities). Use real neighborhood names (Florentin, Rothschild, Neve Tzedek, Hadar, Kiryat Yovel, Talpiot, …). Include real rent_nis_per_sqm_month figures.

For online businesses: `top_options` = 3–5 geo markets/segments (e.g., "Tel Aviv tech workers", "Haifa engineering"), still using the same NeighborhoodOption shape — put the market name in `name`, the broader region in `city`, leave rent null, and use demand_score + competition_level to differentiate.

Rules:
- `recommended_index` points to the #1 option.
- `expansion_plan_md`: 3 stages (launch / month 6–12 / year 2+) in a short markdown.
- `narrative_md`: 200–350 word summary with a comparison table of the top options.
- Respond in the user's language.
"""


async def location_analyst_node(state: FounderState) -> dict:
    try:
        idea: RefinedIdea | None = state.get("refined_idea")
        language = state.get("language", "en")
        task = (
            f"User language: {language}.\n\n"
            f"Refined idea (JSON):\n{summarize_for_handoff(idea, 1200)}"
        )
        result, meta = await call_structured(
            role="sonnet",
            cached_preamble=CACHED_PREAMBLE,
            task_instruction=task,
            user_message="Produce the location strategy.",
            schema=LocationStrategy,
            tool_name="submit_location_strategy",
            max_tokens=2048,
        )
        return {
            "location_analysis": result,
            "agent_statuses": {AGENT_KEY: "done"},
            "metadata": {AGENT_KEY: meta},
        }
    except Exception as exc:
        return {
            "agent_statuses": {AGENT_KEY: "error"},
            "error": f"location_analyst: {exc}",
        }
