"""Command expectation models for coordinator reconciliation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PendingCommandExpectation:
    """Track pending command values until observed in status updates."""

    sent_at: float
    expected: dict[str, str]

    def is_expired(self, now: float, timeout_seconds: float) -> bool:
        """Return True when pending expectation exceeded timeout."""
        return now - self.sent_at > timeout_seconds

    def stale_keys(self, properties: dict[str, Any]) -> set[str]:
        """Return keys that still conflict with expected values."""
        return {
            key
            for key, value in properties.items()
            if key in self.expected and str(value) != self.expected[key]
        }

    def observe(self, properties: dict[str, Any]) -> bool:
        """Consume matching keys from an observed property update.

        Returns True when all expected keys are confirmed.
        """
        for key in list(self.expected):
            value = properties.get(key)
            if value is not None and str(value) == self.expected[key]:
                self.expected.pop(key, None)
        return not self.expected
