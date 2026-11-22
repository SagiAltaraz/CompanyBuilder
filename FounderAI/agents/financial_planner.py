"""Agent 6 — financial planner (hardest numerical reasoning → Opus)."""
from __future__ import annotations

from .client import call_structured
from .schemas import (
    FinancialPlan,
    LegalCompliance,
    LocationStrategy,
    MarketAnalysis,
    RefinedIdea,
    TeamPlan,
)
from .state import FounderState
from .utils import summarize_for_handoff

CACHED_PREAMBLE = """You are the Financial Planner — agent 6 of the FounderAI pipeline. You produce quantified startup finances in NIS (₪). This is the most numerically load-bearing section.

Hard rules:
- `startup_cost_low_nis` ≤ `startup_cost_high_nis`. Both include company registration, legal, first accountant setup, equipment, licenses, deposits, branding, first marketing push, 10% reserve.
- Monthly burns INCLUDE salaries (use the TeamPlan stage totals directly; do not recompute). Burn also includes rent (from LocationStrategy #1 pick if physical), software, marketing, utilities, accounting, insurance, 10% buffer.
- `monthly_burn_stage1_nis` ≤ `monthly_burn_stage2_nis` ≤ `monthly_burn_stage3_nis`.
- `runway_months_at_100k_usd`: assume ₪370,000 starting capital, divide by stage1 burn.
- `revenue_monthly_nis_12mo`: exactly 12 entries. Be CONSERVATIVE. Start at ₪0 or small and ramp. Last-month revenue must be ≤ SOM / 12 (if SOM is given).
- `break_even_month`: first month where cumulative revenue ≥ cumulative burn. Null if not reached in 12.
- `assumptions`: 3–6 bullets stating the big assumptions (price per unit, customers per month, conversion rate). The critic will check these against market.
- `narrative_md`: 300–500 words, with a setup-cost table, a burn table (3 stages), and a short P&L narrative. No vague ranges; give numbers.
- Respond in the user's language.
"""


async def financial_planner_node(state: FounderState) -> dict:
    try:
        idea: RefinedIdea | None = state.get("refined_idea")
        market: MarketAnalysis | None = state.get("market_analysis")
        legal: LegalCompliance | None = state.get("legal_compliance")
        location: LocationStrategy | None = state.get("location_analysis")
        team: TeamPlan | None = state.get("team_structure")
        language = state.get("language", "en")

        task = (
            f"User language: {language}.\n\n"
            f"Refined idea:\n{summarize_for_handoff(idea, 800)}\n\n"
            f"Market:\n{summarize_for_handoff(market, 1200)}\n\n"
            f"Legal:\n{summarize_for_handoff(legal, 800)}\n\n"
            f"Location:\n{summarize_for_handoff(location, 800)}\n\n"
            f"Team:\n{summarize_for_handoff(team, 1500)}"
        )
        result, meta = await call_structured(
            role="opus",
            cached_preamble=CACHED_PREAMBLE,
            task_instruction=task,
            user_message="Produce the financial plan.",
            schema=FinancialPlan,
            tool_name="submit_financial_plan",
            max_tokens=3000,
        )
        return {
            "financial_plan": result,
            "current_agent": "financial_planner",
            "agent_statuses": {"financial_planner": "done"},
            "metadata": {"financial_planner": meta},
        }
    except Exception as exc:
        return {
            "current_agent": "financial_planner",
            "agent_statuses": {"financial_planner": "error"},
            "error": f"financial_planner: {exc}",
        }
