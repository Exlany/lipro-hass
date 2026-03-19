"""Topic-building helpers extracted from the MQTT transport."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
import logging
from typing import Final

from ..utils.redaction import redact_identifier as _redact_identifier
from .topics import build_topic

_LOGGER = logging.getLogger(__package__ or __name__)
_DEFAULT_BATCH_SIZE: Final[int] = 50


@dataclass(slots=True)
class MqttTopicBuilder:
    """Build validated MQTT topic batches for device subscriptions."""

    biz_id: str
    batch_size: int = _DEFAULT_BATCH_SIZE

    def build_topic_pairs(
        self,
        device_ids: Iterable[str],
        *,
        invalid_log_message: str,
        on_invalid: Callable[[str], None] | None = None,
    ) -> list[tuple[str, str]]:
        """Build valid MQTT topic pairs while centralizing invalid-ID handling."""
        topic_pairs: list[tuple[str, str]] = []
        for device_id in device_ids:
            try:
                topic = build_topic(self.biz_id, device_id)
            except ValueError:
                if on_invalid is not None:
                    on_invalid(device_id)
                _LOGGER.warning(
                    invalid_log_message,
                    _redact_identifier(device_id) or "***",
                )
                continue
            topic_pairs.append((device_id, topic))
        return topic_pairs

    def batch_topic_pairs(
        self,
        topic_pairs: list[tuple[str, str]],
    ) -> list[list[tuple[str, str]]]:
        """Split topic pairs into MQTT-sized batches."""
        return [
            topic_pairs[i : i + self.batch_size]
            for i in range(0, len(topic_pairs), self.batch_size)
        ]
