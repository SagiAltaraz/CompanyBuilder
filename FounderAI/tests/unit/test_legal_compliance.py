"""Unit tests for Agent 3: Legal & Compliance."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from agents.legal_compliance import legal_compliance_node
from tests.conftest import make_state

MOCK_LEGAL_OUTPUT = (
    "## Company Structure Options\n"
    "| Structure | Setup Cost | Tax | Liability |\n"
    "|---|---|---|---|\n"
    "| עוסק מורשה | ₪0 | Personal income tax | None |\n"
    "| חברה בע\"מ | ₪2,500 | 23% corporate tax | Protected |\n\n"
    "## Grants\n"
    "| Program | Amount | Provider | Difficulty |\n"
    "|---|---|---|---|\n"
    "| Tnufa | ₪200,000 | Innovation Authority | Medium |\n"
    "| Nofar | ₪1,000,000 | Innovation Authority | Hard |\n"
)


def _mock_response(text: str):
    msg = MagicMock()
    msg.content = text
    msg.response_metadata = {"token_usage": {"total_tokens": 400}}
    return msg


@pytest.mark.asyncio
async def test_legal_compliance_sets_output(state_after_refine):
    with (
        patch("agents.legal_compliance.ChatOpenAI") as MockLLM,
        patch("agents.legal_compliance.duckduckgo_search", return_value=["Israel VAT threshold 100k ILS"]),
    ):
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_LEGAL_OUTPUT))
        result = await legal_compliance_node(state_after_refine)

    assert result["legal_compliance"] != ""


@pytest.mark.asyncio
async def test_legal_compliance_mentions_grants(state_after_refine):
    with (
        patch("agents.legal_compliance.ChatOpenAI") as MockLLM,
        patch("agents.legal_compliance.duckduckgo_search", return_value=[]),
    ):
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_LEGAL_OUTPUT))
        result = await legal_compliance_node(state_after_refine)

    assert "Tnufa" in result["legal_compliance"] or "Grant" in result["legal_compliance"]


@pytest.mark.asyncio
async def test_legal_compliance_uses_search(state_after_refine):
    search_calls = []

    def fake_search(query, max_results=4):
        search_calls.append(max_results)
        return []

    with (
        patch("agents.legal_compliance.ChatOpenAI") as MockLLM,
        patch("agents.legal_compliance.duckduckgo_search", side_effect=fake_search),
    ):
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_LEGAL_OUTPUT))
        await legal_compliance_node(state_after_refine)

    assert len(search_calls) == 1
    assert search_calls[0] <= 4


@pytest.mark.asyncio
async def test_legal_compliance_status_done(state_after_refine):
    with (
        patch("agents.legal_compliance.ChatOpenAI") as MockLLM,
        patch("agents.legal_compliance.duckduckgo_search", return_value=[]),
    ):
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_LEGAL_OUTPUT))
        result = await legal_compliance_node(state_after_refine)

    assert result["agent_statuses"]["legal_agent"] == "done"
