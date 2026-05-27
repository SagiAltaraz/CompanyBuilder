import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .state import FounderState
from .utils import detect_language

MODEL_NAME = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You are a business idea clarifier. Extract the following from the user's input:\n"
    "- Business concept (1 sentence)\n"
    "- Industry/sector\n"
    "- Business model: B2B, B2C, B2B2C, or marketplace\n"
    "- Product type: SaaS, service agency, physical product, marketplace, or app\n"
    "- Target market: Israel, global, or specific region\n"
    "- Stage: idea, MVP, early revenue, or scaling\n\n"
    "Also detect the input language: return 'he' for Hebrew, 'en' for English.\n"
    "Respond in the SAME language as the input.\n"
    "Return as structured text with clear labels, not JSON."
)


async def idea_refiner_node(state: FounderState) -> dict:
    start = time.perf_counter()
    try:
        language = detect_language(state["raw_input"])
        llm = ChatOpenAI(model=MODEL_NAME, temperature=0, max_tokens=800)
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=state["raw_input"]),
        ])
        duration = int((time.perf_counter() - start) * 1000)
        tokens = response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
        return {
            "refined_idea": response.content.strip(),
            "language": language,
            "current_agent": "idea_refiner",
            "agent_statuses": {"idea_refiner": "done"},
            "metadata": {"idea_refiner": {"model_used": MODEL_NAME, "duration_ms": duration, "tokens_used": tokens}},
        }
    except Exception as exc:
        return {
            "current_agent": "idea_refiner",
            "agent_statuses": {"idea_refiner": "error"},
            "error": str(exc),
        }
