"""Pack-level redaction and report-local pseudonymization."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

from custom_components.lipro.core.telemetry.models import TelemetrySensitivity

_SKIP = object()
_REFERENCE_SUFFIXES = ("_ref",)
_EXTRA_BLOCKED_KEYS = frozenset(
    {
        "secret",
        "access_token",
        "refresh_token",
        "password",
        "password_hash",
        "phone_id",
        "phone",
        "access_key",
        "refresh_access_key",
        "token",
    }
)


@dataclass(slots=True)
class EvidencePackRedactor:
    """Apply pack-level denylist and report-local pseudonymization."""

    report_id: str
    sensitivity: TelemetrySensitivity = field(default_factory=TelemetrySensitivity)
    _reference_cache: dict[tuple[str, str], str] = field(default_factory=dict)

    def redact(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Return a recursively redacted copy of one payload mapping."""
        return self._redact_mapping(payload)

    def _redact_mapping(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            key_text = str(key)
            if self._is_blocked(key_text):
                continue
            alias = self._alias_for(key_text)
            if alias is not None:
                reference = self._build_reference(alias, value)
                if reference is not None:
                    redacted[key_text] = reference
                continue
            sanitized = self._redact_value(value, key=key_text)
            if sanitized is _SKIP:
                continue
            redacted[key_text] = sanitized
        return redacted

    def _redact_value(self, value: Any, *, key: str | None) -> Any:
        if key is not None and self._is_blocked(key):
            return _SKIP
        if isinstance(value, Mapping):
            return self._redact_mapping(value)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            items: list[Any] = []
            for item in value:
                sanitized = self._redact_value(item, key=None)
                if sanitized is _SKIP:
                    continue
                items.append(sanitized)
            return items
        return value

    def _is_blocked(self, key: str) -> bool:
        normalized = key.lower().replace("-", "_")
        if normalized in {"generated_at", "started_at", "finished_at", "timestamp"}:
            return False
        if normalized.endswith(_REFERENCE_SUFFIXES):
            return False
        if self.sensitivity.reference_alias_for(key) is not None:
            return False
        return self.sensitivity.is_blocked(key) or normalized in _EXTRA_BLOCKED_KEYS

    def _alias_for(self, key: str) -> str | None:
        normalized = key.lower().replace("-", "_")
        alias = self.sensitivity.reference_alias_for(key)
        if alias is not None:
            return alias
        if normalized.endswith(_REFERENCE_SUFFIXES):
            return normalized
        return None

    def _build_reference(self, alias: str, value: Any) -> str | None:
        if value in {None, ""}:
            return None
        raw = str(value)
        cache_key = (alias, raw)
        cached = self._reference_cache.get(cache_key)
        if cached is not None:
            return cached
        digest = sha256(f"{self.report_id}:{alias}:{raw}".encode()).hexdigest()[:10]
        reference = f"{alias}_{digest}"
        self._reference_cache[cache_key] = reference
        return reference
