"""Shared Anthropic client used by every agent.

Responsibilities:
  - One AsyncAnthropic singleton (cheap: just carries config).
  - call_structured(): structured output via forced tool-use, with retries
    and a self-correction turn on ValidationError.
  - Prompt caching: system prompts are split into [cached_preamble, task_instruction]
    and the preamble gets cache_control: ephemeral.

Model IDs resolve against MODELS so every agent file names its role, not a string.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any, Optional

from anthropic import AsyncAnthropic, APIStatusError, RateLimitError
from pydantic import BaseModel, ValidationError
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

MODELS = {
    "haiku":  "claude-haiku-5-5",
    "sonnet": "claude-sonnet-5-5",
    "opus":   "claude-opus-5-5",
}

# Approximate per-1M-token prices (USD) — used only for cost estimates in the UI.
# Keep order of magnitude right; UI treats as estimate, not invoice.
PRICE_IN_PER_MTOK = {
    "claude-haiku-5-5":  1.0,
    "claude-sonnet-5-5": 3.0,
    "claude-opus-5-5":   15.0,
}
PRICE_OUT_PER_MTOK = {
    "claude-haiku-5-5":  5.0,
    "claude-sonnet-5-5": 15.0,
    "claude-opus-5-5":   75.0,
}

_client: Optional[AsyncAnthropic] = None


def get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
    return _client


def _schema_as_tool(schema: type[BaseModel], tool_name: str) -> dict:
    """Pydantic → Anthropic tool definition. Forces the model to produce JSON matching the schema."""
    return {
        "name": tool_name,
        "description": f"Return the result as a {tool_name} object.",
        "input_schema": schema.model_json_schema(),
    }


def _estimate_cost_usd(model: str, in_tok: int, out_tok: int, cached_in_tok: int = 0) -> float:
    pin  = PRICE_IN_PER_MTOK.get(model, 3.0)  / 1_000_000
    pout = PRICE_OUT_PER_MTOK.get(model, 15.0) / 1_000_000
    # Cached input is ~10% of normal input on Anthropic ephemeral caching.
    return (in_tok - cached_in_tok) * pin + cached_in_tok * pin * 0.1 + out_tok * pout


async def call_structured(
    *,
    role: str,
    cached_preamble: str,
    task_instruction: str,
    user_message: str,
    schema: type[BaseModel],
    tool_name: str,
    max_tokens: int = 2048,
    temperature: float = 0.0,
) -> tuple[BaseModel, dict]:
    """Call Claude, force a schema-shaped tool call, return (parsed, metadata).

    `cached_preamble` is the big static part of the system prompt — gets
    cache_control: ephemeral, so re-runs within ~5 minutes pay a fraction.
    `task_instruction` is the small dynamic part — not cached.

    Retries up to 3 times:
      - APIStatusError / RateLimitError: exponential backoff.
      - ValidationError: one correction turn ("your output failed validation…").
    """
    model = MODELS[role]
    client = get_client()
    start = time.perf_counter()

    system_blocks = [
        {"type": "text", "text": cached_preamble,
         "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": task_instruction},
    ]
    tool = _schema_as_tool(schema, tool_name)
    base_messages = [{"role": "user", "content": user_message}]

    last_validation_err: ValidationError | None = None

    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.0, min=1.0, max=12.0),
        retry=retry_if_exception_type((APIStatusError, RateLimitError)),
        reraise=True,
    ):
        with attempt:
            messages = list(base_messages)
            if last_validation_err is not None:
                messages.append({
                    "role": "user",
                    "content": (
                        "Your previous tool call failed schema validation with:\n"
                        f"{last_validation_err}\n\n"
                        "Call the same tool again with a corrected, valid payload."
                    ),
                })

            resp = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_blocks,
                tools=[tool],
                tool_choice={"type": "tool", "name": tool_name},
                messages=messages,
            )

            tool_use = next(
                (b for b in resp.content if getattr(b, "type", None) == "tool_use"),
                None,
            )
            if tool_use is None:
                raise RuntimeError(f"{role}: model did not call the tool")

            try:
                parsed = schema.model_validate(tool_use.input)
                break
            except ValidationError as ve:
                last_validation_err = ve
                # Stay in the retry loop to try a correction turn.
                continue

    # If we exited the loop without `parsed` being set, the last attempt still
    # failed validation. Raise.
    if last_validation_err is not None and "parsed" not in locals():
        raise last_validation_err  # type: ignore[misc]

    duration_ms = int((time.perf_counter() - start) * 1000)
    usage = resp.usage
    in_tok  = getattr(usage, "input_tokens", 0) or 0
    out_tok = getattr(usage, "output_tokens", 0) or 0
    cached  = getattr(usage, "cache_read_input_tokens", 0) or 0
    total   = in_tok + out_tok

    metadata = {
        "model_used": model,
        "duration_ms": duration_ms,
        "tokens_used": total,
        "tokens_in": in_tok,
        "tokens_out": out_tok,
        "tokens_cached": cached,
        "cost_usd": round(_estimate_cost_usd(model, in_tok, out_tok, cached), 4),
    }
    return parsed, metadata


__all__ = ["call_structured", "MODELS", "get_client"]
