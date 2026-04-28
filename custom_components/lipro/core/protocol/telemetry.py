"""Protocol-root telemetry owned above transport-specific child facades."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..telemetry.models import (
    FailureSummary,
    build_failure_summary_from_exception,
    empty_failure_summary,
)


@dataclass(slots=True)
class ProtocolTelemetry:
    """Shared protocol telemetry summary.

    This intentionally stays lightweight in Phase 2.5: the goal is to provide a
    single owner for protocol-level transport observations rather than duplicate
    per-transport truth.
    """

    mqtt_facades_created: int = 0
    mqtt_start_count: int = 0
    mqtt_stop_count: int = 0
    mqtt_sync_count: int = 0
    mqtt_last_error_type: str | None = None
    mqtt_last_error_stage: str | None = None
    failure_summary: FailureSummary = field(default_factory=empty_failure_summary)

    def record_mqtt_facade_created(self) -> None:
        """Record creation of one MQTT child façade."""
        self.mqtt_facades_created += 1

    def record_mqtt_start(self) -> None:
        """Record one MQTT startup attempt."""
        self.mqtt_start_count += 1

    def record_mqtt_stop(self) -> None:
        """Record one MQTT shutdown call."""
        self.mqtt_stop_count += 1

    def record_mqtt_sync(self) -> None:
        """Record one MQTT subscription-sync call."""
        self.mqtt_sync_count += 1

    def record_mqtt_error(
        self, err: Exception | None, *, stage: str | None = None
    ) -> None:
        """Record the latest MQTT transport error type and normalized summary."""
        self.mqtt_last_error_type = type(err).__name__ if err is not None else None
        self.mqtt_last_error_stage = stage if err is not None else None
        self.failure_summary = build_failure_summary_from_exception(
            err,
            failure_origin="protocol.mqtt",
        )

    def snapshot(
        self,
        *,
        mqtt_connected: bool | None,
        subscribed_count: int | None,
    ) -> dict[str, Any]:
        """Return a transport-neutral telemetry snapshot."""
        return {
            "mqtt_facades_created": self.mqtt_facades_created,
            "mqtt_start_count": self.mqtt_start_count,
            "mqtt_stop_count": self.mqtt_stop_count,
            "mqtt_sync_count": self.mqtt_sync_count,
            "mqtt_connected": mqtt_connected,
            "mqtt_subscribed_count": subscribed_count,
            "mqtt_last_error_type": self.mqtt_last_error_type,
            "mqtt_last_error_stage": self.mqtt_last_error_stage,
            "failure_summary": dict(self.failure_summary),
        }


__all__ = ["ProtocolTelemetry"]
