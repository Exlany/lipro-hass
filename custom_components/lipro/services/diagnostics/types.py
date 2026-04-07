"""Type definitions for diagnostics services.

This module contains TypedDict, Protocol, and type alias definitions
used by diagnostics service handlers.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterator
from typing import Protocol, TypedDict

from aiohttp import ClientSession

from homeassistant.core import HomeAssistant, ServiceCall

from ...core.api.types import DiagnosticsApiResponse
from ...core.command.result import CommandResultPayload, CommandResultPollingState
from ...core.device import LiproDevice
from ...runtime_types import LiproCoordinator


# Response TypedDicts
class DeveloperReportResponse(TypedDict, total=False):
    """Response payload returned by the developer-report service."""

    entry_count: int
    reports: list[DeveloperReport]
    requested_entry_id: str


class DeveloperFeedbackResponse(TypedDict, total=False):
    """Response payload returned by developer-feedback submission."""

    success: bool
    message: str
    submitted_entries: int
    requested_entry_id: str


class CapabilityResponse(TypedDict):
    """Envelope used by optional diagnostics capabilities."""

    result: CapabilityPayload


class SensorHistoryResponse(TypedDict):
    """Structured sensor-history response payload."""

    serial: str
    sensor_device_id: str
    mesh_type: str
    result: DiagnosticsApiResponse


class FailureSummaryPayload(TypedDict, total=False):
    """Shared failure-summary vocabulary for diagnostics-service payloads."""

    failure_category: str | None
    failure_origin: str | None
    handling_policy: str | None
    error_type: str | None


class LastErrorPayload(TypedDict, total=False):
    """Serializable API error details for diagnostics output."""

    code: int | str
    message: str
    failure_summary: FailureSummaryPayload


class QueryCommandResultResponse(TypedDict, total=False):
    """Response payload for query_command_result diagnostics."""

    serial: str
    msg_sn: str
    max_attempts: int
    time_budget_seconds: float
    state: CommandResultPollingState
    attempts: int
    attempt_limit: int
    retry_delays_seconds: list[float]
    result: CommandResultPayload | None
    last_error: LastErrorPayload


# Protocol definitions
type DiagnosticsCoordinator = LiproCoordinator
type DiagnosticsDevice = LiproDevice


class DeveloperFeedbackShareManager(Protocol):
    """Share manager surface needed by developer-feedback submission."""

    async def submit_developer_feedback(
        self,
        session: ClientSession,
        payload: DeveloperFeedbackPayload,
    ) -> bool:
        """Submit the serialized developer-feedback payload."""


# Type aliases
type DeveloperFeedbackPayload = dict[str, object]
type DeveloperReport = dict[str, object]
type CapabilityPayload = dict[str, object]
type SensorHistoryClientMethod = Callable[..., Awaitable[DiagnosticsApiResponse]]
type DeveloperReportCollector = Callable[..., list[DeveloperReport]]
type DiagnosticsCoordinatorIterator = Callable[[HomeAssistant], Iterator[LiproCoordinator]]
type RuntimeCoordinatorIterator = DiagnosticsCoordinatorIterator
type RuntimeEntryResolver = Callable[[HomeAssistant, LiproCoordinator], object | None]
type EntryTelemetryViewGetter = Callable[[object, str], object | None]
type AnonymousShareManagerFactory = Callable[..., DeveloperFeedbackShareManager]
type ClientSessionGetter = Callable[[HomeAssistant], ClientSession]
type GetDeviceAndCoordinator = Callable[[HomeAssistant, ServiceCall], Awaitable[tuple[LiproDevice, LiproCoordinator]]]
type OptionalCapabilityCaller = Callable[..., Awaitable[DiagnosticsApiResponse]]
type SensorHistoryResultBuilder = Callable[..., SensorHistoryResponse]
