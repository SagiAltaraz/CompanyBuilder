"""Small utilities shared across agents."""
from __future__ import annotations

import re


def detect_language(text: str) -> str:
    """Heuristic: 'he' if ≥15% of characters fall in the Hebrew block, else 'en'."""
    if not text:
        return "en"
    hebrew_chars = sum(1 for c in text if 'א' <= c <= 'ת')
    return "he" if hebrew_chars > len(text) * 0.15 else "en"


def summarize_for_handoff(obj, max_chars: int = 1500) -> str:
    """Compact JSON-ish rendering of a typed agent output for downstream prompts.

    We feed downstream agents the typed upstream object, serialized compactly.
    This is what replaces the prior approach of pasting whole markdown blocks.
    """
    if obj is None:
        return "(none)"
    if hasattr(obj, "model_dump_json"):
        s = obj.model_dump_json(exclude_none=True)
    elif isinstance(obj, str):
        s = obj
    else:
        s = str(obj)
    return s if len(s) <= max_chars else s[:max_chars - 1] + "…"


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
