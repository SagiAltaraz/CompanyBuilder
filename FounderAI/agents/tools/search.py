"""
DuckDuckGo search — no API key required.
Token-efficiency rule: max_results is capped at 4.
Returns snippet text (not raw links) for maximum LLM usefulness.
"""
from typing import List
import requests
from bs4 import BeautifulSoup


def duckduckgo_search(query: str, max_results: int = 4) -> List[str]:
    """Search DuckDuckGo and return up to max_results text snippets."""
    max_results = min(max_results, 4)  # token-efficiency cap

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    url = "https://html.duckduckgo.com/html/"
    try:
        resp = requests.post(url, data={"q": query}, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception:
        return [f"[Search unavailable for: {query}]"]

    soup = BeautifulSoup(resp.text, "html.parser")
    results: List[str] = []

    for block in soup.select(".result")[:max_results]:
        title_el = block.select_one(".result__a")
        snippet_el = block.select_one(".result__snippet")
        title = title_el.get_text(strip=True) if title_el else ""
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""
        if title or snippet:
            results.append(f"{title}: {snippet}".strip(": "))

    return results if results else [f"[No results for: {query}]"]
