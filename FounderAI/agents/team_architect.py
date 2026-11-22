"""Agent 5 — team architect: hiring plan with Israeli salary data."""
from __future__ import annotations

from .client import call_structured
from .schemas import LegalCompliance, LocationStrategy, MarketAnalysis, RefinedIdea, TeamPlan
from .state import FounderState
from .utils import summarize_for_handoff

CACHED_PREAMBLE = """You are the Team Architect — agent 5 of the FounderAI pipeline. You produce a concrete hiring plan with realistic Israeli monthly costs.

Rules:
- `hires` is a chronological list from month 0 forward. The founder is always the first entry (role="Founder", seniority=lead, employment_type="founder", monthly_cost_nis=0 in bootstrap). Every other hire has a specific `hire_month` ≥ 0.
- `monthly_cost_nis` is total cost to the business, not gross salary: for employees add ~25% employer overhead on top of gross (Bituach Leumi, pension, severance reserve). For freelancers use effective monthly spend.
- `employment_type`: "founder" | "employee" | "freelancer" | "offshore".
- `stage1_monthly_cost_nis` is months 0–6, `stage2` is 6–18, `stage3` is 18–36. Sum of `hires` active in each stage.
- `employer_overhead_pct` stays around 0.25 for Israel unless you justify otherwise.
- `narrative_md`: 250–450 words with a stage table and a note on which roles should start offshore vs. local.
- Respond in the user's language.

Use the typed Market, Legal, and Location inputs directly — specifically:
- Team size should match the SOM in year 1–2 (don't plan a team that can't be supported by target revenue).
- If `legal.entity_recommendation` is sole_proprietor, assume the founder stays technical/operational longer.
- If `location.is_physical` is true, include a store/location manager hire at month 1–3.
"""


async def team_architect_node(state: FounderState) -> dict:
    try:
        idea: RefinedIdea | None = state.get("refined_idea")
        market: MarketAnalysis | None = state.get("market_analysis")
        legal: LegalCompliance | None = state.get("legal_compliance")
        location: LocationStrategy | None = state.get("location_analysis")
        language = state.get("language", "en")

        task = (
            f"User language: {language}.\n\n"
            f"Refined idea:\n{summarize_for_handoff(idea, 800)}\n\n"
            f"Market:\n{summarize_for_handoff(market, 1200)}\n\n"
            f"Legal:\n{summarize_for_handoff(legal, 1200)}\n\n"
            f"Location:\n{summarize_for_handoff(location, 800)}"
        )
        result, meta = await call_structured(
            role="sonnet",
            cached_preamble=CACHED_PREAMBLE,
            task_instruction=task,
            user_message="Produce the team plan.",
            schema=TeamPlan,
            tool_name="submit_team_plan",
            max_tokens=2048,
        )
        return {
            "team_structure": result,
            "current_agent": "team_architect",
            "agent_statuses": {"team_architect": "done"},
            "metadata": {"team_architect": meta},
        }
    except Exception as exc:
        return {
            "current_agent": "team_architect",
            "agent_statuses": {"team_architect": "error"},
            "error": f"team_architect: {exc}",
        }
