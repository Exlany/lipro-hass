"""Diagnostics service module.

This module provides diagnostics service handlers split into:
- types: TypedDict, Protocol, and type alias definitions
- helpers: Utility functions for parameter extraction and capability collection
- handlers: Concrete service handler implementations

All public APIs are re-exported from this module to provide one stable diagnostics service import surface.
"""

from __future__ import annotations

# Re-export handlers
from .handlers import (
    async_handle_fetch_body_sensor_history,
    async_handle_fetch_door_sensor_history,
    async_handle_get_city,
    async_handle_query_command_result,
    async_handle_query_user_cloud,
)

# Re-export helpers
from .helpers import (
    async_call_optional_capability,
    async_handle_get_developer_report,
    async_handle_submit_developer_feedback,
    build_developer_feedback_payload,
    build_sensor_history_result,
    collect_developer_reports,
    raise_optional_capability_error,
)

# Re-export types
from .types import (
    AnonymousShareManagerFactory,
    CapabilityPayload,
    CapabilityResponse,
    ClientSessionGetter,
    DeveloperFeedbackResponse,
    DeveloperFeedbackShareManager,
    DeveloperReport,
    DeveloperReportCollector,
    DeveloperReportResponse,
    DiagnosticsCoordinator,
    DiagnosticsDevice,
    GetDeviceAndCoordinator,
    LastErrorPayload,
    OptionalCapabilityCaller,
    QueryCommandResultResponse,
    RuntimeCoordinatorIterator,
    SensorHistoryClientMethod,
    SensorHistoryResponse,
    SensorHistoryResultBuilder,
)

__all__ = [
    # Types
    "AnonymousShareManagerFactory",
    "CapabilityPayload",
    "CapabilityResponse",
    "ClientSessionGetter",
    "DeveloperFeedbackResponse",
    "DeveloperFeedbackShareManager",
    "DeveloperReport",
    "DeveloperReportCollector",
    "DeveloperReportResponse",
    "DiagnosticsCoordinator",
    "DiagnosticsDevice",
    "GetDeviceAndCoordinator",
    "LastErrorPayload",
    "OptionalCapabilityCaller",
    "QueryCommandResultResponse",
    "RuntimeCoordinatorIterator",
    "SensorHistoryClientMethod",
    "SensorHistoryResponse",
    "SensorHistoryResultBuilder",
    # Helpers
    "async_call_optional_capability",
    # Handlers
    "async_handle_fetch_body_sensor_history",
    "async_handle_fetch_door_sensor_history",
    "async_handle_get_city",
    "async_handle_get_developer_report",
    "async_handle_query_command_result",
    "async_handle_query_user_cloud",
    "async_handle_submit_developer_feedback",
    "build_developer_feedback_payload",
    "build_sensor_history_result",
    "collect_developer_reports",
    "raise_optional_capability_error",
]
