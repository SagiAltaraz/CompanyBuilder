"""
FounderAI — LangGraph pipeline with parallel execution.

Agents 2 (market_analyst), 3 (legal_compliance), and 4 (location_analyst)
run in parallel after Agent 1 (idea_refiner) completes. LangGraph merges
their state automatically before Agent 5 (team_architect) begins.
"""
from langgraph.graph import StateGraph, START, END

from .state import FounderState
from .idea_refiner import idea_refiner_node
from .market_analyst import market_analyst_node
from .legal_compliance import legal_compliance_node
from .location_analyst import location_analyst_node
from .team_architect import team_architect_node
from .financial_planner import financial_planner_node
from .alternatives_optimizer import alternatives_optimizer_node
from .report_synthesizer import report_synthesizer_node


def build_founder_graph():
    """Build and compile the FounderAI agent graph."""
    graph = StateGraph(FounderState)

    # Register all nodes
    graph.add_node("idea_refiner", idea_refiner_node)
    graph.add_node("market_analyst", market_analyst_node)
    graph.add_node("legal_agent", legal_compliance_node)
    graph.add_node("location_analyst", location_analyst_node)
    graph.add_node("team_architect", team_architect_node)
    graph.add_node("financial_planner", financial_planner_node)
    graph.add_node("alternatives_optimizer", alternatives_optimizer_node)
    graph.add_node("report_synthesizer", report_synthesizer_node)

    # Linear start → idea_refiner
    graph.add_edge(START, "idea_refiner")

    # Parallel fork: 3 agents run simultaneously after idea_refiner
    graph.add_edge("idea_refiner", "market_analyst")
    graph.add_edge("idea_refiner", "legal_agent")
    graph.add_edge("idea_refiner", "location_analyst")

    # All 3 converge into team_architect (LangGraph waits for all before running)
    graph.add_edge("market_analyst", "team_architect")
    graph.add_edge("legal_agent", "team_architect")
    graph.add_edge("location_analyst", "team_architect")

    # Linear tail
    graph.add_edge("team_architect", "financial_planner")
    graph.add_edge("financial_planner", "alternatives_optimizer")
    graph.add_edge("alternatives_optimizer", "report_synthesizer")
    graph.add_edge("report_synthesizer", END)

    return graph.compile()


# Singleton compiled graph — import and use directly
founder_graph = build_founder_graph()
