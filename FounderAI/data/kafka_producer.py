"""
Kafka producer for FounderAI pipeline events.
"""
from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from kafka import KafkaProducer as _KafkaProducer
    from kafka.errors import KafkaError

    _KAFKA_AVAILABLE = True
except ImportError:
    _KAFKA_AVAILABLE = False


TOPIC_AGENT_UPDATES = "founderai.agent.updates"
TOPIC_BLUEPRINTS_COMPLETED = "founderai.blueprints.completed"


class KafkaEventProducer:
    """
    Thin wrapper around KafkaProducer.
    Gracefully degrades to a no-op logger if Kafka is unavailable.
    """

    def __init__(self, bootstrap_servers: str = "kafka:9092") -> None:
        self._producer = None
        if _KAFKA_AVAILABLE:
            try:
                self._producer = _KafkaProducer(
                    bootstrap_servers=bootstrap_servers.split(","),
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    retries=3,
                    acks="all",
                )
                logger.info("Kafka producer connected to %s", bootstrap_servers)
            except Exception as exc:
                logger.warning("Kafka unavailable (%s) — events will be logged only", exc)

    def send(self, topic: str, event: dict[str, Any]) -> None:
        if self._producer:
            try:
                self._producer.send(topic, event)
            except Exception as exc:
                logger.error("Failed to send Kafka event: %s", exc)
        else:
            logger.debug("Kafka event (no-op): topic=%s event=%s", topic, event)

    def flush(self) -> None:
        if self._producer:
            self._producer.flush()

    def close(self) -> None:
        if self._producer:
            self._producer.close()
