"""FounderAI — LangGraph pipeline.

Topology:
    START → idea_refiner
          ├─► market_analyst ─┐
          ├─► legal_agent    ─┼─► team_architect ─► financial_planner ─► alternatives_optimizer ─┐
          └─► location_analyst┘                                                                   ├─► report_synthesizer ─► END
                                                                                                  └─► critic ────────────► END

The critic runs in parallel with the synthesizer — both consume the full
upstream state, neither writes a field the other needs.
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from .alternatives_optimizer import alternatives_optimizer_node
from .critic import critic_node
from .financial_planner import financial_planner_node
from .idea_refiner import idea_refiner_node
from .legal_compliance import legal_compliance_node
from .location_analyst import location_analyst_node
from .market_analyst import market_analyst_node
from .report_synthesizer import report_synthesizer_node
from .state import FounderState
from .team_architect import team_architect_node


def build_founder_graph():
    g = StateGraph(FounderState)

    g.add_node("idea_refiner", idea_refiner_node)
    g.add_node("market_analyst", market_analyst_node)
    g.add_node("legal_agent", legal_compliance_node)
    g.add_node("location_analyst", location_analyst_node)
    g.add_node("team_architect", team_architect_node)
    g.add_node("financial_planner", financial_planner_node)
    g.add_node("alternatives_optimizer", alternatives_optimizer_node)
    g.add_node("report_synthesizer", report_synthesizer_node)
    g.add_node("critic", critic_node)

    g.add_edge(START, "idea_refiner")

    # Parallel fan-out
    g.add_edge("idea_refiner", "market_analyst")
    g.add_edge("idea_refiner", "legal_agent")
    g.add_edge("idea_refiner", "location_analyst")

    # Fan-in at team_architect
    g.add_edge("market_analyst", "team_architect")
    g.add_edge("legal_agent", "team_architect")
    g.add_edge("location_analyst", "team_architect")

    g.add_edge("team_architect", "financial_planner")
    g.add_edge("financial_planner", "alternatives_optimizer")

    # Parallel final pair: synthesizer + critic
    g.add_edge("alternatives_optimizer", "report_synthesizer")
    g.add_edge("alternatives_optimizer", "critic")

    g.add_edge("report_synthesizer", END)
    g.add_edge("critic", END)

    return g.compile()


founder_graph = build_founder_graph()
