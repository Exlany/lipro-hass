"""MQTT message deduplication logic."""

from __future__ import annotations

from collections.abc import Mapping
from time import monotonic
from typing import Any, Final

from .....const.api import MAX_MQTT_CACHE_SIZE
from ....mqtt.message import (
    build_dedup_cache_key,
    cleanup_dedup_cache,
    compute_properties_hash,
    is_duplicate_within_window,
)

# Time threshold (seconds) for cleaning stale MQTT dedup cache entries.
_MQTT_CACHE_STALE_SECONDS: Final[float] = 5.0


class MqttDedupManager:
    """Manages MQTT message deduplication cache."""

    def __init__(self, *, dedup_window: float = 0.5) -> None:
        """Initialize dedup manager.

        Args:
            dedup_window: Time window in seconds for duplicate detection
        """
        self._dedup_window = dedup_window
        self._message_cache: dict[tuple[str, int], float] = {}

    def is_duplicate(
        self,
        device_id: str,
        properties: Mapping[str, Any],
        *,
        current_time: float | None = None,
    ) -> bool:
        """Check if message is a duplicate within the dedup window.

        Args:
            device_id: Device identifier
            properties: Message properties payload
            current_time: Current timestamp (defaults to monotonic())

        Returns:
            True if message is a duplicate, False otherwise
        """
        payload_hash = compute_properties_hash(dict(properties))
        if payload_hash is None:
            return False

        cache_key = build_dedup_cache_key(device_id, payload_hash)
        now = monotonic() if current_time is None else current_time

        if is_duplicate_within_window(
            self._message_cache,
            cache_key=cache_key,
            current_time=now,
            dedup_window=self._dedup_window,
        ):
            return True

        self._message_cache[cache_key] = now
        return False

    def cleanup(self, *, current_time: float | None = None) -> None:
        """Clean up stale cache entries.

        Args:
            current_time: Current timestamp (defaults to monotonic())
        """
        now = monotonic() if current_time is None else current_time
        self._message_cache = cleanup_dedup_cache(
            self._message_cache,
            current_time=now,
            stale_seconds=_MQTT_CACHE_STALE_SECONDS,
            max_entries=MAX_MQTT_CACHE_SIZE,
        )

    def reset(self) -> None:
        """Clear all cache entries."""
        self._message_cache.clear()
