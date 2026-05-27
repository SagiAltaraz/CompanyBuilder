import time
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .state import FounderState
from .utils import summarize_text
from .tools.search import duckduckgo_search

MODEL_NAME = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You are a market research analyst. Based on the business concept provided, research and analyze:\n\n"
    "1. MARKET SIZE\n"
    "   - TAM (Total Addressable Market) — global\n"
    "   - SAM (Serviceable Addressable Market) — realistic target segment\n"
    "   - SOM (Serviceable Obtainable Market) — realistic first 2 years\n\n"
    "2. COMPETITIVE LANDSCAPE\n"
    "   - Top 5 direct competitors (name, pricing, strengths, weaknesses)\n"
    "   - Top 3 indirect competitors\n"
    "   - Market gaps and underserved segments\n\n"
    "3. MARKET TRENDS\n"
    "   - 3 macro trends supporting this business\n"
    "   - 2 risks or headwinds\n\n"
    "4. POSITIONING OPPORTUNITY\n"
    "   - Recommended unique angle vs competitors\n\n"
    "Use tables and bullet points. Be specific with numbers."
)


async def market_analyst_node(state: FounderState) -> dict:
    start = time.perf_counter()
    try:
        refined = state.get("refined_idea", state.get("raw_input", ""))
        language = state.get("language", "en")

        search_results = await asyncio.to_thread(
            duckduckgo_search, f"{refined[:200]} market size competitors trends", 4
        )
        search_context = "\n".join(f"- {r}" for r in search_results)

        llm = ChatOpenAI(model=MODEL_NAME, temperature=0, max_tokens=1200)
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=(
                f"Business concept:\n{refined}\n\n"
                f"Search results:\n{search_context}\n\n"
                f"Respond in language: {language}"
            )),
        ])
        duration = int((time.perf_counter() - start) * 1000)
        tokens = response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
        return {
            "market_analysis": response.content.strip(),
            "agent_statuses": {"market_analyst": "done"},
            "metadata": {"market_analyst": {"model_used": MODEL_NAME, "duration_ms": duration, "tokens_used": tokens}},
        }
    except Exception as exc:
        return {
            "agent_statuses": {"market_analyst": "error"},
            "error": str(exc),
        }
