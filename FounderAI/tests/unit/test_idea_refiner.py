"""Unit tests for Agent 1: Idea Refiner."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from agents.idea_refiner import idea_refiner_node
from agents.utils import detect_language
from tests.conftest import make_state


def _mock_llm_response(text: str):
    """Create a mock LLM response object."""
    msg = MagicMock()
    msg.content = text
    msg.response_metadata = {"token_usage": {"total_tokens": 150}}
    return msg


# ── detect_language ──────────────────────────────────────────────────────────

def test_detect_language_english():
    assert detect_language("I want to build a SaaS for restaurants") == "en"


def test_detect_language_hebrew():
    assert detect_language("אני רוצה להקים סטארטאפ לבניית אתרים לחברות קטנות") == "he"


def test_detect_language_mixed_mostly_english():
    # "שלום" is 4 Hebrew chars in a 50-char string = 8% < 15% threshold → English
    assert detect_language("Hello world שלום hello there and more english text here") == "en"


def test_detect_language_mixed_mostly_hebrew():
    assert detect_language("שלום אני רוצה להקים עסק חדש hello") == "he"


def test_detect_language_empty():
    assert detect_language("") == "en"


# ── idea_refiner_node ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_idea_refiner_sets_refined_idea():
    state = make_state(raw_input="I want to start a web design agency for small businesses")
    mock_response = _mock_llm_response(
        "Business concept: Web design agency targeting SMBs\n"
        "Industry: Digital services\n"
        "Business model: B2B\n"
        "Product type: Service agency\n"
        "Target market: Israel\n"
        "Stage: idea"
    )
    with patch("agents.idea_refiner.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=mock_response)
        result = await idea_refiner_node(state)

    assert result["refined_idea"] != ""
    assert "Business concept" in result["refined_idea"]


@pytest.mark.asyncio
async def test_idea_refiner_detects_english():
    state = make_state(raw_input="SaaS for restaurant management in Israel")
    mock_response = _mock_llm_response("Business concept: Restaurant SaaS\nBusiness model: B2B")
    with patch("agents.idea_refiner.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=mock_response)
        result = await idea_refiner_node(state)

    assert result["language"] == "en"


@pytest.mark.asyncio
async def test_idea_refiner_detects_hebrew():
    state = make_state(raw_input="אני רוצה להקים סטארטאפ לבניית אתרים לחברות קטנות")
    mock_response = _mock_llm_response("מושג עסקי: סוכנות עיצוב אתרים לעסקים קטנים")
    with patch("agents.idea_refiner.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=mock_response)
        result = await idea_refiner_node(state)

    assert result["language"] == "he"


@pytest.mark.asyncio
async def test_idea_refiner_sets_status_done():
    state = make_state()
    mock_response = _mock_llm_response("Business concept: test")
    with patch("agents.idea_refiner.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=mock_response)
        result = await idea_refiner_node(state)

    assert result["agent_statuses"]["idea_refiner"] == "done"


@pytest.mark.asyncio
async def test_idea_refiner_records_metadata():
    state = make_state()
    mock_response = _mock_llm_response("Business concept: test")
    with patch("agents.idea_refiner.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=mock_response)
        result = await idea_refiner_node(state)

    meta = result["metadata"].get("idea_refiner", {})
    assert "duration_ms" in meta
    assert meta["model_used"] == "gpt-4o-mini"


@pytest.mark.asyncio
async def test_idea_refiner_handles_error():
    state = make_state()
    with patch("agents.idea_refiner.ChatOpenAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(side_effect=Exception("OpenAI API error"))
        with pytest.raises(Exception, match="OpenAI API error"):
            await idea_refiner_node(state)

    assert state["agent_statuses"]["idea_refiner"] == "error"
    assert "OpenAI API error" in state["error"]
