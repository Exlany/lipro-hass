"""Coordinator runtime telemetry surface."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...telemetry.models import (
    FailureSummary,
    build_failure_summary_from_exception,
    empty_failure_summary,
)
from ..types import (
    CommandTrace,
    ConnectStateEvent,
    GroupReconciliationRequestEvent,
    MetricMapping,
    RuntimeTelemetrySnapshot,
)

if TYPE_CHECKING:
    from ..runtime.command_runtime import CommandRuntime
    from ..runtime.mqtt_runtime import MqttRuntime
    from ..runtime.status_runtime import StatusRuntime
    from ..runtime.tuning_runtime import TuningRuntime
    from .device_refresh_service import CoordinatorDeviceRefreshService
    from .mqtt_service import CoordinatorMqttService


@dataclass(slots=True)
class CoordinatorTelemetryService:
    """Expose stable runtime telemetry for diagnostics and assurance."""

    mqtt_service: CoordinatorMqttService
    command_runtime: CommandRuntime
    status_runtime: StatusRuntime
    tuning_runtime: TuningRuntime
    mqtt_runtime_getter: Callable[[], MqttRuntime]
    device_count_getter: Callable[[], int]
    polling_interval_seconds_getter: Callable[[], int | None]
    _connect_state_events: deque[ConnectStateEvent] = field(
        default_factory=lambda: deque(maxlen=20),
        init=False,
        repr=False,
    )
    _group_reconciliation_requests: deque[GroupReconciliationRequestEvent] = field(
        default_factory=lambda: deque(maxlen=20),
        init=False,
        repr=False,
    )
    _failure_summary: FailureSummary = field(
        default_factory=empty_failure_summary,
        init=False,
        repr=False,
    )
    _failure_stage: str | None = field(default=None, init=False, repr=False)

    def record_connect_state(
        self,
        *,
        device_serial: str,
        timestamp: float,
        is_online: bool,
    ) -> None:
        """Record one connect-state observation for diagnostics/assurance."""
        self._connect_state_events.append(
            {
                "device_serial": device_serial,
                "timestamp": timestamp,
                "is_online": is_online,
            }
        )

    def record_group_reconciliation_request(
        self,
        *,
        device_name: str,
        timestamp: float,
    ) -> None:
        """Record one group reconciliation request signal."""
        self._group_reconciliation_requests.append(
            {
                "device_name": device_name,
                "timestamp": timestamp,
            }
        )

    def record_update_failure(self, err: Exception | None, *, stage: str) -> None:
        """Record one coordinator update failure as runtime telemetry truth."""
        self._failure_stage = stage if err is not None else None
        self._failure_summary = build_failure_summary_from_exception(
            err,
            failure_origin="runtime.update",
        )

    def record_update_success(self) -> None:
        """Clear the last coordinator update failure after a successful run."""
        self._failure_stage = None
        self._failure_summary = empty_failure_summary()

    @staticmethod
    def _failure_summary_mapping(summary: FailureSummary) -> MetricMapping:
        return dict(summary)

    def build_snapshot(self) -> RuntimeTelemetrySnapshot:
        """Build one runtime telemetry snapshot."""
        mqtt_runtime = self.mqtt_runtime_getter()
        mqtt_snapshot: MetricMapping = {
            "connected": self.mqtt_service.connected,
            **mqtt_runtime.get_runtime_metrics(),
        }
        return {
            "device_count": self.device_count_getter(),
            "polling_interval_seconds": self.polling_interval_seconds_getter(),
            "failure_summary": self._failure_summary_mapping(self._failure_summary),
            "last_runtime_failure_stage": self._failure_stage,
            "mqtt": mqtt_snapshot,
            "command": self.command_runtime.get_runtime_metrics(),
            "status": self.status_runtime.get_runtime_metrics(),
            "tuning": self.tuning_runtime.get_runtime_metrics(),
            "signals": {
                "connect_state_event_count": len(self._connect_state_events),
                "group_reconciliation_request_count": len(
                    self._group_reconciliation_requests
                ),
                "recent_connect_state_events": list(self._connect_state_events),
                "recent_group_reconciliation_requests": list(
                    self._group_reconciliation_requests
                ),
            },
            "recent_command_traces": self.command_runtime.get_recent_traces(limit=20),
        }

    def get_recent_command_traces(self, limit: int | None = None) -> list[CommandTrace]:
        """Return recent command traces for diagnostics consumers."""
        return self.command_runtime.get_recent_traces(limit=limit)


@dataclass(slots=True)
class CoordinatorSignalService:
    """Formal runtime signal ports consumed by runtime wiring only."""

    telemetry_service_getter: Callable[[], CoordinatorTelemetryService]
    device_refresh_service_getter: Callable[[], CoordinatorDeviceRefreshService]

    def record_connect_state(
        self,
        device_serial: str,
        timestamp: float,
        is_online: bool,
    ) -> None:
        """Route one MQTT connect-state observation into telemetry."""
        self.telemetry_service_getter().record_connect_state(
            device_serial=device_serial,
            timestamp=timestamp,
            is_online=is_online,
        )

    def schedule_group_reconciliation(
        self,
        device_name: str,
        timestamp: float,
    ) -> None:
        """Route one group-online signal into telemetry + canonical refresh."""
        self.telemetry_service_getter().record_group_reconciliation_request(
            device_name=device_name,
            timestamp=timestamp,
        )
        self.device_refresh_service_getter().request_group_reconciliation(
            device_name=device_name,
            timestamp=timestamp,
        )


__all__ = ["CoordinatorSignalService", "CoordinatorTelemetryService"]
