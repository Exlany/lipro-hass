"""Formal control-plane router for HA service callbacks."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterator, Mapping
import logging
import re
from typing import Any, Final, NoReturn

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from ..const.base import DOMAIN, IOT_DEVICE_ID_PREFIX
from ..const.config import CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE
from ..core import LiproApiError, LiproDevice, get_anonymous_share_manager
from ..core.utils.redaction import redact_identifier as _redact_identifier
from ..runtime_types import LiproCoordinator
from ..services import contracts as _contracts
from ..services.command import (
    async_handle_send_command as _async_handle_send_command_service,
)
from ..services.device_lookup import (
    get_device_and_coordinator as _get_device_and_coordinator_service,
    iter_runtime_coordinators as _iter_runtime_coordinators_service,
)
from ..services.diagnostics import (
    async_call_optional_capability as _async_call_optional_capability_service,
    async_handle_fetch_body_sensor_history as _async_handle_fetch_body_sensor_history_service,
    async_handle_fetch_door_sensor_history as _async_handle_fetch_door_sensor_history_service,
    async_handle_get_city as _async_handle_get_city_service,
    async_handle_get_developer_report as _async_handle_get_developer_report_service,
    async_handle_query_command_result as _async_handle_query_command_result_service,
    async_handle_query_user_cloud as _async_handle_query_user_cloud_service,
    async_handle_submit_developer_feedback as _async_handle_submit_developer_feedback_service,
    build_sensor_history_result as _build_sensor_history_result_service,
    collect_developer_reports as _collect_developer_reports_service,
    raise_optional_capability_error as _raise_optional_capability_error_service,
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
    async_handle_get_anonymous_share_report as _async_handle_get_anonymous_share_report_service,
    async_handle_submit_anonymous_share as _async_handle_submit_anonymous_share_service,
)

_LOGGER = logging.getLogger(__name__)
_SERIAL_PATTERN: Final = re.compile(
    rf"({re.escape(IOT_DEVICE_ID_PREFIX)}[0-9A-Fa-f]{{12}}|mesh_group_\d+)(?:_|$)"
)


def _summarize_service_properties(properties: Any) -> dict[str, Any]:
    """Build a log-safe summary for service properties."""
    if not isinstance(properties, list):
        return {"count": 0, "keys": []}

    keys = [
        item.get("key")
        for item in properties
        if isinstance(item, dict) and isinstance(item.get("key"), str)
    ]
    return {"count": len(properties), "keys": keys}


def _iter_runtime_coordinators(
    hass: HomeAssistant,
) -> Iterator[LiproCoordinator]:
    """Iterate all active coordinators for the Lipro domain."""
    yield from _iter_runtime_coordinators_service(hass, domain=DOMAIN)


def _build_single_runtime_coordinator_iterator(
    coordinator: object,
) -> Callable[[HomeAssistant], Iterator[object]]:
    """Build a stable iterator factory for one runtime coordinator."""

    def _iter_single_runtime_coordinator(_hass: HomeAssistant) -> Iterator[object]:
        return iter((coordinator,))

    return _iter_single_runtime_coordinator


def _is_debug_mode_enabled_for_entry(entry: Any) -> bool:
    """Return True when one config entry explicitly opts into debug services."""
    options = getattr(entry, "options", None)
    if not isinstance(options, Mapping):
        return DEFAULT_DEBUG_MODE
    return bool(options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE))


def _raise_developer_mode_not_enabled(*, entry_id: str | None = None) -> NoReturn:
    """Raise a consistent validation error for disabled developer services."""
    del entry_id
    raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="developer_mode_not_enabled",
    )


def _find_runtime_entry_for_coordinator(
    hass: HomeAssistant,
    coordinator: LiproCoordinator,
) -> Any | None:
    """Return the config entry that owns one active coordinator."""
    config_entry = getattr(coordinator, "config_entry", None)
    if getattr(config_entry, "runtime_data", None) is coordinator:
        return config_entry
    for entry in hass.config_entries.async_entries(DOMAIN):
        if getattr(entry, "runtime_data", None) is coordinator:
            return entry
    return None


def _is_developer_coordinator(
    hass: HomeAssistant,
    coordinator: LiproCoordinator,
) -> bool:
    """Return whether the coordinator belongs to a debug-enabled entry."""
    entry = _find_runtime_entry_for_coordinator(hass, coordinator)
    return entry is not None and _is_debug_mode_enabled_for_entry(entry)


def _iter_developer_runtime_coordinators(
    hass: HomeAssistant,
) -> Iterator[LiproCoordinator]:
    """Iterate runtime coordinators that explicitly opted into debug mode."""
    for coordinator in _iter_runtime_coordinators(hass):
        if _is_developer_coordinator(hass, coordinator):
            yield coordinator


async def _get_developer_device_and_coordinator(
    hass: HomeAssistant,
    call: ServiceCall,
) -> tuple[LiproDevice, LiproCoordinator]:
    """Resolve one device/coordinator pair and require debug-mode opt-in."""
    device, coordinator = await _get_device_and_coordinator(hass, call)
    if not _is_developer_coordinator(hass, coordinator):
        entry = _find_runtime_entry_for_coordinator(hass, coordinator)
        _raise_developer_mode_not_enabled(entry_id=getattr(entry, "entry_id", None))
    return device, coordinator


def _log_send_command_call(
    requested_device_id: str | None,
    resolved_serial: str,
    command: str,
    properties_summary: dict[str, Any],
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
) -> dict[str, Any]:
    """Handle the send_command service call."""
    return await _async_handle_send_command_service(
        hass,
        call,
        get_device_and_coordinator=_get_device_and_coordinator,
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
) -> dict[str, Any]:
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
) -> dict[str, Any]:
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
) -> dict[str, Any]:
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
) -> dict[str, Any]:
    """Handle the submit_anonymous_share service call."""
    return await _async_handle_submit_anonymous_share_service(
        hass,
        call,
        get_anonymous_share_manager=get_anonymous_share_manager,
        get_client_session=async_get_clientsession,
        raise_service_error=_raise_service_error,
        domain=DOMAIN,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
    )


async def async_handle_get_anonymous_share_report(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the get_anonymous_share_report service call."""
    return await _async_handle_get_anonymous_share_report_service(
        hass,
        call,
        get_anonymous_share_manager=get_anonymous_share_manager,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
    )


def _collect_developer_reports(
    hass: HomeAssistant,
    *,
    requested_entry_id: str | None = None,
) -> list[dict[str, Any]]:
    """Collect developer reports from debug-enabled runtime entries only."""
    if requested_entry_id is not None:
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.entry_id != requested_entry_id:
                continue
            coordinator = getattr(entry, "runtime_data", None)
            if coordinator is None:
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="entry_not_found",
                    translation_placeholders={"entry_id": requested_entry_id},
                )
            if not _is_debug_mode_enabled_for_entry(entry):
                _raise_developer_mode_not_enabled(entry_id=requested_entry_id)
            return _collect_developer_reports_service(
                hass,
                iter_runtime_coordinators=_build_single_runtime_coordinator_iterator(
                    coordinator
                ),
            )

        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="entry_not_found",
            translation_placeholders={"entry_id": requested_entry_id},
        )

    coordinators = list(_iter_developer_runtime_coordinators(hass))
    return _collect_developer_reports_service(
        hass,
        iter_runtime_coordinators=lambda _hass: iter(coordinators),
    )


async def async_handle_get_developer_report(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the get_developer_report service call."""
    return await _async_handle_get_developer_report_service(
        hass,
        call,
        collect_reports=_collect_developer_reports,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
    )


async def async_handle_submit_developer_feedback(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
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


def _raise_optional_capability_error(capability: str, err: LiproApiError) -> NoReturn:
    """Raise a concise service-layer error for optional diagnostic capabilities."""
    _raise_optional_capability_error_service(capability, err, logger=_LOGGER)


async def _async_call_optional_capability(
    capability: str,
    method: Callable[..., Awaitable[Any]],
    **kwargs: Any,
) -> Any:
    """Call optional capability API and map auth/API failures to service errors."""
    return await _async_call_optional_capability_service(
        capability,
        method,
        raise_optional_error=_raise_optional_capability_error,
        raise_service_error=_raise_service_error,
        **kwargs,
    )


async def async_handle_query_command_result(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
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
) -> dict[str, Any]:
    """Developer-only service: get city information."""
    coordinators = list(_iter_developer_runtime_coordinators(hass))
    return await _async_handle_get_city_service(
        hass,
        call,
        iter_runtime_coordinators=lambda _hass: iter(coordinators),
        raise_optional_error=_raise_optional_capability_error,
        service_get_city=_contracts.SERVICE_GET_CITY,
    )


async def async_handle_query_user_cloud(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Developer-only service: query user cloud information."""
    coordinators = list(_iter_developer_runtime_coordinators(hass))
    return await _async_handle_query_user_cloud_service(
        hass,
        call,
        iter_runtime_coordinators=lambda _hass: iter(coordinators),
        raise_optional_error=_raise_optional_capability_error,
        service_query_user_cloud=_contracts.SERVICE_QUERY_USER_CLOUD,
    )


async def _async_handle_fetch_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    service_handler: Callable[..., Awaitable[dict[str, Any]]],
    service_name_kw: str,
    service_name: str,
) -> dict[str, Any]:
    """Shared wrapper for body/door sensor-history services."""
    return await service_handler(
        hass,
        call,
        get_device_and_coordinator=_get_developer_device_and_coordinator,
        async_call_optional_capability=_async_call_optional_capability,
        build_sensor_history_result=_build_sensor_history_result_service,
        attr_sensor_device_id=_contracts.ATTR_SENSOR_DEVICE_ID,
        attr_mesh_type=_contracts.ATTR_MESH_TYPE,
        **{service_name_kw: service_name},
    )


async def async_handle_fetch_body_sensor_history(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Developer-only service: fetch body-sensor history payload."""
    return await _async_handle_fetch_sensor_history(
        hass=hass,
        call=call,
        service_handler=_async_handle_fetch_body_sensor_history_service,
        service_name_kw="service_fetch_body_sensor_history",
        service_name=_contracts.SERVICE_FETCH_BODY_SENSOR_HISTORY,
    )


async def async_handle_fetch_door_sensor_history(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Developer-only service: fetch door-sensor history payload."""
    return await _async_handle_fetch_sensor_history(
        hass=hass,
        call=call,
        service_handler=_async_handle_fetch_door_sensor_history_service,
        service_name_kw="service_fetch_door_sensor_history",
        service_name=_contracts.SERVICE_FETCH_DOOR_SENSOR_HISTORY,
    )


async def async_handle_refresh_devices(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
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
