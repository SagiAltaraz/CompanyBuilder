"""Unit tests for Agent 4: Team Architect."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from agents.team_architect import team_architect_node

MOCK_TEAM_OUTPUT = (
    "## Stage 1 — Bootstrap (Months 0-6)\n"
    "| Role | # | Monthly Cost (ILS) | Monthly Cost (USD) | Type | Responsibilities | Delay? |\n"
    "|---|---|---|---|---|---|---|\n"
    "| Founder / Product | 1 | ₪0 | $0 | Founder | Everything | No |\n"
    "| Freelance Developer | 1 | ₪8,000/project | $2,100 | Freelancer | MVP build | No |\n\n"
    "**Total Stage 1:** ₪8,000 – ₪15,000/month\n\n"
    "## Stage 2 — Early Traction (Months 6-18)\n"
    "First hire: Full-time junior developer at ₪15,000/month when MRR > ₪20,000\n"
)


def _mock_response(text: str):
    msg = MagicMock()
    msg.content = text
    msg.response_metadata = {"token_usage": {"total_tokens": 350}}
    return msg


@pytest.mark.asyncio
async def test_team_architect_sets_team_structure(state_after_legal):
    with patch("agents.team_architect.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_TEAM_OUTPUT))
        result = await team_architect_node(state_after_legal)

    assert result["team_structure"] != ""
    assert "Stage 1" in result["team_structure"]


@pytest.mark.asyncio
async def test_team_architect_reads_prior_outputs(state_after_legal):
    captured_messages = []

    async def capture_ainvoke(messages):
        captured_messages.extend(messages)
        return _mock_response(MOCK_TEAM_OUTPUT)

    with patch("agents.team_architect.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = capture_ainvoke
        await team_architect_node(state_after_legal)

    # The HumanMessage should include context from prior agents
    human_content = captured_messages[-1].content
    assert "market" in human_content.lower() or "business" in human_content.lower()


@pytest.mark.asyncio
async def test_team_architect_status_done(state_after_legal):
    with patch("agents.team_architect.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_TEAM_OUTPUT))
        result = await team_architect_node(state_after_legal)

    assert result["agent_statuses"]["team_architect"] == "done"


@pytest.mark.asyncio
async def test_team_architect_metadata(state_after_legal):
    with patch("agents.team_architect.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_TEAM_OUTPUT))
        result = await team_architect_node(state_after_legal)

    meta = result["metadata"].get("team_architect", {})
    assert meta.get("model_used") == "gpt-4o-mini"
    assert meta.get("duration_ms", 0) >= 0
