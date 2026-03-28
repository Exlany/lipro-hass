"""Internal transport/notification support helpers for MQTT runtime."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import logging
from time import monotonic
from typing import Protocol, TypeVar

from ....const.api import MQTT_DISCONNECT_NOTIFY_THRESHOLD
from ...telemetry.models import FailureSummary
from ..types import RuntimeMetrics

_ResultT = TypeVar("_ResultT")
_TransportFacadeT = TypeVar("_TransportFacadeT", bound="_TransportFacadeProtocol")


class _TransportFacadeProtocol(Protocol):
    async def start(self, device_ids: list[str]) -> None: ...
    async def sync_subscriptions(self, device_ids: set[str]) -> None: ...
    async def wait_until_connected(self) -> bool: ...
    async def stop(self) -> None: ...


class _ConnectionManagerProtocol(Protocol):
    @property
    def is_connected(self) -> bool: ...

    @property
    def disconnect_time(self) -> float | None: ...

    @property
    def disconnect_notified(self) -> bool: ...

    def mark_disconnect_notified(self) -> None: ...


class _ReconnectManagerProtocol(Protocol):
    def on_reconnect_failure(self) -> None: ...

    @property
    def backoff_gate_logged(self) -> bool: ...


async def run_transport_operation(
    *,
    stage: str,
    action: str,
    operation: Callable[[], Awaitable[_ResultT]],
    handle_transport_error: Callable[[Exception], None],
    logger: logging.Logger,
) -> tuple[bool, _ResultT | None]:
    """Run one transport operation with explicit failure recording."""
    try:
        return True, await operation()
    except asyncio.CancelledError:
        raise
    except (
        TimeoutError,
        OSError,
        RuntimeError,
        ValueError,
        TypeError,
        LookupError,
    ) as err:
        handle_transport_error(err)
        logger.exception("MQTT %s failed", action)
        return False, None


def require_transport(
    mqtt_transport: _TransportFacadeT | None,
    *,
    logger: logging.Logger,
    log_missing: bool = False,
) -> _TransportFacadeT | None:
    """Return the bound transport when available."""
    if mqtt_transport is not None:
        return mqtt_transport
    if log_missing:
        logger.error("MQTT transport not initialized")
    return None


def finalize_connect_attempt(
    *,
    connected: bool,
    reconnect_manager: _ReconnectManagerProtocol,
) -> bool:
    """Record reconnect bookkeeping for one connect attempt."""
    if connected:
        return True
    reconnect_manager.on_reconnect_failure()
    return False


def disconnect_notification_minutes(
    *,
    connection_manager: _ConnectionManagerProtocol,
    current_time: float | None = None,
    threshold: float = MQTT_DISCONNECT_NOTIFY_THRESHOLD,
) -> int | None:
    """Return disconnect duration in minutes once notification threshold is met."""
    if connection_manager.is_connected or connection_manager.disconnect_notified:
        return None
    disconnect_time = connection_manager.disconnect_time
    if disconnect_time is None:
        return None
    elapsed = (monotonic() if current_time is None else current_time) - disconnect_time
    if elapsed < threshold:
        return None
    return int(elapsed // 60)


def had_disconnect_state(connection_manager: _ConnectionManagerProtocol) -> bool:
    """Return whether the runtime still carries disconnect-side effects."""
    return (
        connection_manager.disconnect_notified
        or connection_manager.disconnect_time is not None
    )


def consume_background_task_exception(task: asyncio.Task[object]) -> None:
    """Consume background-task exceptions so they surface deterministically."""
    if not task.cancelled():
        task.exception()


def build_runtime_metrics(
    *,
    has_transport: bool,
    connection_manager: _ConnectionManagerProtocol,
    last_transport_error: Exception | None,
    last_transport_error_stage: str | None,
    failure_summary: FailureSummary,
    reconnect_manager: _ReconnectManagerProtocol,
) -> RuntimeMetrics:
    """Return lightweight MQTT runtime telemetry payload."""
    return {
        "has_transport": has_transport,
        "is_connected": connection_manager.is_connected,
        "disconnect_time": connection_manager.disconnect_time,
        "disconnect_notified": connection_manager.disconnect_notified,
        "last_transport_error": (
            type(last_transport_error).__name__ if last_transport_error is not None else None
        ),
        "last_transport_error_stage": last_transport_error_stage,
        "failure_summary": dict(failure_summary),
        "backoff_gate_logged": reconnect_manager.backoff_gate_logged,
    }


__all__ = [
    "build_runtime_metrics",
    "consume_background_task_exception",
    "disconnect_notification_minutes",
    "finalize_connect_attempt",
    "had_disconnect_state",
    "require_transport",
    "run_transport_operation",
]
