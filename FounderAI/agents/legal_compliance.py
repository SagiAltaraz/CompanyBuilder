import time
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .state import FounderState
from .tools.search import duckduckgo_search

MODEL_NAME = "gpt-4o-mini"
AGENT_KEY = "legal_agent"  # node name — cannot match state field "legal_compliance"

SYSTEM_PROMPT = (
    "You are a legal and financial compliance advisor for entrepreneurs. "
    "Based on the business concept and target market, provide:\n\n"
    "1. COMPANY STRUCTURE OPTIONS (sole proprietor vs LLC vs corporation)\n"
    "2. REQUIRED REGISTRATIONS & LICENSES (cost, time, order of operations)\n"
    "3. TAX OBLIGATIONS (income tax, VAT thresholds, payroll, tax advantages)\n"
    "4. MANDATORY SERVICE PROVIDERS (accountant, lawyer, insurance, bank — cost + budget option)\n"
    "5. GRANTS, SUBSIDIES & FUNDING PROGRAMS\n"
    "   For Israel always include: Innovation Authority (Tnufa, Nofar, R&D grants), "
    "BIRD Foundation, ISERD/EU Horizon, municipality programs, Bank Leumi/Hapoalim startup programs.\n\n"
    "Be specific with costs in local currency. Use tables and bullet points."
)


async def legal_compliance_node(state: FounderState) -> dict:
    start = time.perf_counter()
    try:
        refined = state.get("refined_idea", state.get("raw_input", ""))
        language = state.get("language", "en")

        search_results = await asyncio.to_thread(
            duckduckgo_search, f"{refined[:200]} company registration grants subsidies legal requirements", 4
        )
        search_context = "\n".join(f"- {r}" for r in search_results)

        llm = ChatOpenAI(model=MODEL_NAME, temperature=0, max_tokens=1400)
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
            "legal_compliance": response.content.strip(),
            "agent_statuses": {AGENT_KEY: "done"},
            "metadata": {AGENT_KEY: {"model_used": MODEL_NAME, "duration_ms": duration, "tokens_used": tokens}},
        }
    except Exception as exc:
        return {
            "agent_statuses": {AGENT_KEY: "error"},
            "error": str(exc),
        }
