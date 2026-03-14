"""Service registration tables and debug-mode gating for Lipro."""

from __future__ import annotations

from typing import Final

from homeassistant.core import SupportsResponse

from ..control.runtime_access import (
    has_debug_mode_runtime_entry,
    is_debug_mode_enabled_for_entry,
)
from ..control.service_router import (
    async_handle_add_schedule,
    async_handle_delete_schedules,
    async_handle_fetch_body_sensor_history,
    async_handle_fetch_door_sensor_history,
    async_handle_get_anonymous_share_report,
    async_handle_get_city,
    async_handle_get_developer_report,
    async_handle_get_schedules,
    async_handle_query_command_result,
    async_handle_query_user_cloud,
    async_handle_refresh_devices,
    async_handle_send_command,
    async_handle_submit_anonymous_share,
    async_handle_submit_developer_feedback,
)
from . import contracts as _contracts
from .registry import ServiceRegistration

PUBLIC_SERVICE_REGISTRATIONS: Final[tuple[ServiceRegistration, ...]] = (
    ServiceRegistration(
        _contracts.SERVICE_SEND_COMMAND,
        async_handle_send_command,
        _contracts.SERVICE_SEND_COMMAND_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_GET_SCHEDULES,
        async_handle_get_schedules,
        _contracts.SERVICE_GET_SCHEDULES_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_ADD_SCHEDULE,
        async_handle_add_schedule,
        _contracts.SERVICE_ADD_SCHEDULE_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_DELETE_SCHEDULES,
        async_handle_delete_schedules,
        _contracts.SERVICE_DELETE_SCHEDULES_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_SUBMIT_ANONYMOUS_SHARE,
        async_handle_submit_anonymous_share,
        _contracts.SERVICE_SUBMIT_ANONYMOUS_SHARE_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_GET_ANONYMOUS_SHARE_REPORT,
        async_handle_get_anonymous_share_report,
        _contracts.SERVICE_GET_ANONYMOUS_SHARE_REPORT_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_REFRESH_DEVICES,
        async_handle_refresh_devices,
        _contracts.SERVICE_REFRESH_DEVICES_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
)

DEVELOPER_SERVICE_REGISTRATIONS: Final[tuple[ServiceRegistration, ...]] = (
    ServiceRegistration(
        _contracts.SERVICE_GET_DEVELOPER_REPORT,
        async_handle_get_developer_report,
        _contracts.SERVICE_GET_DEVELOPER_REPORT_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_SUBMIT_DEVELOPER_FEEDBACK,
        async_handle_submit_developer_feedback,
        _contracts.SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_QUERY_COMMAND_RESULT,
        async_handle_query_command_result,
        _contracts.SERVICE_QUERY_COMMAND_RESULT_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_GET_CITY,
        async_handle_get_city,
        None,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_QUERY_USER_CLOUD,
        async_handle_query_user_cloud,
        None,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_FETCH_BODY_SENSOR_HISTORY,
        async_handle_fetch_body_sensor_history,
        _contracts.SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_FETCH_DOOR_SENSOR_HISTORY,
        async_handle_fetch_door_sensor_history,
        _contracts.SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
        SupportsResponse.ONLY,
    ),
)

SERVICE_REGISTRATIONS: Final[tuple[ServiceRegistration, ...]] = (
    PUBLIC_SERVICE_REGISTRATIONS + DEVELOPER_SERVICE_REGISTRATIONS
)


__all__ = [
    "DEVELOPER_SERVICE_REGISTRATIONS",
    "PUBLIC_SERVICE_REGISTRATIONS",
    "SERVICE_REGISTRATIONS",
    "has_debug_mode_runtime_entry",
    "is_debug_mode_enabled_for_entry",
]
