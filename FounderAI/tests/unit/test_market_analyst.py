"""Unit tests for Agent 2: Market Analyst."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from agents.market_analyst import market_analyst_node
from tests.conftest import make_state

MOCK_MARKET_OUTPUT = (
    "## Market Size\n"
    "- TAM: $10B global restaurant software\n"
    "- SAM: $500M Israel + MENA region\n"
    "- SOM: $5M realistic first 2 years\n\n"
    "## Competitors\n"
    "| Competitor | Price | Strength | Weakness |\n"
    "|---|---|---|---|\n"
    "| Toast | $69/mo | US market leader | No Hebrew support |\n"
    "| Square | $60/mo | Easy setup | Limited features |\n"
)


def _mock_response(text: str):
    msg = MagicMock()
    msg.content = text
    msg.response_metadata = {"token_usage": {"total_tokens": 300}}
    return msg


@pytest.mark.asyncio
async def test_market_analyst_sets_market_analysis(state_after_refine):
    with (
        patch("agents.market_analyst.ChatOpenAI") as MockLLM,
        patch("agents.market_analyst.duckduckgo_search", return_value=["Market growing 25% YoY"]),
    ):
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_MARKET_OUTPUT))
        result = await market_analyst_node(state_after_refine)

    assert result["market_analysis"] != ""
    assert "Market Size" in result["market_analysis"]


@pytest.mark.asyncio
async def test_market_analyst_uses_search(state_after_refine):
    search_called_with = []

    def fake_search(query, max_results=4):
        search_called_with.append((query, max_results))
        return ["Result 1", "Result 2"]

    with (
        patch("agents.market_analyst.ChatOpenAI") as MockLLM,
        patch("agents.market_analyst.duckduckgo_search", side_effect=fake_search),
    ):
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_MARKET_OUTPUT))
        await market_analyst_node(state_after_refine)

    assert len(search_called_with) == 1
    _, max_r = search_called_with[0]
    assert max_r <= 4  # token-efficiency cap


@pytest.mark.asyncio
async def test_market_analyst_status_done(state_after_refine):
    with (
        patch("agents.market_analyst.ChatOpenAI") as MockLLM,
        patch("agents.market_analyst.duckduckgo_search", return_value=[]),
    ):
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_MARKET_OUTPUT))
        result = await market_analyst_node(state_after_refine)

    assert result["agent_statuses"]["market_analyst"] == "done"


@pytest.mark.asyncio
async def test_market_analyst_handles_error(state_after_refine):
    with (
        patch("agents.market_analyst.ChatOpenAI") as MockLLM,
        patch("agents.market_analyst.duckduckgo_search", return_value=[]),
    ):
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(side_effect=Exception("rate limit"))
        with pytest.raises(Exception):
            await market_analyst_node(state_after_refine)

    assert state_after_refine["agent_statuses"]["market_analyst"] == "error"
