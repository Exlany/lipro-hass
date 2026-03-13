"""Formal telemetry contracts for exporter-owned assurance views."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SCHEMA_VERSION = "telemetry.v1"


_BLOCKED_KEYS = frozenset(
    {
        "access_token",
        "accesskey",
        "biz_id",
        "bizid",
        "device_id",
        "deviceid",
        "gatewaydeviceid",
        "gateway_device_id",
        "password",
        "passwordhash",
        "password_hash",
        "phone",
        "phone_id",
        "phoneid",
        "refresh_access_key",
        "refresh_token",
        "refreshaccesskey",
        "refreshtoken",
        "secret",
        "secret_key",
        "secretkey",
        "serial",
        "user_id",
        "userid",
    }
)

_REFERENCE_ALIASES = {
    "device_id": "device_ref",
    "deviceid": "device_ref",
    "device_name": "device_ref",
    "devicename": "device_ref",
    "device_serial": "device_ref",
    "deviceserial": "device_ref",
    "entry_id": "entry_ref",
    "entryid": "entry_ref",
    "gateway_device_id": "device_ref",
    "gatewaydeviceid": "device_ref",
    "group_id": "device_ref",
    "groupid": "device_ref",
    "serial": "device_ref",
}


def normalize_telemetry_key(key: str) -> str:
    """Normalize one telemetry field name for policy lookup."""
    return key.lower().replace("-", "_")


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
        return normalized in self.blocked_keys

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


@dataclass(frozen=True, slots=True)
class TelemetrySnapshot:
    """Normalized exporter snapshot shared by all sinks."""

    schema_version: str
    report_id: str
    generated_at: float
    entry_ref: str | None
    protocol: dict[str, Any]
    runtime: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation of the snapshot."""
        return {
            "schema_version": self.schema_version,
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "entry_ref": self.entry_ref,
            "protocol": self.protocol,
            "runtime": self.runtime,
        }


@dataclass(frozen=True, slots=True)
class TelemetryViews:
    """Exporter projections for diagnostics/system-health/developer/CI."""

    snapshot: TelemetrySnapshot
    diagnostics: dict[str, Any]
    system_health: dict[str, Any]
    developer: dict[str, Any]
    ci: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return all sink views in a stable dictionary shape."""
        return {
            "snapshot": self.snapshot.to_dict(),
            "diagnostics": self.diagnostics,
            "system_health": self.system_health,
            "developer": self.developer,
            "ci": self.ci,
        }


__all__ = [
    "SCHEMA_VERSION",
    "CardinalityBudget",
    "TelemetrySensitivity",
    "TelemetrySnapshot",
    "TelemetryViews",
    "normalize_telemetry_key",
]
