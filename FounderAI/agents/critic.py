"""Agent 9 — critic. Runs in parallel with the synthesizer.

Reads every upstream typed output and checks numerical/logical consistency.
Produces a list of Issues (info / warn / block). The frontend renders these
as flags next to the relevant section; a 'block' issue is a hard contradiction
that should prompt the user to regenerate.
"""
from __future__ import annotations

from .client import call_structured
from .schemas import CriticReport, Issue
from .state import FounderState
from .utils import summarize_for_handoff

CACHED_PREAMBLE = """You are the Critic — the final agent of the FounderAI pipeline. You do not generate new strategy; you verify the consistency of the plan the other agents produced.

Check at minimum:
1. Market vs Finance: last-month revenue projection should not exceed market SOM/12. Flag "warn" if it does. If assumptions imply more customers than the market has, flag "block".
2. Legal vs Team: if entity_recommendation is sole_proprietor, team should be small (≤3 employees); otherwise flag "info".
3. Location vs Team: if location.is_physical and there's no on-site role in team.hires, flag "warn".
4. Finance internal: startup_cost_low ≤ startup_cost_high; stage1_burn ≤ stage2_burn ≤ stage3_burn. Flag any violation "block".
5. Finance vs Alternatives: if total_monthly_savings_nis > 0.5 * monthly_burn_stage1_nis, the baseline plan is probably bloated — flag "info".
6. Currency/unit coherence: all NIS fields should be positive, revenue arrays have length 12. Flag "block" if any is wrong.

Rules:
- `issues`: at most 12. Only real issues — do not fill it with filler. Empty is fine if the plan is clean.
- `overall_confidence`: 0..1, calibrated. 0.9 is "very confident this plan is internally consistent", 0.5 is "has issues worth another pass".
- `summary`: 2–4 sentences, plain language.
- Respond in the user's language.
"""


async def critic_node(state: FounderState) -> dict:
    try:
        language = state.get("language", "en")
        task = (
            f"User language: {language}.\n\n"
            f"Refined:\n{summarize_for_handoff(state.get('refined_idea'), 600)}\n\n"
            f"Market:\n{summarize_for_handoff(state.get('market_analysis'), 1200)}\n\n"
            f"Legal:\n{summarize_for_handoff(state.get('legal_compliance'), 1000)}\n\n"
            f"Location:\n{summarize_for_handoff(state.get('location_analysis'), 1000)}\n\n"
            f"Team:\n{summarize_for_handoff(state.get('team_structure'), 1200)}\n\n"
            f"Financial:\n{summarize_for_handoff(state.get('financial_plan'), 1500)}\n\n"
            f"Alternatives:\n{summarize_for_handoff(state.get('alternatives'), 1000)}"
        )
        result, meta = await call_structured(
            role="sonnet",
            cached_preamble=CACHED_PREAMBLE,
            task_instruction=task,
            user_message="Produce the critic report.",
            schema=CriticReport,
            tool_name="submit_critic_report",
            max_tokens=2048,
        )
        return {
            "critic": result,
            "agent_statuses": {"critic": "done"},
            "metadata": {"critic": meta},
        }
    except Exception as exc:
        return {
            "agent_statuses": {"critic": "error"},
            "error": f"critic: {exc}",
        }
