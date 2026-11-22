"""Agent 7 — budget alternatives optimizer."""
from __future__ import annotations

from .client import call_structured
from .schemas import Alternatives, FinancialPlan, LegalCompliance, RefinedIdea, TeamPlan
from .state import FounderState
from .utils import summarize_for_handoff

CACHED_PREAMBLE = """You are the Alternatives Optimizer — agent 7 of the FounderAI pipeline. For every paid tool, service, and hire proposed upstream, you propose a cheaper alternative that delivers ≥75% of the value.

Rules:
- `cuts` covers at least these categories if the upstream mentions them: software, services (accountant/lawyer/insurance), hires (local → offshore where sensible), location (smaller/off-main-street), marketing.
- Every cut names a concrete `recommended` (what upstream picked) and a concrete `alternative` (named product/vendor/location). Always include a `trade_off` the founder must accept.
- `recommended_cost_nis_month` and `alternative_cost_nis_month` are monthly figures; either may be null for one-time items.
- `total_monthly_savings_nis` is the sum of (recommended - alternative) across categories where both are known.
- `narrative_md`: 200–350 words with a comparison table grouped by category and a one-line verdict at the end.
- Respond in the user's language.
"""


async def alternatives_optimizer_node(state: FounderState) -> dict:
    try:
        idea: RefinedIdea | None = state.get("refined_idea")
        team: TeamPlan | None = state.get("team_structure")
        finance: FinancialPlan | None = state.get("financial_plan")
        legal: LegalCompliance | None = state.get("legal_compliance")
        language = state.get("language", "en")

        task = (
            f"User language: {language}.\n\n"
            f"Refined idea:\n{summarize_for_handoff(idea, 600)}\n\n"
            f"Team (what to cut):\n{summarize_for_handoff(team, 1200)}\n\n"
            f"Financial plan (what to cut):\n{summarize_for_handoff(finance, 1200)}\n\n"
            f"Legal (providers):\n{summarize_for_handoff(legal, 800)}"
        )
        result, meta = await call_structured(
            role="sonnet",
            cached_preamble=CACHED_PREAMBLE,
            task_instruction=task,
            user_message="Produce the budget alternatives.",
            schema=Alternatives,
            tool_name="submit_alternatives",
            max_tokens=2048,
        )
        return {
            "alternatives": result,
            "current_agent": "alternatives_optimizer",
            "agent_statuses": {"alternatives_optimizer": "done"},
            "metadata": {"alternatives_optimizer": meta},
        }
    except Exception as exc:
        return {
            "current_agent": "alternatives_optimizer",
            "agent_statuses": {"alternatives_optimizer": "error"},
            "error": f"alternatives_optimizer: {exc}",
        }
