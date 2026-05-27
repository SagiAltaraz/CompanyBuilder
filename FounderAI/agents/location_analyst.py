import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .state import FounderState
from .utils import summarize_text

MODEL_NAME = "gpt-4o-mini"
AGENT_KEY = "location_analyst"

SYSTEM_PROMPT = (
    "You are a market geography and location strategy expert, specializing in Israel. "
    "Analyze where this business should be located or which markets to enter first.\n\n"

    "## LOCATION RECOMMENDATION\n"
    "State the #1 recommended location/area and why in 2-3 sentences.\n\n"

    "## TOP AREAS COMPARISON\n"
    "For physical businesses — compare 3-5 specific areas:\n"
    "Table: Area / Neighborhood | City | Monthly Rent ₪/sqm | Foot Traffic | "
    "Target Customer Fit | Competition Level | Overall Score (1-10) | Key Advantage\n\n"
    "For online/service businesses — compare 3-5 target markets:\n"
    "Table: City / Region | Population | Avg. Income | Demand Potential | "
    "Customer Density | Competition | Entry Difficulty | Recommended Priority\n\n"

    "## DEMAND ANALYSIS BY AREA\n"
    "Table: Area | Market Size (₪/month) | # Potential Customers | Avg. Spend per Customer | "
    "Seasonal Trends | Growth Direction (growing / stable / declining)\n\n"

    "## COMPETITION MAP\n"
    "Table: Competitor | Area | Monthly Revenue Estimate | Price Point | Their Weakness | "
    "How to Win Against Them\n\n"

    "## RENT & OVERHEAD BY LOCATION\n"
    "Table: Area | Space Needed (sqm) | Rent ₪/mo | Utilities Est. | "
    "Total Location Cost ₪/mo | Notes (parking, accessibility, visibility)\n\n"

    "## EXPANSION ROADMAP\n"
    "Stage 1 (launch): exact location — what, where, why\n"
    "Stage 2 (month 6-12): when to add a second location or expand reach\n"
    "Stage 3 (year 2+): regional or national expansion plan\n\n"

    "Use real Israeli city names, neighborhoods, and streets where relevant. "
    "Be specific with rent prices in ₪. For non-physical businesses, focus on digital geo-targeting."
)


async def location_analyst_node(state: FounderState) -> dict:
    start = time.perf_counter()
    try:
        refined = state.get("refined_idea", state.get("raw_input", ""))
        language = state.get("language", "en")

        llm = ChatOpenAI(model=MODEL_NAME, temperature=0, max_tokens=1800)
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=(
                f"Business concept:\n{summarize_text(refined, 1000)}\n\n"
                f"Respond in language: {language}"
            )),
        ])
        duration = int((time.perf_counter() - start) * 1000)
        tokens = response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
        return {
            "location_analysis": response.content.strip(),
            "agent_statuses": {AGENT_KEY: "done"},
            "metadata": {AGENT_KEY: {"model_used": MODEL_NAME, "duration_ms": duration, "tokens_used": tokens}},
        }
    except Exception as exc:
        return {
            "agent_statuses": {AGENT_KEY: "error"},
            "error": str(exc),
        }
