import re
from datetime import datetime
from typing import Any, Dict

from .state import FounderState


def detect_language(text: str) -> str:
    hebrew_chars = sum(1 for c in text if '\u05d0' <= c <= '\u05ea')
    return "he" if hebrew_chars > len(text) * 0.15 else "en"


def record_agent_metadata(state: FounderState, agent_name: str, model: str, duration_ms: int, tokens_used: int = 0) -> None:
    metadata = state.get("metadata", {})
    metadata.setdefault(agent_name, {})
    metadata[agent_name]["model_used"] = model
    metadata[agent_name]["duration_ms"] = int(duration_ms)
    metadata[agent_name]["tokens_used"] = int(tokens_used)
    state["metadata"] = metadata


def summarize_text(text: str, max_chars: int = 1500) -> str:
    if len(text) <= max_chars:
        return text
    snippet = text[:max_chars]
    return snippet.rsplit("\n", 1)[0] if "\n" in snippet else snippet


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
