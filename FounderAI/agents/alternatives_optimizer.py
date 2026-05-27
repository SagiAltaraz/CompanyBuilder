import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .state import FounderState
from .utils import summarize_text

MODEL_NAME = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You are a cost optimization advisor. For EVERY paid tool, service, and hire "
    "recommended by the prior agents — provide a cheaper alternative.\n\n"
    "Format as comparison tables:\n\n"
    "CATEGORY: [Software Tools]\n"
    "| Recommended | Cost/mo | Budget Alternative | Cost/mo | Quality Trade-off |\n\n"
    "CATEGORY: [Service Providers]\n"
    "| Recommended | Cost/mo | Budget Alternative | Cost/mo | When to upgrade |\n\n"
    "CATEGORY: [Hires — Offshore Options]\n"
    "| Role | Local Cost | Offshore Location | Offshore Cost | Quality notes |\n\n"
    "Always cover: project mgmt, communication, CRM, accounting, design, hosting, "
    "email marketing, analytics.\n"
    "Always include free/open-source options. Budget option must deliver ≥75% value.\n"
    "End with: TOTAL MONTHLY SAVINGS if founder chooses all budget options."
)


async def alternatives_optimizer_node(state: FounderState) -> dict:
    start = time.perf_counter()
    try:
        language = state.get("language", "en")
        llm = ChatOpenAI(model=MODEL_NAME, temperature=0, max_tokens=1400)
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=(
                f"Business concept:\n{summarize_text(state.get('refined_idea', ''), 800)}\n\n"
                f"Team structure:\n{summarize_text(state.get('team_structure', ''), 1000)}\n\n"
                f"Financial plan:\n{summarize_text(state.get('financial_plan', ''), 1000)}\n\n"
                f"Legal & compliance:\n{summarize_text(state.get('legal_compliance', ''), 800)}\n\n"
                f"Respond in language: {language}"
            )),
        ])
        duration = int((time.perf_counter() - start) * 1000)
        tokens = response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
        return {
            "alternatives": response.content.strip(),
            "current_agent": "alternatives_optimizer",
            "agent_statuses": {"alternatives_optimizer": "done"},
            "metadata": {"alternatives_optimizer": {"model_used": MODEL_NAME, "duration_ms": duration, "tokens_used": tokens}},
        }
    except Exception as exc:
        return {
            "current_agent": "alternatives_optimizer",
            "agent_statuses": {"alternatives_optimizer": "error"},
            "error": str(exc),
        }
