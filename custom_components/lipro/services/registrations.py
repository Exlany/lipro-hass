"""Service registration tables and debug-mode gating for Lipro."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from homeassistant.core import HomeAssistant, SupportsResponse

from ..const.base import DOMAIN
from ..const.config import CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE
from ..control.service_router import (
    _async_handle_add_schedule,
    _async_handle_delete_schedules,
    _async_handle_fetch_body_sensor_history,
    _async_handle_fetch_door_sensor_history,
    _async_handle_get_anonymous_share_report,
    _async_handle_get_city,
    _async_handle_get_developer_report,
    _async_handle_get_schedules,
    _async_handle_query_command_result,
    _async_handle_query_user_cloud,
    _async_handle_refresh_devices,
    _async_handle_send_command,
    _async_handle_submit_anonymous_share,
    _async_handle_submit_developer_feedback,
)
from . import contracts as _contracts
from .registry import ServiceRegistration

PUBLIC_SERVICE_REGISTRATIONS: Final[tuple[ServiceRegistration, ...]] = (
    ServiceRegistration(
        _contracts.SERVICE_SEND_COMMAND,
        _async_handle_send_command,
        _contracts.SERVICE_SEND_COMMAND_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_GET_SCHEDULES,
        _async_handle_get_schedules,
        _contracts.SERVICE_GET_SCHEDULES_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_ADD_SCHEDULE,
        _async_handle_add_schedule,
        _contracts.SERVICE_ADD_SCHEDULE_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_DELETE_SCHEDULES,
        _async_handle_delete_schedules,
        _contracts.SERVICE_DELETE_SCHEDULES_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_SUBMIT_ANONYMOUS_SHARE,
        _async_handle_submit_anonymous_share,
        _contracts.SERVICE_SUBMIT_ANONYMOUS_SHARE_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_GET_ANONYMOUS_SHARE_REPORT,
        _async_handle_get_anonymous_share_report,
        _contracts.SERVICE_GET_ANONYMOUS_SHARE_REPORT_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_REFRESH_DEVICES,
        _async_handle_refresh_devices,
        _contracts.SERVICE_REFRESH_DEVICES_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
)

DEVELOPER_SERVICE_REGISTRATIONS: Final[tuple[ServiceRegistration, ...]] = (
    ServiceRegistration(
        _contracts.SERVICE_GET_DEVELOPER_REPORT,
        _async_handle_get_developer_report,
        _contracts.SERVICE_GET_DEVELOPER_REPORT_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_SUBMIT_DEVELOPER_FEEDBACK,
        _async_handle_submit_developer_feedback,
        _contracts.SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_QUERY_COMMAND_RESULT,
        _async_handle_query_command_result,
        _contracts.SERVICE_QUERY_COMMAND_RESULT_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_GET_CITY,
        _async_handle_get_city,
        None,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_QUERY_USER_CLOUD,
        _async_handle_query_user_cloud,
        None,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_FETCH_BODY_SENSOR_HISTORY,
        _async_handle_fetch_body_sensor_history,
        _contracts.SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_FETCH_DOOR_SENSOR_HISTORY,
        _async_handle_fetch_door_sensor_history,
        _contracts.SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
        SupportsResponse.ONLY,
    ),
)

SERVICE_REGISTRATIONS: Final[tuple[ServiceRegistration, ...]] = (
    PUBLIC_SERVICE_REGISTRATIONS + DEVELOPER_SERVICE_REGISTRATIONS
)


def is_debug_mode_enabled_for_entry(entry: Any) -> bool:
    """Return whether one config entry has developer diagnostics enabled."""
    options = getattr(entry, "options", None)
    if not isinstance(options, Mapping):
        return DEFAULT_DEBUG_MODE
    return bool(options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE))


def has_debug_mode_runtime_entry(hass: HomeAssistant) -> bool:
    """Return True when any active Lipro runtime entry opts into debug mode."""
    return any(
        getattr(entry, "runtime_data", None) is not None
        and is_debug_mode_enabled_for_entry(entry)
        for entry in hass.config_entries.async_entries(DOMAIN)
    )


__all__ = [
    "DEVELOPER_SERVICE_REGISTRATIONS",
    "PUBLIC_SERVICE_REGISTRATIONS",
    "SERVICE_REGISTRATIONS",
    "has_debug_mode_runtime_entry",
    "is_debug_mode_enabled_for_entry",
]
