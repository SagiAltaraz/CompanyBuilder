"""
Kafka event schemas for blueprint pipeline events.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional


@dataclass
class AgentUpdateEvent:
    blueprint_id: str
    agent_name: str
    status: Literal["running", "done", "error"]
    output: str = ""
    duration_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    event_type: str = "agent_update"

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "blueprint_id": self.blueprint_id,
            "agent_name": self.agent_name,
            "status": self.status,
            "output": self.output,
            "duration_ms": self.duration_ms,
            "tokens_used": self.tokens_used,
            "model_used": self.model_used,
            "timestamp": self.timestamp,
        }


@dataclass
class BlueprintCompletedEvent:
    blueprint_id: str
    language: str
    report_preview: str = ""
    total_tokens: int = 0
    total_duration_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    event_type: str = "blueprint_completed"

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "blueprint_id": self.blueprint_id,
            "language": self.language,
            "report_preview": self.report_preview[:500],
            "total_tokens": self.total_tokens,
            "total_duration_ms": self.total_duration_ms,
            "timestamp": self.timestamp,
        }
