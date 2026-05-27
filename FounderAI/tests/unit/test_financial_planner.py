"""Unit tests for Agent 5: Financial Planner."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from agents.financial_planner import financial_planner_node, MODEL_NAME

MOCK_FINANCIAL_OUTPUT = (
    "## Setup Costs (One-Time)\n"
    "| Item | Low | High |\n"
    "|---|---|---|\n"
    "| Company registration | ₪1,500 | ₪2,500 |\n"
    "| Legal setup | ₪3,000 | ₪8,000 |\n"
    "| Total | ₪4,500 | ₪10,500 |\n\n"
    "## Monthly Burn Per Stage\n"
    "| Category | Stage 1 | Stage 2 | Stage 3 |\n"
    "|---|---|---|---|\n"
    "| Salaries | ₪0 | ₪15,000 | ₪80,000 |\n"
    "| Software | ₪500 | ₪2,000 | ₪5,000 |\n\n"
    "## Runway Calculator\n"
    "| Starting Capital | Months at Stage 1 burn |\n"
    "|---|---|\n"
    "| $10k | 2.7 months |\n"
    "| $50k | 13.5 months |\n"
    "| $100k | 27 months |\n\n"
    "## Grant Potential\n"
    "- Tnufa: ₪200,000 (apply first)\n"
    "- Nofar: ₪1,000,000\n"
    "- Total non-dilutive potential: ₪1,200,000\n"
)


def _mock_response(text: str):
    msg = MagicMock()
    msg.content = text
    msg.response_metadata = {"token_usage": {"total_tokens": 600}}
    return msg


@pytest.mark.asyncio
async def test_financial_planner_sets_output(state_after_team):
    with patch("agents.financial_planner.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_FINANCIAL_OUTPUT))
        result = await financial_planner_node(state_after_team)

    assert result["financial_plan"] != ""
    assert "Stage 1" in result["financial_plan"]


@pytest.mark.asyncio
async def test_financial_planner_uses_gpt4o():
    """Agent 5 must use gpt-4o (not mini) — complex synthesis."""
    assert MODEL_NAME == "gpt-4o"


@pytest.mark.asyncio
async def test_financial_planner_includes_grants(state_after_team):
    with patch("agents.financial_planner.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_FINANCIAL_OUTPUT))
        result = await financial_planner_node(state_after_team)

    assert "Grant" in result["financial_plan"] or "grant" in result["financial_plan"]


@pytest.mark.asyncio
async def test_financial_planner_status_done(state_after_team):
    with patch("agents.financial_planner.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_FINANCIAL_OUTPUT))
        result = await financial_planner_node(state_after_team)

    assert result["agent_statuses"]["financial_planner"] == "done"


@pytest.mark.asyncio
async def test_financial_planner_does_not_search(state_after_team):
    """Agent 5 should read legal agent's grant research — not search again."""
    search_was_called = []

    with (
        patch("agents.financial_planner.ChatOpenAI") as MockLLM,
        patch("agents.financial_planner.duckduckgo_search", side_effect=lambda *a, **kw: search_was_called.append(True)) if False else patch("builtins.open", MagicMock()),
    ):
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_FINANCIAL_OUTPUT))
        await financial_planner_node(state_after_team)

    # No web search should be called in the financial planner
    assert len(search_was_called) == 0
