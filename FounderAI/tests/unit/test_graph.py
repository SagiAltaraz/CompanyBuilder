"""Smoke tests for the compiled LangGraph.

We don't exercise the LLM here — we just confirm the topology is what we
designed: critic runs in parallel with the synthesizer, team_architect
waits for the three parallel research agents, etc.
"""
from __future__ import annotations

from agents.graph import build_founder_graph, founder_graph


def test_graph_compiles():
    assert founder_graph is not None


def test_graph_has_all_nodes():
    g = build_founder_graph().get_graph()
    nodes = set(g.nodes.keys())
    for expected in [
        "idea_refiner", "market_analyst", "legal_agent", "location_analyst",
        "team_architect", "financial_planner", "alternatives_optimizer",
        "report_synthesizer", "critic",
    ]:
        assert expected in nodes, f"missing node: {expected}"


def test_graph_fan_out_from_idea_refiner():
    g = build_founder_graph().get_graph()
    targets = {e.target for e in g.edges if e.source == "idea_refiner"}
    assert {"market_analyst", "legal_agent", "location_analyst"}.issubset(targets)


def test_critic_parallel_with_synthesizer():
    g = build_founder_graph().get_graph()
    from_alts = {e.target for e in g.edges if e.source == "alternatives_optimizer"}
    assert {"report_synthesizer", "critic"}.issubset(from_alts)
