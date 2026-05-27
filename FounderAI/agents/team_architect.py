import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .state import FounderState
from .utils import summarize_text

MODEL_NAME = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You are an organizational design expert and HR advisor for startups. "
    "Build a detailed, actionable hiring plan with real cost data.\n\n"

    "## STAGE 1 — BOOTSTRAP (Months 0-6)\n"
    "Goal: MVP + first 3-5 paying customers. Absolute minimum team.\n\n"
    "Table: Role | # | Gross Salary (₪/mo) | Employer Total Cost (₪/mo) | "
    "Employee / Freelancer / Offshore | Key Responsibilities | Priority\n\n"
    "Include: founder (₪0 salary stage 1), any critical freelancers.\n"
    "**Stage 1 Total: ₪X–₪Y/month**\n\n"

    "## STAGE 2 — EARLY TRACTION (Months 6-18)\n"
    "First real hires, triggered by revenue milestones.\n\n"
    "Table: Role | # | Gross Salary (₪/mo) | Total Employer Cost | "
    "Hire Trigger (revenue/event) | Employee vs Freelancer | Offshore Option?\n\n"
    "**Stage 2 Total: ₪X–₪Y/month**\n\n"

    "## STAGE 3 — SCALING (Months 18-36)\n"
    "Building departments, management layer.\n\n"
    "Table: Role | # | Gross Salary (₪/mo) | Total Employer Cost | Department | Priority\n\n"
    "**Stage 3 Total: ₪X–₪Y/month**\n\n"

    "## SALARY BENCHMARKS (Israel 2024)\n"
    "Table: Role | Junior (₪/mo gross) | Mid (₪/mo gross) | Senior (₪/mo gross) | "
    "Freelance Rate (₪/hr) | Offshore Alternative ($/mo)\n"
    "Cover all roles relevant to this business type.\n\n"

    "## EMPLOYER SOCIAL COST BREAKDOWN (Israel)\n"
    "Table: Component | % of Salary | Notes\n"
    "Include: Bituach Leumi (employer), vacation pay, sick days, pension (keren hishtalmut), "
    "severance reserve. Total: typically 20-27% on top of gross.\n\n"

    "## OFFSHORE OPTIONS\n"
    "Table: Role | Local Cost (₪/mo) | Offshore Location | Offshore Cost ($/mo) | "
    "Quality Notes | Recommended Platforms\n"
    "Include: Upwork, Toptal, Israeli outsourcing companies, specific Eastern Europe locations.\n\n"

    "## WHAT FOUNDER DOES INSTEAD\n"
    "For each role in Stage 1 that isn't hired: what the founder must do themselves, "
    "time estimate per week, and at what point it becomes unsustainable.\n\n"

    "Be specific with all numbers. Use Israeli shekel (₪) as primary currency."
)


async def team_architect_node(state: FounderState) -> dict:
    start = time.perf_counter()
    try:
        refined = state.get("refined_idea", state.get("raw_input", ""))
        language = state.get("language", "en")
        market = summarize_text(state.get("market_analysis", ""), 800)
        legal = summarize_text(state.get("legal_compliance", ""), 800)
        location = summarize_text(state.get("location_analysis", ""), 600)

        llm = ChatOpenAI(model=MODEL_NAME, temperature=0, max_tokens=2000)
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=(
                f"Business concept:\n{refined}\n\n"
                f"Market analysis:\n{market}\n\n"
                f"Legal & compliance:\n{legal}\n\n"
                f"Location strategy:\n{location}\n\n"
                f"Respond in language: {language}"
            )),
        ])
        duration = int((time.perf_counter() - start) * 1000)
        tokens = response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
        return {
            "team_structure": response.content.strip(),
            "current_agent": "team_architect",
            "agent_statuses": {"team_architect": "done"},
            "metadata": {"team_architect": {"model_used": MODEL_NAME, "duration_ms": duration, "tokens_used": tokens}},
        }
    except Exception as exc:
        return {
            "current_agent": "team_architect",
            "agent_statuses": {"team_architect": "error"},
            "error": str(exc),
        }
