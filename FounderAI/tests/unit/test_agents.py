"""Unit tests for every agent.

Agents are now a thin wrapper around `call_structured` — they build the task
context, call it, and return the typed result plus metadata. So every agent
test looks the same: patch `call_structured` on the agent module, run the
node, assert the state updates.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from agents import (
    alternatives_optimizer,
    critic,
    financial_planner,
    idea_refiner,
    legal_compliance,
    location_analyst,
    market_analyst,
    report_synthesizer,
    team_architect,
)
from agents.schemas import (
    ActionItem,
    Alternatives,
    BudgetAlternative,
    Competitor,
    CriticReport,
    FinalReport,
    FinancialPlan,
    Hire,
    Issue,
    LegalCompliance,
    LocationStrategy,
    MarketAnalysis,
    NeighborhoodOption,
    RefinedIdea,
    RiskItem,
    Seniority,
    TeamPlan,
)
from agents.utils import detect_language
from tests.conftest import make_state


FAKE_META = {
    "model_used": "claude-sonnet-5-5",
    "duration_ms": 123,
    "tokens_used": 1024,
    "tokens_in": 800,
    "tokens_out": 224,
    "tokens_cached": 400,
    "cost_usd": 0.0037,
}


def _mock_call(module, return_obj):
    """Return a patch context manager that makes `call_structured` on `module` return `(return_obj, meta)`."""
    return patch.object(module, "call_structured", AsyncMock(return_value=(return_obj, FAKE_META)))


# ── detect_language ─────────────────────────────────────────────────────────

def test_detect_english():
    assert detect_language("SaaS for restaurants in Tel Aviv") == "en"


def test_detect_hebrew():
    assert detect_language("אני רוצה להקים סטארטאפ") == "he"


def test_detect_empty_defaults_english():
    assert detect_language("") == "en"


# ── idea_refiner ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_idea_refiner_sets_typed_field():
    state = make_state(raw_input="Web design agency for SMBs")
    obj = RefinedIdea(
        concept="Web design agency", industry="digital services",
        business_model="b2b", product_type="service",
        target_market="israel", stage="idea",
        language="en", confidence=0.8, narrative_md="n",
    )
    with _mock_call(idea_refiner, obj):
        result = await idea_refiner.idea_refiner_node(state)
    assert isinstance(result["refined_idea"], RefinedIdea)
    assert result["language"] == "en"
    assert result["agent_statuses"]["idea_refiner"] == "done"
    assert result["metadata"]["idea_refiner"]["model_used"] == "claude-sonnet-5-5"


@pytest.mark.asyncio
async def test_idea_refiner_propagates_hebrew():
    state = make_state(raw_input="אני רוצה להקים סוכנות שיווק")
    obj = RefinedIdea(
        concept="סוכנות שיווק", industry="שיווק דיגיטלי",
        business_model="b2b", product_type="service",
        target_market="israel", stage="idea",
        language="he", confidence=0.8, narrative_md="נ",
    )
    with _mock_call(idea_refiner, obj):
        result = await idea_refiner.idea_refiner_node(state)
    assert result["language"] == "he"


@pytest.mark.asyncio
async def test_idea_refiner_handles_error():
    state = make_state()
    with patch.object(idea_refiner, "call_structured",
                      AsyncMock(side_effect=RuntimeError("api down"))):
        result = await idea_refiner.idea_refiner_node(state)
    assert result["agent_statuses"]["idea_refiner"] == "error"
    assert "api down" in result["error"]


# ── market_analyst ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_market_analyst_returns_typed_market(state_after_refine):
    obj = MarketAnalysis(
        tam_nis=1_000_000_000, sam_nis=50_000_000, som_nis=5_000_000,
        competitors=[Competitor(name="Toast", positioning="US POS")],
        positioning="Hebrew-first", confidence=0.7, narrative_md="n",
    )
    with _mock_call(market_analyst, obj):
        result = await market_analyst.market_analyst_node(state_after_refine)
    assert isinstance(result["market_analysis"], MarketAnalysis)
    assert result["market_analysis"].som_nis == 5_000_000


# ── legal_compliance ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_legal_uses_distinct_node_key(state_after_refine):
    obj = LegalCompliance(
        entity_recommendation="ltd",
        entity_rationale="Fundraise path",
        narrative_md="n",
    )
    with _mock_call(legal_compliance, obj):
        result = await legal_compliance.legal_compliance_node(state_after_refine)
    # Node key is "legal_agent" to avoid clashing with state field "legal_compliance"
    assert result["agent_statuses"]["legal_agent"] == "done"
    assert isinstance(result["legal_compliance"], LegalCompliance)


# ── location_analyst ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_location_physical_vs_online(state_after_refine):
    obj = LocationStrategy(
        is_physical=False,
        top_options=[NeighborhoodOption(name="TLV tech", city="TLV",
                                        demand_score=9, competition_level="medium",
                                        rationale="x")],
        narrative_md="n",
    )
    with _mock_call(location_analyst, obj):
        result = await location_analyst.location_analyst_node(state_after_refine)
    assert result["location_analysis"].is_physical is False


# ── team_architect ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_team_reads_typed_upstream(state_after_legal):
    obj = TeamPlan(
        hires=[Hire(role="Founder", seniority=Seniority.lead, employment_type="founder",
                    monthly_cost_nis=0, hire_month=0, rationale="x")],
        stage1_monthly_cost_nis=0,
        stage2_monthly_cost_nis=25000,
        stage3_monthly_cost_nis=80000,
        narrative_md="n",
    )
    with _mock_call(team_architect, obj):
        result = await team_architect.team_architect_node(state_after_legal)
    assert result["team_structure"].stage3_monthly_cost_nis == 80000


# ── financial_planner ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_financial_requires_full_upstream(state_after_team):
    obj = FinancialPlan(
        startup_cost_low_nis=10000, startup_cost_high_nis=25000,
        monthly_burn_stage1_nis=20000,
        monthly_burn_stage2_nis=60000,
        monthly_burn_stage3_nis=150000,
        revenue_monthly_nis_12mo=[0]*12, narrative_md="n",
    )
    with _mock_call(financial_planner, obj):
        result = await financial_planner.financial_planner_node(state_after_team)
    assert len(result["financial_plan"].revenue_monthly_nis_12mo) == 12


# ── alternatives_optimizer ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_alternatives(full_state):
    obj = Alternatives(
        cuts=[BudgetAlternative(category="software", recommended="X", alternative="Y",
                                trade_off="z")],
        total_monthly_savings_nis=1200,
        narrative_md="n",
    )
    with _mock_call(alternatives_optimizer, obj):
        result = await alternatives_optimizer.alternatives_optimizer_node(full_state)
    assert result["alternatives"].total_monthly_savings_nis == 1200


# ── report_synthesizer ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_report_synthesizer_produces_actions(full_state):
    actions = [ActionItem(action=f"do {i}", category="legal", owner="founder",
                          by_week=1) for i in range(5)]
    obj = FinalReport(
        title="Test Plan",
        executive_summary_md="es",
        action_items_this_week=actions,
        twelve_month_roadmap_md="r",
        risks=[RiskItem(risk="x", probability="low", impact="high", mitigation="y")],
        kpis_md="k",
        narrative_md="# Test Plan\n\n...",
    )
    with _mock_call(report_synthesizer, obj):
        result = await report_synthesizer.report_synthesizer_node(full_state)
    assert len(result["final_report"].action_items_this_week) == 5


# ── critic ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_critic_returns_issues(full_state):
    obj = CriticReport(
        issues=[Issue(severity="warn", section="financial_plan", message="Revenue outpaces SOM")],
        overall_confidence=0.72,
        summary="Mostly consistent; one flag.",
    )
    with _mock_call(critic, obj):
        result = await critic.critic_node(full_state)
    assert result["critic"].issues[0].severity == "warn"
    assert result["agent_statuses"]["critic"] == "done"
