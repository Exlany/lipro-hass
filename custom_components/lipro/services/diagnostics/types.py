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
from ...core.command.result import CommandResultPayload
from ...runtime_types import LiproCoordinator
from ..execution import AuthenticatedCoordinator


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


class LastErrorPayload(TypedDict, total=False):
    """Serializable API error details for diagnostics output."""

    code: int | str
    message: str


class QueryCommandResultResponse(TypedDict, total=False):
    """Response payload for query_command_result diagnostics."""

    serial: str
    msg_sn: str
    max_attempts: int
    time_budget_seconds: float
    state: str
    attempts: int
    attempt_limit: int
    retry_delays_seconds: list[float]
    result: CommandResultPayload | None
    last_error: LastErrorPayload


# Protocol definitions
class DiagnosticsCoordinator(AuthenticatedCoordinator, Protocol):
    """Coordinator facade required by diagnostics services."""

    async def async_query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: str | int,
    ) -> CommandResultPayload:
        """Query one command-result payload."""

    async def async_get_city(self) -> CapabilityPayload:
        """Return city metadata from the backend."""

    async def async_query_user_cloud(self) -> CapabilityPayload:
        """Return user-cloud metadata from the backend."""

    async def async_fetch_body_sensor_history(
        self,
        *,
        device_id: str,
        device_type: str | int,
        sensor_device_id: str,
        mesh_type: str,
    ) -> DiagnosticsApiResponse:
        """Fetch body-sensor history diagnostics."""

    async def async_fetch_door_sensor_history(
        self,
        *,
        device_id: str,
        device_type: str | int,
        sensor_device_id: str,
        mesh_type: str,
    ) -> DiagnosticsApiResponse:
        """Fetch door-sensor history diagnostics."""


class DeveloperReportCoordinator(DiagnosticsCoordinator, Protocol):
    """Coordinator contract that can build developer reports."""

    def build_developer_report(self) -> DeveloperReport:
        """Build one serialized developer report."""


class DiagnosticsDevice(Protocol):
    """Device contract required by diagnostics services."""

    serial: str
    name: str
    device_type: int | str
    device_type_hex: str


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
# Keep developer-report collection separate from capability iterators so exporter
# fallback can continue to work with lighter runtime coordinators.
type DeveloperReport = dict[str, object]
type CapabilityPayload = dict[str, object]
type SensorHistoryClientMethod = Callable[..., Awaitable[DiagnosticsApiResponse]]
type DeveloperReportCollector = Callable[..., list[DeveloperReport]]
type DiagnosticsCoordinatorIterator = Callable[
    [HomeAssistant], Iterator[DiagnosticsCoordinator]
]
type DeveloperReportCoordinatorIterator = Callable[
    [HomeAssistant], Iterator[LiproCoordinator]
]
type RuntimeCoordinatorIterator = DiagnosticsCoordinatorIterator
type AnonymousShareManagerFactory = Callable[..., DeveloperFeedbackShareManager]
type ClientSessionGetter = Callable[[HomeAssistant], ClientSession]
type GetDeviceAndCoordinator = Callable[
    [HomeAssistant, ServiceCall],
    Awaitable[tuple[DiagnosticsDevice, DiagnosticsCoordinator]],
]
type OptionalCapabilityCaller = Callable[..., Awaitable[DiagnosticsApiResponse]]
type SensorHistoryResultBuilder = Callable[..., SensorHistoryResponse]
