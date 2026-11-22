"""LangGraph state for the FounderAI pipeline.

Every agent writes exactly one typed field; agent_statuses and metadata are
merged across parallel nodes via `_merge_dicts`. Error is last-writer-wins so
any parallel branch can surface a failure.
"""
from __future__ import annotations

from typing import Annotated, Any, Optional, TypedDict

from .schemas import (
    Alternatives,
    CriticReport,
    FinalReport,
    FinancialPlan,
    LegalCompliance,
    LocationStrategy,
    MarketAnalysis,
    RefinedIdea,
    TeamPlan,
)


def _merge_dicts(a: dict, b: dict) -> dict:
    """Reducer for parallel nodes: merge instead of last-writer-wins."""
    return {**a, **b}


class FounderState(TypedDict, total=False):
    task_id: str
    raw_input: str
    language: str

    # Typed outputs — each written by exactly one node, no conflict.
    refined_idea: Optional[RefinedIdea]
    market_analysis: Optional[MarketAnalysis]
    legal_compliance: Optional[LegalCompliance]
    location_analysis: Optional[LocationStrategy]
    team_structure: Optional[TeamPlan]
    financial_plan: Optional[FinancialPlan]
    alternatives: Optional[Alternatives]
    final_report: Optional[FinalReport]
    critic: Optional[CriticReport]

    current_agent: str
    error: Annotated[Optional[str], lambda a, b: b if b is not None else a]

    # Written by multiple parallel nodes — merge reducer.
    agent_statuses: Annotated[dict[str, str], _merge_dicts]
    metadata: Annotated[dict[str, Any], _merge_dicts]
