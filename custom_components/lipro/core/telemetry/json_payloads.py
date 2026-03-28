"""Inward telemetry JSON/value policy helpers behind the outward contract home."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from ..utils.redaction import (
    SHARED_SENSITIVE_KEY_NAMES,
    TELEMETRY_REFERENCE_ALIASES,
    is_sensitive_key_name,
    normalize_redaction_key,
)

_REFERENCE_ALIASES: Final = dict(TELEMETRY_REFERENCE_ALIASES)
_BLOCKED_KEYS: Final = frozenset(
    key for key in SHARED_SENSITIVE_KEY_NAMES if key not in _REFERENCE_ALIASES
)


def normalize_telemetry_key(key: str) -> str:
    """Normalize one telemetry field name for policy lookup."""
    return normalize_redaction_key(key)


@dataclass(frozen=True, slots=True)
class TelemetrySensitivity:
    """Sensitivity contract used by the exporter."""

    blocked_keys: frozenset[str] = field(default_factory=lambda: _BLOCKED_KEYS)
    reference_aliases: dict[str, str] = field(
        default_factory=lambda: dict(_REFERENCE_ALIASES)
    )

    def is_blocked(self, key: str) -> bool:
        """Return whether a field must be removed from exported views."""
        normalized = normalize_telemetry_key(key)
        if normalized in self.reference_aliases:
            return False
        return normalized in self.blocked_keys or is_sensitive_key_name(normalized)

    def reference_alias_for(self, key: str) -> str | None:
        """Return the pseudonymous alias for a field, when configured."""
        normalized = normalize_telemetry_key(key)
        return self.reference_aliases.get(normalized)


@dataclass(frozen=True, slots=True)
class CardinalityBudget:
    """Budget contract preventing high-cardinality telemetry growth."""

    max_mapping_items: int = 32
    max_sequence_items: int = 20
    max_string_length: int = 256


__all__ = [
    "CardinalityBudget",
    "TelemetrySensitivity",
    "normalize_telemetry_key",
]
