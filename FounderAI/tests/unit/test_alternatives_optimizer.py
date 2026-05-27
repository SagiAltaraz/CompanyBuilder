"""Unit tests for Agent 6: Alternatives Optimizer."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from agents.alternatives_optimizer import alternatives_optimizer_node, MODEL_NAME

MOCK_ALT_OUTPUT = (
    "## CATEGORY: Software Tools\n"
    "| Recommended | Cost/mo | Budget Alternative | Cost/mo | Quality Trade-off |\n"
    "|---|---|---|---|---|\n"
    "| Jira | $20 | GitHub Issues | Free | 80% — no roadmap view |\n"
    "| Slack | $8/user | Discord | Free | 85% — less enterprise |\n"
    "| QuickBooks | $30 | Wave | Free | 90% — no payroll |\n\n"
    "## CATEGORY: Hires — Offshore Options\n"
    "| Role | Local Cost | Offshore | Offshore Cost | Notes |\n"
    "|---|---|---|---|---|\n"
    "| Developer | ₪20,000/mo | Ukraine | $1,500/mo | Strong React/Node talent |\n\n"
    "**TOTAL MONTHLY SAVINGS: $1,200/month if all budget options chosen**\n"
)


def _mock_response(text: str):
    msg = MagicMock()
    msg.content = text
    msg.response_metadata = {"token_usage": {"total_tokens": 250}}
    return msg


@pytest.mark.asyncio
async def test_alternatives_sets_output(full_state):
    with patch("agents.alternatives_optimizer.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_ALT_OUTPUT))
        result = await alternatives_optimizer_node(full_state)

    assert result["alternatives"] != ""


@pytest.mark.asyncio
async def test_alternatives_uses_mini_model():
    """Agent 6 must use gpt-4o-mini — structured comparison, no synthesis needed."""
    assert MODEL_NAME == "gpt-4o-mini"


@pytest.mark.asyncio
async def test_alternatives_includes_free_options(full_state):
    with patch("agents.alternatives_optimizer.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_ALT_OUTPUT))
        result = await alternatives_optimizer_node(full_state)

    content = result["alternatives"].lower()
    assert "free" in content or "₪0" in content or "$0" in content


@pytest.mark.asyncio
async def test_alternatives_status_done(full_state):
    with patch("agents.alternatives_optimizer.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=_mock_response(MOCK_ALT_OUTPUT))
        result = await alternatives_optimizer_node(full_state)

    assert result["agent_statuses"]["alternatives_optimizer"] == "done"
