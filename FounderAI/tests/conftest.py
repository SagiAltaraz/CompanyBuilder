"""
Shared test fixtures.
"""
import pytest
from agents.state import FounderState


def make_state(**kwargs) -> FounderState:
    """Return a minimal FounderState with defaults."""
    base: FounderState = {
        "task_id": "test-uuid-1234",
        "raw_input": "I want to build a SaaS for restaurant management in Israel",
        "language": "en",
        "refined_idea": "",
        "market_analysis": "",
        "legal_compliance": "",
        "team_structure": "",
        "financial_plan": "",
        "alternatives": "",
        "final_report": "",
        "current_agent": "",
        "agent_statuses": {},
        "error": None,
        "metadata": {},
    }
    base.update(kwargs)
    return base


@pytest.fixture
def base_state() -> FounderState:
    return make_state()


@pytest.fixture
def hebrew_state() -> FounderState:
    return make_state(
        raw_input="אני רוצה להקים סטארטאפ לבניית אתרים לחברות קטנות",
    )


@pytest.fixture
def state_after_refine() -> FounderState:
    return make_state(
        refined_idea=(
            "Business concept: SaaS platform for restaurant management\n"
            "Industry: Food & Beverage Tech\n"
            "Business model: B2B SaaS\n"
            "Product type: SaaS\n"
            "Target market: Israel\n"
            "Stage: idea"
        ),
        language="en",
    )


@pytest.fixture
def state_after_market(state_after_refine) -> FounderState:
    state_after_refine["market_analysis"] = (
        "## Market Size\n- TAM: $10B global restaurant software\n"
        "## Competitors\n- Toast, Square, Lightspeed\n"
        "## Trends\n- Cloud adoption in F&B increasing 25% YoY"
    )
    return state_after_refine


@pytest.fixture
def state_after_legal(state_after_market) -> FounderState:
    state_after_market["legal_compliance"] = (
        "## Company Structure\n- Recommended: Chevra Ba'am (Ltd)\n"
        "## Grants\n- Tnufa: up to ₪200,000\n- Nofar: up to ₪1M"
    )
    return state_after_market


@pytest.fixture
def state_after_team(state_after_legal) -> FounderState:
    state_after_legal["team_structure"] = (
        "## Stage 1\n| Role | Cost | Type |\n|---|---|---|\n"
        "| Founder | ₪0 | Founder |\n| Freelance Dev | ₪8,000/project | Freelancer |"
    )
    return state_after_legal


@pytest.fixture
def full_state(state_after_team) -> FounderState:
    state_after_team["financial_plan"] = (
        "## Setup Costs\n- Registration: ₪1,500\n"
        "## Monthly Burn\n- Stage 1: ₪15,000\n"
    )
    state_after_team["alternatives"] = (
        "## Software\n| Jira | $20/mo | GitHub Issues | Free |"
    )
    return state_after_team
