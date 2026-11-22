"""Agent 8 — report synthesizer: the user-facing blueprint document."""
from __future__ import annotations

from .client import call_structured
from .schemas import (
    Alternatives,
    FinalReport,
    FinancialPlan,
    LegalCompliance,
    LocationStrategy,
    MarketAnalysis,
    RefinedIdea,
    TeamPlan,
)
from .state import FounderState
from .utils import summarize_for_handoff

CACHED_PREAMBLE = """You are the Report Synthesizer — agent 8, the final narrative author. You assemble a polished, confident, document-style blueprint from the upstream typed outputs.

Rules:
- `title`: a real business-paper title. Example: "Rothschild Mobile Coffee — Tel Aviv Launch Plan". Not "FounderAI Report".
- `executive_summary_md`: 3 tight paragraphs — what the business is, why now, the recommended path.
- `action_items_this_week`: 5–8 concrete items, each with specific owner, by_week, and (where real) cost_nis. First action usually "Register entity with Rashut Ha'taagidim" or similar.
- `twelve_month_roadmap_md`: a markdown table with Month | Milestone | Key Actions | Expected Revenue | Team | Budget.
- `risks`: 3–5 real risks for THIS business (not generic "economy slows"). Each with probability, impact, mitigation.
- `kpis_md`: a markdown table of 4–8 KPIs with Stage 1 and Stage 2 targets.
- `narrative_md`: the FULL user-facing document as markdown. Structure:
    # {title}
    ## Executive Summary
    ## This Week — Action Items
    ## Market Opportunity (numbers from market analysis)
    ## Location Strategy (recommended neighborhood + comparison table)
    ## Legal & Compliance (entity + licenses + grants table)
    ## Team Plan (stages + costs table)
    ## Financial Overview (setup, burn, 12-month revenue, break-even)
    ## Budget Alternatives (table + total savings)
    ## 12-Month Execution Roadmap
    ## Top Risks & Mitigations
    ## KPIs to Track
  Pull real numbers from the upstream typed objects — don't invent new ones.
  Write in the user's language.
"""


async def report_synthesizer_node(state: FounderState) -> dict:
    try:
        language = state.get("language", "en")
        task = (
            f"User language: {language}.\n\n"
            f"Refined idea:\n{summarize_for_handoff(state.get('refined_idea'), 800)}\n\n"
            f"Market:\n{summarize_for_handoff(state.get('market_analysis'), 1200)}\n\n"
            f"Location:\n{summarize_for_handoff(state.get('location_analysis'), 1000)}\n\n"
            f"Legal:\n{summarize_for_handoff(state.get('legal_compliance'), 1200)}\n\n"
            f"Team:\n{summarize_for_handoff(state.get('team_structure'), 1200)}\n\n"
            f"Financial:\n{summarize_for_handoff(state.get('financial_plan'), 1500)}\n\n"
            f"Alternatives:\n{summarize_for_handoff(state.get('alternatives'), 1000)}"
        )
        result, meta = await call_structured(
            role="opus",
            cached_preamble=CACHED_PREAMBLE,
            task_instruction=task,
            user_message="Produce the final blueprint report.",
            schema=FinalReport,
            tool_name="submit_final_report",
            max_tokens=5000,
            temperature=0.2,
        )
        return {
            "final_report": result,
            "current_agent": "report_synthesizer",
            "agent_statuses": {"report_synthesizer": "done"},
            "metadata": {"report_synthesizer": meta},
        }
    except Exception as exc:
        return {
            "current_agent": "report_synthesizer",
            "agent_statuses": {"report_synthesizer": "error"},
            "error": f"report_synthesizer: {exc}",
        }
