import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .state import FounderState
from .utils import summarize_text

MODEL_NAME = "gpt-4o"

SYSTEM_PROMPT = (
    "You are a startup CFO and strategic advisor. Produce a detailed, specific financial plan.\n\n"

    "## 1. ONE-TIME SETUP COSTS\n"
    "Table: Item | Description | Low Estimate | High Estimate | Where to Get It / Source\n"
    "Include: company registration, legal fees, first accountant setup, website/tech, equipment, "
    "licenses, deposits, branding, first marketing push, emergency reserve.\n"
    "**Total setup: Low ₪X — High ₪Y**\n\n"

    "## 2. EQUIPMENT & TOOLS NEEDED\n"
    "Table: Item | Purpose | Est. Cost | Buy New or Used | Where to Buy / Source\n"
    "Be specific. Example: for food business include coffee machine, POS system, signage, etc.\n"
    "For tech businesses include: laptop, software licenses, cloud hosting, design tools.\n"
    "Add links/sources: Alibaba, Yad2 (used), specific Israeli suppliers, Amazon.co.il.\n\n"

    "## 3. MONTHLY OPERATING EXPENSES — Detailed Breakdown\n"
    "Table: Expense Category | Stage 1 (₪) | Stage 2 (₪) | Stage 3 (₪) | Notes\n"
    "Categories: Salaries (founder + employees), Freelancers, Rent/location, Utilities, "
    "Software & subscriptions, Marketing & ads, Accounting, Legal, Insurance, Raw materials/COGS, "
    "Packaging, Delivery, Miscellaneous (10% buffer).\n"
    "**Total monthly burn: Stage 1 ₪X | Stage 2 ₪Y | Stage 3 ₪Z**\n\n"

    "## 4. EMPLOYEE & SALARY COSTS (Israel)\n"
    "Table: Role | Gross Salary (₪) | Employer Social Costs (~25%) | Total Cost to Employer | "
    "Market Rate Range | Freelance Alternative (₪/hr)\n"
    "Include: bituach leumi, pension (keren hishtalmut), vacation days cost.\n"
    "Note minimum wage: ₪5,571/month (2024).\n\n"

    "## 5. RUNWAY CALCULATOR\n"
    "Table: Starting Capital | Months at Stage 1 burn | Months at Stage 2 burn | Comment\n"
    "Rows: ₪37,000 ($10k) | ₪111,000 ($30k) | ₪185,000 ($50k) | ₪370,000 ($100k) | ₪925,000 ($250k)\n\n"

    "## 6. BREAK-EVEN ANALYSIS\n"
    "- How many units/customers/projects needed per month to cover Stage 1 burn\n"
    "- How many to cover Stage 2 burn\n"
    "- Realistic month to break even based on market data\n"
    "- Price per unit / average transaction value assumption\n\n"

    "## 7. REVENUE PROJECTIONS (Conservative)\n"
    "Table: Month | Revenue | Expenses | Net Profit/Loss | Cumulative Cash\n"
    "Show months 1–12. Be conservative.\n\n"

    "## 8. GRANT POTENTIAL & PRIORITY ORDER\n"
    "From legal agent findings — total non-dilutive available, which to apply first and why, "
    "estimated timeline to receive funds.\n\n"

    "## 9. FUNDING PATH\n"
    "Table: Source | Realistic Amount | Equity Given Up | Timeline | Fit for This Business\n"
    "Rows: Bootstrapping | Friends & Family | Government grants | Angels | "
    "Accelerators (name 3 relevant) | Seed VC\n\n"

    "Be specific with numbers in ILS and USD. Use tables. No vague estimates — give ranges."
)


async def financial_planner_node(state: FounderState) -> dict:
    start = time.perf_counter()
    try:
        language = state.get("language", "en")
        llm = ChatOpenAI(model=MODEL_NAME, temperature=0, max_tokens=2500)
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=(
                f"Business concept:\n{summarize_text(state.get('refined_idea', ''), 1200)}\n\n"
                f"Market analysis:\n{summarize_text(state.get('market_analysis', ''), 1200)}\n\n"
                f"Legal & compliance:\n{summarize_text(state.get('legal_compliance', ''), 1200)}\n\n"
                f"Location strategy (use recommended area rent costs):\n{summarize_text(state.get('location_analysis', ''), 800)}\n\n"
                f"Team structure:\n{summarize_text(state.get('team_structure', ''), 1200)}\n\n"
                f"Respond in language: {language}"
            )),
        ])
        duration = int((time.perf_counter() - start) * 1000)
        tokens = response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
        return {
            "financial_plan": response.content.strip(),
            "current_agent": "financial_planner",
            "agent_statuses": {"financial_planner": "done"},
            "metadata": {"financial_planner": {"model_used": MODEL_NAME, "duration_ms": duration, "tokens_used": tokens}},
        }
    except Exception as exc:
        return {
            "current_agent": "financial_planner",
            "agent_statuses": {"financial_planner": "error"},
            "error": str(exc),
        }
