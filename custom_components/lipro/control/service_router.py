"""Formal control-plane router for HA service callbacks."""

from __future__ import annotations

import logging
import re
from typing import Final, cast

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from ..const.base import DOMAIN, IOT_DEVICE_ID_PREFIX
from ..core import LiproDevice, get_anonymous_share_manager
from ..core.utils.redaction import redact_identifier as _redact_identifier
from ..runtime_types import LiproCoordinator
from ..services import contracts as _contracts
from ..services.command import (
    DeviceAndCoordinatorGetter,
    async_handle_send_command as _async_handle_send_command_service,
)
from ..services.contracts import (
    RefreshDevicesResult,
    SendCommandResult,
    ServicePropertySummary,
)
from ..services.device_lookup import (
    get_device_and_coordinator as _get_device_and_coordinator_service,
)
from ..services.diagnostics import (
    DiagnosticsCoordinator,
    DiagnosticsDevice,
    async_handle_fetch_body_sensor_history as _async_handle_fetch_body_sensor_history_service,
    async_handle_fetch_door_sensor_history as _async_handle_fetch_door_sensor_history_service,
    async_handle_get_city as _async_handle_get_city_service,
    async_handle_get_developer_report as _async_handle_get_developer_report_service,
    async_handle_query_command_result as _async_handle_query_command_result_service,
    async_handle_query_user_cloud as _async_handle_query_user_cloud_service,
    async_handle_submit_developer_feedback as _async_handle_submit_developer_feedback_service,
)
from ..services.diagnostics.types import (
    CapabilityResponse,
    DeveloperFeedbackResponse,
    DeveloperReportResponse,
    QueryCommandResultResponse,
    SensorHistoryResponse,
)
from ..services.errors import (
    raise_service_error as _raise_service_error,
    resolve_command_failure_translation_key as _resolve_command_failure_translation_key,
)
from ..services.maintenance import (
    async_handle_refresh_devices as _async_handle_refresh_devices_service,
)
from ..services.schedule import (
    async_handle_add_schedule as _async_handle_add_schedule_service,
    async_handle_delete_schedules as _async_handle_delete_schedules_service,
    async_handle_get_schedules as _async_handle_get_schedules_service,
)
from ..services.share import (
    AnonymousShareManagerFactory as ShareAnonymousShareManagerFactory,
    ShareServiceResponse,
    async_handle_get_anonymous_share_report as _async_handle_get_anonymous_share_report_service,
    async_handle_submit_anonymous_share as _async_handle_submit_anonymous_share_service,
)
from .developer_router_support import (
    async_handle_fetch_sensor_history as _async_handle_fetch_sensor_history_support,
    collect_developer_reports as _collect_developer_reports,
    raise_developer_mode_not_enabled as _raise_developer_mode_not_enabled,
    raise_optional_capability_error as _raise_optional_capability_error,
)
from .runtime_access import (
    find_runtime_entry_for_coordinator as _find_runtime_entry_for_coordinator,
    is_developer_runtime_coordinator as _is_developer_runtime_coordinator,
    iter_developer_runtime_coordinators as _iter_developer_runtime_coordinators,
)

_LOGGER = logging.getLogger(__name__)
_SERIAL_PATTERN: Final = re.compile(
    rf"({re.escape(IOT_DEVICE_ID_PREFIX)}[0-9A-Fa-f]{{12}}|mesh_group_\d+)(?:_|$)"
)


def _summarize_service_properties(
    properties: object,
) -> ServicePropertySummary:
    """Build a log-safe summary for service properties."""
    if not isinstance(properties, list):
        return {"count": 0, "keys": []}

    keys: list[str] = []
    for item in properties:
        if not isinstance(item, dict):
            continue
        key = item.get("key")
        if isinstance(key, str):
            keys.append(key)
    return {"count": len(properties), "keys": keys}


async def _get_developer_device_and_coordinator(
    hass: HomeAssistant,
    call: ServiceCall,
) -> tuple[DiagnosticsDevice, DiagnosticsCoordinator]:
    """Resolve one device/coordinator pair and require debug-mode opt-in."""
    device, coordinator = await _get_device_and_coordinator(hass, call)
    if not _is_developer_runtime_coordinator(hass, coordinator):
        entry = _find_runtime_entry_for_coordinator(hass, coordinator)
        _raise_developer_mode_not_enabled(
            entry_id=entry.entry_id if entry is not None else None
        )
    return cast(DiagnosticsDevice, device), cast(DiagnosticsCoordinator, coordinator)


def _log_send_command_call(
    requested_device_id: str | None,
    resolved_serial: str,
    command: str,
    properties_summary: ServicePropertySummary,
) -> bool:
    """Log send_command call details and return whether alias resolution occurred."""
    is_alias_resolution = bool(
        requested_device_id and requested_device_id != resolved_serial
    )

    if is_alias_resolution:
        _LOGGER.info(
            "Service call: send_command requested_id=%s resolved_to=%s, "
            "command=%s, property_summary=%s",
            _redact_identifier(requested_device_id),
            _redact_identifier(resolved_serial),
            command,
            properties_summary,
        )
    else:
        _LOGGER.info(
            "Service call: send_command to %s, command=%s, property_summary=%s",
            _redact_identifier(resolved_serial),
            command,
            properties_summary,
        )

    return is_alias_resolution


async def _get_device_and_coordinator(
    hass: HomeAssistant,
    call: ServiceCall,
) -> tuple[LiproDevice, LiproCoordinator]:
    """Get device and coordinator from service call."""
    return await _get_device_and_coordinator_service(
        hass,
        call,
        domain=DOMAIN,
        serial_pattern=_SERIAL_PATTERN,
        attr_device_id=_contracts.ATTR_DEVICE_ID,
    )


async def async_handle_send_command(
    hass: HomeAssistant, call: ServiceCall
) -> SendCommandResult:
    """Handle the send_command service call."""
    return await _async_handle_send_command_service(
        hass,
        call,
        get_device_and_coordinator=cast(
            DeviceAndCoordinatorGetter, _get_device_and_coordinator
        ),
        summarize_service_properties=_summarize_service_properties,
        log_send_command_call=_log_send_command_call,
        resolve_command_failure_translation_key=_resolve_command_failure_translation_key,
        raise_service_error=_raise_service_error,
        logger=_LOGGER,
        attr_command=_contracts.ATTR_COMMAND,
        attr_properties=_contracts.ATTR_PROPERTIES,
        attr_device_id=_contracts.ATTR_DEVICE_ID,
    )


async def async_handle_get_schedules(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, object]:
    """Handle the get_schedules service call."""
    return await _async_handle_get_schedules_service(
        hass,
        call,
        get_device_and_coordinator=_get_device_and_coordinator,
        raise_service_error=_raise_service_error,
        logger=_LOGGER,
    )


async def async_handle_add_schedule(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, object]:
    """Handle the add_schedule service call."""
    return await _async_handle_add_schedule_service(
        hass,
        call,
        get_device_and_coordinator=_get_device_and_coordinator,
        raise_service_error=_raise_service_error,
        logger=_LOGGER,
        domain=DOMAIN,
        attr_days=_contracts.ATTR_DAYS,
        attr_times=_contracts.ATTR_TIMES,
        attr_events=_contracts.ATTR_EVENTS,
    )


async def async_handle_delete_schedules(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, object]:
    """Handle the delete_schedules service call."""
    return await _async_handle_delete_schedules_service(
        hass,
        call,
        get_device_and_coordinator=_get_device_and_coordinator,
        raise_service_error=_raise_service_error,
        logger=_LOGGER,
        attr_schedule_ids=_contracts.ATTR_SCHEDULE_IDS,
    )


async def async_handle_submit_anonymous_share(
    hass: HomeAssistant, call: ServiceCall
) -> ShareServiceResponse:
    """Handle the submit_anonymous_share service call."""
    return await _async_handle_submit_anonymous_share_service(
        hass,
        call,
        get_anonymous_share_manager=cast(
            ShareAnonymousShareManagerFactory, get_anonymous_share_manager
        ),
        get_client_session=async_get_clientsession,
        raise_service_error=_raise_service_error,
        domain=DOMAIN,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
    )


async def async_handle_get_anonymous_share_report(
    hass: HomeAssistant, call: ServiceCall
) -> ShareServiceResponse:
    """Handle the get_anonymous_share_report service call."""
    return await _async_handle_get_anonymous_share_report_service(
        hass,
        call,
        get_anonymous_share_manager=cast(
            ShareAnonymousShareManagerFactory, get_anonymous_share_manager
        ),
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
    )


async def async_handle_get_developer_report(
    hass: HomeAssistant, call: ServiceCall
) -> DeveloperReportResponse:
    """Handle the get_developer_report service call."""
    return await _async_handle_get_developer_report_service(
        hass,
        call,
        collect_reports=_collect_developer_reports,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
    )


async def async_handle_submit_developer_feedback(
    hass: HomeAssistant, call: ServiceCall
) -> DeveloperFeedbackResponse:
    """Handle the submit_developer_feedback service call."""
    return await _async_handle_submit_developer_feedback_service(
        hass,
        call,
        collect_reports=_collect_developer_reports,
        get_anonymous_share_manager=get_anonymous_share_manager,
        get_client_session=async_get_clientsession,
        domain=DOMAIN,
        service_submit_developer_feedback=_contracts.SERVICE_SUBMIT_DEVELOPER_FEEDBACK,
        attr_note=_contracts.ATTR_NOTE,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
        raise_service_error=_raise_service_error,
    )


async def async_handle_query_command_result(
    hass: HomeAssistant, call: ServiceCall
) -> QueryCommandResultResponse:
    """Developer-only service: query command result status by msgSn."""
    return await _async_handle_query_command_result_service(
        hass,
        call,
        get_device_and_coordinator=_get_developer_device_and_coordinator,
        attr_msg_sn=_contracts.ATTR_MSG_SN,
        attr_max_attempts=_contracts.ATTR_MAX_ATTEMPTS,
        attr_time_budget_seconds=_contracts.ATTR_TIME_BUDGET_SECONDS,
        raise_service_error=_raise_service_error,
    )


async def async_handle_get_city(
    hass: HomeAssistant, call: ServiceCall
) -> CapabilityResponse:
    """Developer-only service: get city information."""
    coordinators = list(_iter_developer_runtime_coordinators(hass))
    return await _async_handle_get_city_service(
        hass,
        call,
        iter_runtime_coordinators=lambda _hass: (
            cast(DiagnosticsCoordinator, coordinator) for coordinator in coordinators
        ),
        raise_optional_error=_raise_optional_capability_error,
        service_get_city=_contracts.SERVICE_GET_CITY,
    )


async def async_handle_query_user_cloud(
    hass: HomeAssistant, call: ServiceCall
) -> CapabilityResponse:
    """Developer-only service: query user cloud information."""
    coordinators = list(_iter_developer_runtime_coordinators(hass))
    return await _async_handle_query_user_cloud_service(
        hass,
        call,
        iter_runtime_coordinators=lambda _hass: (
            cast(DiagnosticsCoordinator, coordinator) for coordinator in coordinators
        ),
        raise_optional_error=_raise_optional_capability_error,
        service_query_user_cloud=_contracts.SERVICE_QUERY_USER_CLOUD,
    )


async def async_handle_fetch_body_sensor_history(
    hass: HomeAssistant, call: ServiceCall
) -> SensorHistoryResponse:
    """Developer-only service: fetch body-sensor history payload."""
    return await _async_handle_fetch_sensor_history_support(
        hass=hass,
        call=call,
        service_handler=_async_handle_fetch_body_sensor_history_service,
        service_name_kw="service_fetch_body_sensor_history",
        service_name=_contracts.SERVICE_FETCH_BODY_SENSOR_HISTORY,
        get_device_and_coordinator=_get_developer_device_and_coordinator,
    )


async def async_handle_fetch_door_sensor_history(
    hass: HomeAssistant, call: ServiceCall
) -> SensorHistoryResponse:
    """Developer-only service: fetch door-sensor history payload."""
    return await _async_handle_fetch_sensor_history_support(
        hass=hass,
        call=call,
        service_handler=_async_handle_fetch_door_sensor_history_service,
        service_name_kw="service_fetch_door_sensor_history",
        service_name=_contracts.SERVICE_FETCH_DOOR_SENSOR_HISTORY,
        get_device_and_coordinator=_get_developer_device_and_coordinator,
    )


async def async_handle_refresh_devices(
    hass: HomeAssistant, call: ServiceCall
) -> RefreshDevicesResult:
    """Handle the refresh_devices service call."""
    return await _async_handle_refresh_devices_service(
        hass,
        call,
        domain=DOMAIN,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
    )


__all__ = [
    "_get_device_and_coordinator",
    "_summarize_service_properties",
    "async_get_clientsession",
    "async_handle_add_schedule",
    "async_handle_delete_schedules",
    "async_handle_fetch_body_sensor_history",
    "async_handle_fetch_door_sensor_history",
    "async_handle_get_anonymous_share_report",
    "async_handle_get_city",
    "async_handle_get_developer_report",
    "async_handle_get_schedules",
    "async_handle_query_command_result",
    "async_handle_query_user_cloud",
    "async_handle_refresh_devices",
    "async_handle_send_command",
    "async_handle_submit_anonymous_share",
    "async_handle_submit_developer_feedback",
    "get_anonymous_share_manager",
]
