from typing import Annotated, TypedDict, Optional, Dict, Any


def _merge_dicts(a: dict, b: dict) -> dict:
    """Reducer for parallel nodes: merge dicts instead of last-writer-wins."""
    return {**a, **b}


class FounderState(TypedDict, total=False):
    task_id: str
    raw_input: str
    language: str

    # Agent outputs — each written by exactly one node, no conflict
    refined_idea: str
    market_analysis: str
    legal_compliance: str
    location_analysis: str
    team_structure: str
    financial_plan: str
    alternatives: str
    final_report: str

    current_agent: str
    # error uses last-writer-wins within parallel nodes; annotated to allow both writing
    error: Annotated[Optional[str], lambda a, b: b if b is not None else a]

    # These are written by multiple parallel nodes — use merge reducer
    agent_statuses: Annotated[Dict[str, str], _merge_dicts]
    metadata: Annotated[Dict[str, Any], _merge_dicts]
