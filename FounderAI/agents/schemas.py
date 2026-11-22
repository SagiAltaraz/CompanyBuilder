"""Typed outputs for every agent.

Each agent produces a strongly typed Pydantic object plus a markdown narrative.
Downstream agents consume upstream typed fields directly — no string parsing.
That's what lets the critic check numerical consistency and the frontend
render rich sections (tables, timelines, numbers) instead of plain prose.
"""
from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────

class BizModel(str, Enum):
    b2b = "b2b"
    b2c = "b2c"
    b2b2c = "b2b2c"
    marketplace = "marketplace"


class ProductType(str, Enum):
    saas = "saas"
    service = "service"
    physical = "physical"
    marketplace = "marketplace"
    app = "app"
    other = "other"


class TargetMarket(str, Enum):
    israel = "israel"
    global_market = "global"
    region = "region"


class Stage(str, Enum):
    idea = "idea"
    mvp = "mvp"
    early_revenue = "early_revenue"
    scaling = "scaling"


class EntityType(str, Enum):
    sole_proprietor = "sole_proprietor"   # עוסק פטור / מורשה
    ltd = "ltd"                           # חברה בע״מ
    partnership = "partnership"
    non_profit = "non_profit"


class Seniority(str, Enum):
    junior = "junior"
    mid = "mid"
    senior = "senior"
    lead = "lead"


# ── Shared sub-models ────────────────────────────────────────────────────

class Citation(BaseModel):
    url: str
    claim: str


class Competitor(BaseModel):
    name: str
    url: Optional[str] = None
    positioning: str
    strength: Optional[str] = None
    weakness: Optional[str] = None
    pricing_note: Optional[str] = None


class NeighborhoodOption(BaseModel):
    name: str
    city: str
    rent_nis_per_sqm_month: Optional[int] = None
    demand_score: int = Field(..., ge=1, le=10)
    competition_level: Literal["low", "medium", "high"]
    rationale: str


class LicenseRequirement(BaseModel):
    name: str
    issuing_authority: str
    cost_nis: Optional[int] = None
    time_to_obtain_days: Optional[int] = None


class Grant(BaseModel):
    program: str
    amount_nis_max: Optional[int] = None
    eligibility: str
    difficulty: Literal["low", "medium", "high"]
    priority_score: int = Field(..., ge=1, le=10)


class Hire(BaseModel):
    role: str
    seniority: Seniority
    employment_type: Literal["founder", "employee", "freelancer", "offshore"]
    monthly_cost_nis: int
    hire_month: int = Field(..., ge=0)
    rationale: str


class BudgetAlternative(BaseModel):
    category: Literal["software", "services", "hires", "location", "marketing", "other"]
    recommended: str
    recommended_cost_nis_month: Optional[int] = None
    alternative: str
    alternative_cost_nis_month: Optional[int] = None
    trade_off: str


class ActionItem(BaseModel):
    action: str
    category: Literal["legal", "finance", "team", "product", "marketing", "ops"]
    owner: Literal["founder", "accountant", "lawyer", "contractor"]
    by_week: int = Field(..., ge=1, le=52)
    cost_nis: Optional[int] = None


class RiskItem(BaseModel):
    risk: str
    probability: Literal["low", "medium", "high"]
    impact: Literal["low", "medium", "high"]
    mitigation: str


class Issue(BaseModel):
    severity: Literal["info", "warn", "block"]
    section: str
    message: str


# ── Per-agent outputs ────────────────────────────────────────────────────

class RefinedIdea(BaseModel):
    concept: str
    industry: str
    business_model: BizModel
    product_type: ProductType
    target_market: TargetMarket
    stage: Stage
    language: Literal["he", "en"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    open_questions: list[str] = Field(default_factory=list)
    narrative_md: str


class MarketAnalysis(BaseModel):
    tam_nis: Optional[int] = None
    sam_nis: Optional[int] = None
    som_nis: Optional[int] = None
    competitors: list[Competitor] = Field(default_factory=list)
    gap_opportunities: list[str] = Field(default_factory=list)
    macro_trends: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    positioning: str
    sources: list[Citation] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    narrative_md: str


class LegalCompliance(BaseModel):
    entity_recommendation: EntityType
    entity_rationale: str
    licenses: list[LicenseRequirement] = Field(default_factory=list)
    tax_obligations: list[str] = Field(default_factory=list)
    vat_threshold_nis: Optional[int] = None
    required_providers: list[str] = Field(default_factory=list)
    grants: list[Grant] = Field(default_factory=list)
    narrative_md: str


class LocationStrategy(BaseModel):
    is_physical: bool
    top_options: list[NeighborhoodOption] = Field(default_factory=list)
    recommended_index: int = 0
    expansion_plan_md: str = ""
    narrative_md: str


class TeamPlan(BaseModel):
    hires: list[Hire] = Field(default_factory=list)
    stage1_monthly_cost_nis: int = 0
    stage2_monthly_cost_nis: int = 0
    stage3_monthly_cost_nis: int = 0
    employer_overhead_pct: float = 0.25
    narrative_md: str


class FinancialPlan(BaseModel):
    startup_cost_low_nis: int
    startup_cost_high_nis: int
    monthly_burn_stage1_nis: int
    monthly_burn_stage2_nis: int
    monthly_burn_stage3_nis: int
    runway_months_at_100k_usd: Optional[int] = None
    revenue_monthly_nis_12mo: list[int] = Field(default_factory=list)
    break_even_month: Optional[int] = None
    assumptions: list[str] = Field(default_factory=list)
    narrative_md: str


class Alternatives(BaseModel):
    cuts: list[BudgetAlternative] = Field(default_factory=list)
    total_monthly_savings_nis: int = 0
    narrative_md: str


class FinalReport(BaseModel):
    title: str
    executive_summary_md: str
    action_items_this_week: list[ActionItem] = Field(..., min_length=5, max_length=10)
    twelve_month_roadmap_md: str
    risks: list[RiskItem] = Field(default_factory=list)
    kpis_md: str
    narrative_md: str


class CriticReport(BaseModel):
    issues: list[Issue] = Field(default_factory=list)
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    summary: str


# Field name → schema class, used by the graph and persistence layer.
AGENT_OUTPUT_SCHEMA = {
    "refined_idea":        RefinedIdea,
    "market_analysis":     MarketAnalysis,
    "legal_compliance":    LegalCompliance,
    "location_analysis":   LocationStrategy,
    "team_structure":      TeamPlan,
    "financial_plan":      FinancialPlan,
    "alternatives":        Alternatives,
    "final_report":        FinalReport,
    "critic":              CriticReport,
}
