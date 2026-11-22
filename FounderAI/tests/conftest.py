"""Shared test fixtures."""
from __future__ import annotations

import pytest

from agents.schemas import (
    Alternatives,
    BudgetAlternative,
    Competitor,
    FinancialPlan,
    Hire,
    LegalCompliance,
    LocationStrategy,
    MarketAnalysis,
    NeighborhoodOption,
    RefinedIdea,
    Seniority,
    TeamPlan,
)
from agents.state import FounderState


def make_state(**kwargs) -> FounderState:
    base: FounderState = {
        "task_id": "test-uuid-1234",
        "raw_input": "I want to build a SaaS for restaurant management in Israel",
        "language": "en",
        "agent_statuses": {},
        "metadata": {},
    }
    base.update(kwargs)
    return base


def _refined_idea(**overrides) -> RefinedIdea:
    data = {
        "concept": "SaaS platform for restaurant management",
        "industry": "F&B SaaS",
        "business_model": "b2b",
        "product_type": "saas",
        "target_market": "israel",
        "stage": "idea",
        "language": "en",
        "confidence": 0.85,
        "open_questions": ["Which customer segment first — fine dining or QSR?"],
        "narrative_md": "B2B SaaS for Israeli restaurants.",
    }
    data.update(overrides)
    return RefinedIdea.model_validate(data)


def _market() -> MarketAnalysis:
    return MarketAnalysis(
        tam_nis=3_500_000_000,
        sam_nis=250_000_000,
        som_nis=20_000_000,
        competitors=[Competitor(name="Toast", positioning="US POS leader", weakness="Not Israel-localised")],
        gap_opportunities=["Hebrew-native POS", "Tnuva/Tara direct integrations"],
        positioning="Local, compliant, mobile-first.",
        confidence=0.75,
        narrative_md="Market table and prose.",
    )


def _legal() -> LegalCompliance:
    return LegalCompliance(
        entity_recommendation="ltd",
        entity_rationale="B2B SaaS with planned fundraising → Chevra Ba'am.",
        vat_threshold_nis=120000,
        required_providers=["accountant", "lawyer", "insurance"],
        narrative_md="Setup steps and grants table.",
    )


def _location() -> LocationStrategy:
    return LocationStrategy(
        is_physical=False,
        top_options=[
            NeighborhoodOption(name="Tel Aviv tech workers", city="Tel Aviv", demand_score=9,
                               competition_level="medium", rationale="High density of target buyers."),
        ],
        recommended_index=0,
        narrative_md="Online-first; TLV GTM.",
    )


def _team() -> TeamPlan:
    return TeamPlan(
        hires=[
            Hire(role="Founder", seniority=Seniority.lead, employment_type="founder",
                 monthly_cost_nis=0, hire_month=0, rationale="CEO + product"),
            Hire(role="Full-stack engineer", seniority=Seniority.mid, employment_type="freelancer",
                 monthly_cost_nis=18000, hire_month=0, rationale="Build MVP"),
        ],
        stage1_monthly_cost_nis=18000,
        stage2_monthly_cost_nis=55000,
        stage3_monthly_cost_nis=140000,
        narrative_md="Lean start, hire after first 5 paying customers.",
    )


def _financial() -> FinancialPlan:
    return FinancialPlan(
        startup_cost_low_nis=15000,
        startup_cost_high_nis=35000,
        monthly_burn_stage1_nis=22000,
        monthly_burn_stage2_nis=70000,
        monthly_burn_stage3_nis=180000,
        runway_months_at_100k_usd=17,
        revenue_monthly_nis_12mo=[0, 0, 2000, 5000, 9000, 14000, 20000, 27000, 35000, 45000, 58000, 72000],
        break_even_month=None,
        assumptions=["ARPA ₪600/mo", "20 customers by month 6"],
        narrative_md="Setup + burn tables.",
    )


def _alternatives() -> Alternatives:
    return Alternatives(
        cuts=[BudgetAlternative(category="software", recommended="Linear", recommended_cost_nis_month=180,
                                alternative="GitHub Projects", alternative_cost_nis_month=0,
                                trade_off="Weaker roadmap views")],
        total_monthly_savings_nis=180,
        narrative_md="Cuts table.",
    )


@pytest.fixture
def base_state() -> FounderState:
    return make_state()


@pytest.fixture
def hebrew_state() -> FounderState:
    return make_state(raw_input="אני רוצה להקים סטארטאפ לבניית אתרים לחברות קטנות")


@pytest.fixture
def state_after_refine() -> FounderState:
    return make_state(refined_idea=_refined_idea(), language="en")


@pytest.fixture
def state_after_market(state_after_refine) -> FounderState:
    state_after_refine["market_analysis"] = _market()
    return state_after_refine


@pytest.fixture
def state_after_legal(state_after_market) -> FounderState:
    state_after_market["legal_compliance"] = _legal()
    state_after_market["location_analysis"] = _location()
    return state_after_market


@pytest.fixture
def state_after_team(state_after_legal) -> FounderState:
    state_after_legal["team_structure"] = _team()
    return state_after_legal


@pytest.fixture
def full_state(state_after_team) -> FounderState:
    state_after_team["financial_plan"] = _financial()
    state_after_team["alternatives"] = _alternatives()
    return state_after_team
