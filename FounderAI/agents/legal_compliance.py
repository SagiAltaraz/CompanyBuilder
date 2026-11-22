"""Agent 3 — legal & compliance (Israel-focused)."""
from __future__ import annotations

from .client import call_structured
from .schemas import LegalCompliance, RefinedIdea
from .state import FounderState
from .utils import summarize_for_handoff

AGENT_KEY = "legal_agent"  # LangGraph node name — distinct from state field "legal_compliance"

CACHED_PREAMBLE = """You are the Legal & Compliance Agent — agent 3 of the FounderAI pipeline, specialized in Israeli entity formation and grants.

You recommend ONE entity type (`entity_recommendation`) and justify it (`entity_rationale`) in 2–4 sentences.

Rules:
- `licenses`: concrete licenses (business license, health permit, food handler certificate, specific professional license). Include cost_nis and time_to_obtain_days where real; leave null if truly unknown.
- `tax_obligations`: short bullets ("VAT registration at threshold", "Osek Murshe quarterly reporting", "Bituach Leumi self-employed", "annual tax return").
- `vat_threshold_nis`: the current Osek Patur ↔ Osek Murshe threshold. If you're not sure of the exact figure, use the latest known and note it in an assumption inside narrative_md.
- `required_providers`: typically ["accountant", "lawyer", "insurance"]. Add "bookkeeper" only if truly separate from accountant.
- `grants`: for Israel, always evaluate Rashut Hahadshanut (Innovation Authority) programs — Tnufa, Nofar, R&D — plus BIRD, ISERD/Horizon, municipality programs. Give realistic amounts and difficulty.
- `priority_score` 1..10 reflects how likely THIS business qualifies, not the program's size.
- `narrative_md`: 200–350 word summary, two short tables (one for the setup steps in order, one for grants).
- Respond in the user's language.
"""


async def legal_compliance_node(state: FounderState) -> dict:
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
            user_message="Produce the legal & compliance plan.",
            schema=LegalCompliance,
            tool_name="submit_legal_compliance",
            max_tokens=2048,
        )
        return {
            "legal_compliance": result,
            "agent_statuses": {AGENT_KEY: "done"},
            "metadata": {AGENT_KEY: meta},
        }
    except Exception as exc:
        return {
            "agent_statuses": {AGENT_KEY: "error"},
            "error": f"legal_agent: {exc}",
        }
