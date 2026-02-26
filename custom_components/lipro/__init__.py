"""The Lipro Smart Home integration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterator
from datetime import UTC, datetime
import functools
import logging
import re
from typing import TYPE_CHECKING, Any, Final, NoReturn

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    HomeAssistantError,
    ServiceValidationError,
)
from homeassistant.helpers import config_validation as cv, entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_ACCESS_TOKEN,
    CONF_EXPIRES_AT,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REFRESH_TOKEN,
    CONF_REQUEST_TIMEOUT,
    CONF_SCAN_INTERVAL,
    CONF_USER_ID,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    IOT_DEVICE_ID_PREFIX,
    MAX_REQUEST_TIMEOUT,
    MAX_SCAN_INTERVAL,
    MIN_REQUEST_TIMEOUT,
    MIN_SCAN_INTERVAL,
)
from .core import (
    LiproApiError,
    LiproAuthError,
    LiproAuthManager,
    LiproClient,
    LiproConnectionError,
    LiproDataUpdateCoordinator,
    LiproDevice,
    get_anonymous_share_manager,
)

if TYPE_CHECKING:
    from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

# Supported platforms (using Platform enum per HA best practices)
PLATFORMS: list[Platform] = [
    Platform.LIGHT,
    Platform.COVER,
    Platform.SWITCH,
    Platform.FAN,
    Platform.CLIMATE,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SELECT,
]

type LiproConfigEntry = ConfigEntry[LiproDataUpdateCoordinator]

# Service constants
SERVICE_SEND_COMMAND: Final = "send_command"
SERVICE_GET_SCHEDULES: Final = "get_schedules"
SERVICE_ADD_SCHEDULE: Final = "add_schedule"
SERVICE_DELETE_SCHEDULES: Final = "delete_schedules"
SERVICE_SUBMIT_ANONYMOUS_SHARE: Final = "submit_anonymous_share"
SERVICE_GET_ANONYMOUS_SHARE_REPORT: Final = "get_anonymous_share_report"
SERVICE_GET_DEVELOPER_REPORT: Final = "get_developer_report"
SERVICE_SUBMIT_DEVELOPER_FEEDBACK: Final = "submit_developer_feedback"

ATTR_DEVICE_ID: Final = "device_id"
ATTR_COMMAND: Final = "command"
ATTR_PROPERTIES: Final = "properties"
ATTR_DAYS: Final = "days"
ATTR_TIMES: Final = "times"
ATTR_EVENTS: Final = "events"
ATTR_SCHEDULE_IDS: Final = "schedule_ids"
ATTR_NOTE: Final = "note"

# Pre-compiled pattern for extracting device serial from entity unique_id
_SERIAL_PATTERN = re.compile(
    rf"({re.escape(IOT_DEVICE_ID_PREFIX)}[0-9A-Fa-f]{{12}}|mesh_group_\d+)"
)

# Service schema - device_id is optional when entity target is used
SERVICE_SEND_COMMAND_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_COMMAND): cv.string,
        vol.Optional(ATTR_PROPERTIES): vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Required("key"): cv.string,
                        vol.Required("value"): cv.string,
                    },
                ),
            ],
        ),
    },
)

# Schema for get_schedules service
SERVICE_GET_SCHEDULES_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): cv.string,
    },
)

# Schema for add_schedule service
SERVICE_ADD_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_DAYS): vol.All(
            cv.ensure_list,
            [vol.All(vol.Coerce(int), vol.Range(min=1, max=7))],
        ),
        vol.Required(ATTR_TIMES): vol.All(
            cv.ensure_list,
            [vol.All(vol.Coerce(int), vol.Range(min=0, max=86399))],
        ),
        vol.Required(ATTR_EVENTS): vol.All(
            cv.ensure_list,
            [vol.Coerce(int)],
        ),
    },
)

# Schema for delete_schedules service
SERVICE_DELETE_SCHEDULES_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_SCHEDULE_IDS): vol.All(
            cv.ensure_list,
            [vol.Coerce(int)],
        ),
    },
)

SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_NOTE): cv.string,
    },
)


def _summarize_service_properties(properties: Any) -> dict[str, Any]:
    """Build a log-safe summary for service properties.

    Avoid logging raw values to reduce accidental sensitive-data exposure.
    """
    if not isinstance(properties, list):
        return {"count": 0, "keys": []}

    keys = [
        item.get("key")
        for item in properties
        if isinstance(item, dict) and isinstance(item.get("key"), str)
    ]
    return {"count": len(properties), "keys": keys}


def _coerce_int_option(
    value: Any,
    *,
    default: int,
    option_name: str,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Coerce persisted option values to int with safe fallback/clamp."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        _LOGGER.warning(
            "Invalid option %s=%r, using default %d",
            option_name,
            value,
            default,
        )
        parsed = default

    if min_value is not None:
        parsed = max(min_value, parsed)
    if max_value is not None:
        parsed = min(max_value, parsed)
    return parsed


def _get_entry_int_option(
    entry: LiproConfigEntry,
    *,
    option_name: str,
    default: int,
    min_value: int,
    max_value: int,
) -> int:
    """Read and coerce an integer option from a config entry."""
    return _coerce_int_option(
        entry.options.get(option_name, default),
        default=default,
        option_name=option_name,
        min_value=min_value,
        max_value=max_value,
    )


def _coerce_int_list(value: Any) -> list[int]:
    """Coerce mixed list payloads into integers, skipping invalid items."""
    if not isinstance(value, list):
        return []

    result: list[int] = []
    for item in value:
        if isinstance(item, bool):
            continue
        try:
            result.append(int(item))
        except (TypeError, ValueError):
            continue
    return result


def _get_mesh_context(device: LiproDevice) -> tuple[str, list[Any]]:
    """Extract mesh gateway and member IDs from device metadata."""
    mesh_gateway_id = device.extra_data.get("gateway_device_id", "")
    raw_mesh_member_ids = device.extra_data.get("group_member_ids", [])
    mesh_member_ids = (
        raw_mesh_member_ids if isinstance(raw_mesh_member_ids, list) else []
    )
    return mesh_gateway_id, mesh_member_ids


def _raise_service_error(
    translation_key: str,
    *,
    err: Exception | None = None,
) -> NoReturn:
    """Raise a translated HomeAssistantError, preserving the original cause."""
    if err is None:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key=translation_key,
        )

    raise HomeAssistantError(
        translation_domain=DOMAIN,
        translation_key=translation_key,
    ) from err


async def _async_call_schedule_client(
    device: LiproDevice,
    client_call: Callable[..., Awaitable[Any]],
    *args: Any,
    error_log: str,
    error_translation_key: str,
) -> Any:
    """Call a schedule client API with mesh context and consistent error mapping."""
    mesh_gateway_id, mesh_member_ids = _get_mesh_context(device)

    try:
        return await client_call(
            device.iot_device_id,
            device.device_type_hex,
            *args,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )
    except LiproApiError as err:
        _LOGGER.warning(error_log, err)
        _raise_service_error(error_translation_key, err=err)


async def _async_call_schedule_service(
    device: LiproDevice,
    *,
    client_call: Callable[..., Awaitable[Any]],
    call_args: tuple[Any, ...] = (),
    service_log: str | None = None,
    service_log_args: tuple[Any, ...] = (),
    error_log: str,
    error_translation_key: str,
) -> Any:
    """Invoke a schedule client method with consistent logging and error mapping."""
    if service_log is not None:
        _LOGGER.info(service_log, device.serial, *service_log_args)

    return await _async_call_schedule_client(
        device,
        client_call,
        *call_args,
        error_log=error_log,
        error_translation_key=error_translation_key,
    )


def _format_schedule_time(seconds: int) -> str | None:
    """Convert seconds since midnight to HH:MM, ignoring invalid values."""
    if seconds < 0 or seconds >= 86400:
        return None

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


def _normalize_schedule_row(schedule: Any) -> dict[str, Any] | None:
    """Normalize a raw schedule row into service response format."""
    if not isinstance(schedule, dict):
        return None

    sched_info = schedule.get("schedule")
    if not isinstance(sched_info, dict):
        sched_info = {}

    times = _coerce_int_list(sched_info.get("time"))
    events = _coerce_int_list(sched_info.get("evt"))
    days = _coerce_int_list(sched_info.get("days"))

    time_strs: list[str] = []
    for value in times:
        time_str = _format_schedule_time(value)
        if time_str is not None:
            time_strs.append(time_str)

    return {
        "id": schedule.get("id"),
        "active": schedule.get("active", True),
        "days": days,
        "times": time_strs,
        "events": events,
    }


def _extract_device_id_from_entity_ids(
    hass: HomeAssistant, entity_ids: Any
) -> str | None:
    """Resolve the first Lipro device ID from entity targets."""
    ent_reg = er.async_get(hass)
    for entity_id in entity_ids:
        entity_entry = ent_reg.async_get(entity_id)
        if not entity_entry or not entity_entry.unique_id:
            continue

        unique_id = entity_entry.unique_id
        if not unique_id.startswith("lipro_") or len(unique_id) <= 6:
            continue

        # Extract serial from unique_id: "lipro_{serial}[_{suffix}]"
        # Serial formats: "03ab" + 12 hex, or "mesh_group_" + digits
        match = _SERIAL_PATTERN.match(unique_id[6:])
        if match:
            return match.group(1)

    return None


def _resolve_device_id_from_service_call(
    hass: HomeAssistant,
    call: ServiceCall,
) -> Any:
    """Resolve device identifier from service data or targeted entities."""
    device_id = call.data.get(ATTR_DEVICE_ID)
    if device_id:
        return device_id

    entity_ids = call.data.get(ATTR_ENTITY_ID, [])
    if isinstance(entity_ids, str):
        entity_ids = [entity_ids]

    if not entity_ids:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="no_device_specified",
        )

    resolved_device_id = _extract_device_id_from_entity_ids(hass, entity_ids)
    if not resolved_device_id:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="cannot_determine_device",
        )

    return resolved_device_id


def _find_device_in_coordinator(
    coordinator: LiproDataUpdateCoordinator,
    device_id: Any,
) -> LiproDevice | None:
    """Find device by serial first, then by alias mapping."""
    device = coordinator.get_device(device_id)
    if device is None:
        return coordinator.get_device_by_id(device_id)
    return device


def _iter_runtime_coordinators(
    hass: HomeAssistant,
) -> Iterator[LiproDataUpdateCoordinator]:
    """Iterate all active coordinators for the Lipro domain."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        coordinator = entry.runtime_data
        if coordinator is None:
            continue
        yield coordinator


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
            requested_device_id,
            resolved_serial,
            command,
            properties_summary,
        )
    else:
        _LOGGER.info(
            "Service call: send_command to %s, command=%s, property_summary=%s",
            resolved_serial,
            command,
            properties_summary,
        )

    return is_alias_resolution


def _build_send_command_result(
    resolved_serial: str,
    *,
    requested_device_id: str | None,
    is_alias_resolution: bool,
) -> dict[str, Any]:
    """Build send_command service response payload."""
    result: dict[str, Any] = {"success": True, "serial": resolved_serial}
    if is_alias_resolution:
        result["requested_device_id"] = requested_device_id
        result["resolved_device_id"] = resolved_serial
    return result


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Lipro component."""
    await _async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> bool:
    """Set up Lipro from a config entry."""
    phone_id = entry.data[CONF_PHONE_ID]
    phone = entry.data[CONF_PHONE]
    password_hash = entry.data[CONF_PASSWORD_HASH]

    # Get request timeout from options (clamp to valid range)
    request_timeout = _get_entry_int_option(
        entry,
        option_name=CONF_REQUEST_TIMEOUT,
        default=DEFAULT_REQUEST_TIMEOUT,
        min_value=MIN_REQUEST_TIMEOUT,
        max_value=MAX_REQUEST_TIMEOUT,
    )

    session = async_get_clientsession(hass)
    client = LiproClient(phone_id, session, request_timeout=request_timeout)
    auth_manager = LiproAuthManager(client)

    # Set stored tokens if available
    if CONF_ACCESS_TOKEN in entry.data and CONF_REFRESH_TOKEN in entry.data:
        auth_manager.set_tokens(
            entry.data[CONF_ACCESS_TOKEN],
            entry.data[CONF_REFRESH_TOKEN],
            entry.data.get(CONF_USER_ID),
            entry.data.get(CONF_EXPIRES_AT),
        )

    # Store credentials for re-auth (using hash)
    auth_manager.set_credentials(phone, password_hash, password_is_hashed=True)

    # Try to authenticate
    try:
        await auth_manager.ensure_valid_token()
    except LiproAuthError as err:
        msg = f"Authentication failed: {err}"
        raise ConfigEntryAuthFailed(msg) from err
    except LiproConnectionError as err:
        msg = f"Connection failed: {err}"
        raise ConfigEntryNotReady(msg) from err

    # Get scan interval from options (or use default)
    scan_interval = _get_entry_int_option(
        entry,
        option_name=CONF_SCAN_INTERVAL,
        default=DEFAULT_SCAN_INTERVAL,
        min_value=MIN_SCAN_INTERVAL,
        max_value=MAX_SCAN_INTERVAL,
    )

    # Create coordinator with configurable scan interval
    coordinator = LiproDataUpdateCoordinator(
        hass,
        client,
        auth_manager,
        entry,
        update_interval=scan_interval,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator in runtime data
    entry.runtime_data = coordinator

    # Update stored tokens if they changed
    auth_data = auth_manager.get_auth_data()
    if auth_data[CONF_ACCESS_TOKEN] != entry.data.get(CONF_ACCESS_TOKEN) or auth_data[
        CONF_REFRESH_TOKEN
    ] != entry.data.get(CONF_REFRESH_TOKEN):
        hass.config_entries.async_update_entry(
            entry,
            data={
                **entry.data,
                CONF_ACCESS_TOKEN: auth_data[CONF_ACCESS_TOKEN],
                CONF_REFRESH_TOKEN: auth_data[CONF_REFRESH_TOKEN],
                CONF_EXPIRES_AT: auth_data[CONF_EXPIRES_AT],
            },
        )

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def _get_device_and_coordinator(
    hass: HomeAssistant,
    call: ServiceCall,
) -> tuple[LiproDevice, LiproDataUpdateCoordinator]:
    """Get device and coordinator from service call.

    Helper function to extract device from service call data or entity target.
    """
    device_id = _resolve_device_id_from_service_call(hass, call)

    # Find the device across all active coordinators.
    for coordinator in _iter_runtime_coordinators(hass):
        device = _find_device_in_coordinator(coordinator, device_id)
        if device:
            return device, coordinator

    raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="device_not_found",
        translation_placeholders={"device_id": device_id},
    )


async def _async_handle_send_command(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the send_command service call."""
    command = call.data[ATTR_COMMAND]
    properties = call.data.get(ATTR_PROPERTIES)
    properties_summary = _summarize_service_properties(properties)
    requested_device_id = call.data.get(ATTR_DEVICE_ID)

    device, coordinator = await _get_device_and_coordinator(hass, call)
    is_alias_resolution = _log_send_command_call(
        requested_device_id,
        device.serial,
        command,
        properties_summary,
    )

    try:
        success = await coordinator.async_send_command(
            device,
            command,
            properties,
            fallback_device_id=requested_device_id,
        )
        if not success:
            _raise_service_error("command_failed")
        return _build_send_command_result(
            device.serial,
            requested_device_id=requested_device_id,
            is_alias_resolution=is_alias_resolution,
        )
    except HomeAssistantError:
        raise
    except LiproApiError as err:
        _LOGGER.warning("API error sending command: %s", err)
        _raise_service_error("command_failed", err=err)


async def _async_handle_get_schedules(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the get_schedules service call."""
    device, coordinator = await _get_device_and_coordinator(hass, call)

    schedules = await _async_call_schedule_service(
        device,
        client_call=coordinator.client.get_device_schedules,
        service_log="Service call: get_schedules for %s",
        error_log="API error getting schedules: %s",
        error_translation_key="schedule_fetch_failed",
    )

    # Format schedules for response
    formatted = [
        normalized
        for schedule in schedules
        if (normalized := _normalize_schedule_row(schedule)) is not None
    ]

    return {
        "serial": device.serial,
        "schedules": formatted,
    }


async def _async_handle_add_schedule(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the add_schedule service call."""
    device, coordinator = await _get_device_and_coordinator(hass, call)

    days = call.data[ATTR_DAYS]
    times = call.data[ATTR_TIMES]
    events = call.data[ATTR_EVENTS]

    if len(times) != len(events):
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="times_events_mismatch",
        )

    schedules = await _async_call_schedule_service(
        device,
        client_call=coordinator.client.add_device_schedule,
        call_args=(days, times, events),
        service_log="Service call: add_schedule for %s, days=%s, times=%s, events=%s",
        service_log_args=(days, times, events),
        error_log="API error adding schedule: %s",
        error_translation_key="schedule_add_failed",
    )

    return {
        "success": True,
        "serial": device.serial,
        "schedule_count": len(schedules),
    }


async def _async_handle_delete_schedules(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the delete_schedules service call."""
    device, coordinator = await _get_device_and_coordinator(hass, call)

    schedule_ids = call.data[ATTR_SCHEDULE_IDS]

    remaining = await _async_call_schedule_service(
        device,
        client_call=coordinator.client.delete_device_schedules,
        call_args=(schedule_ids,),
        service_log="Service call: delete_schedules for %s, ids=%s",
        service_log_args=(schedule_ids,),
        error_log="API error deleting schedules: %s",
        error_translation_key="schedule_delete_failed",
    )

    return {
        "success": True,
        "serial": device.serial,
        "remaining_count": len(remaining),
    }


async def _async_handle_submit_anonymous_share(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the submit_anonymous_share service call."""
    share_manager = get_anonymous_share_manager(hass)

    if not share_manager.is_enabled:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="anonymous_share_not_enabled",
        )

    device_count, error_count = share_manager.pending_count
    if device_count == 0 and error_count == 0:
        return {
            "success": True,
            "message": "No data to submit",
            "devices": 0,
            "errors": 0,
        }

    session = async_get_clientsession(hass)
    success = await share_manager.submit_report(session, force=True)

    if not success:
        _raise_service_error("anonymous_share_submit_failed")

    return {
        "success": True,
        "devices": device_count,
        "errors": error_count,
    }


async def _async_handle_get_anonymous_share_report(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the get_anonymous_share_report service call."""
    share_manager = get_anonymous_share_manager(hass)
    report = share_manager.get_pending_report()

    if report is None:
        return {
            "has_data": False,
            "devices": [],
            "errors": [],
        }

    return {
        "has_data": True,
        "device_count": report.get("device_count", 0),
        "error_count": report.get("error_count", 0),
        "devices": report.get("devices", []),
        "errors": report.get("errors", []),
    }


def _collect_developer_reports(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Collect developer reports from active config entries."""
    reports: list[dict[str, Any]] = []
    for coordinator in _iter_runtime_coordinators(hass):
        if not hasattr(coordinator, "build_developer_report"):
            continue
        reports.append(coordinator.build_developer_report())
    return reports


async def _async_handle_get_developer_report(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the get_developer_report service call."""
    reports = _collect_developer_reports(hass)

    return {
        "entry_count": len(reports),
        "reports": reports,
    }


async def _async_handle_submit_developer_feedback(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the submit_developer_feedback service call."""
    reports = _collect_developer_reports(hass)

    if not reports:
        return {
            "success": False,
            "message": "No active Lipro config entries",
            "submitted_entries": 0,
        }

    feedback_payload = {
        "source": "home_assistant_service",
        "service": f"{DOMAIN}.{SERVICE_SUBMIT_DEVELOPER_FEEDBACK}",
        "generated_at": datetime.now(UTC).isoformat(),
        "entry_count": len(reports),
        "note": call.data.get(ATTR_NOTE, ""),
        "reports": reports,
    }

    share_manager = get_anonymous_share_manager(hass)
    session = async_get_clientsession(hass)
    success = await share_manager.submit_developer_feedback(
        session,
        feedback_payload,
    )
    if not success:
        _raise_service_error("developer_feedback_submit_failed")

    return {
        "success": True,
        "submitted_entries": len(reports),
    }


_SERVICE_REGISTRATIONS: Final = (
    (
        SERVICE_SEND_COMMAND,
        _async_handle_send_command,
        SERVICE_SEND_COMMAND_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    (
        SERVICE_GET_SCHEDULES,
        _async_handle_get_schedules,
        SERVICE_GET_SCHEDULES_SCHEMA,
        SupportsResponse.ONLY,
    ),
    (
        SERVICE_ADD_SCHEDULE,
        _async_handle_add_schedule,
        SERVICE_ADD_SCHEDULE_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    (
        SERVICE_DELETE_SCHEDULES,
        _async_handle_delete_schedules,
        SERVICE_DELETE_SCHEDULES_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    (
        SERVICE_SUBMIT_ANONYMOUS_SHARE,
        _async_handle_submit_anonymous_share,
        None,
        SupportsResponse.OPTIONAL,
    ),
    (
        SERVICE_GET_ANONYMOUS_SHARE_REPORT,
        _async_handle_get_anonymous_share_report,
        None,
        SupportsResponse.ONLY,
    ),
    (
        SERVICE_GET_DEVELOPER_REPORT,
        _async_handle_get_developer_report,
        None,
        SupportsResponse.ONLY,
    ),
    (
        SERVICE_SUBMIT_DEVELOPER_FEEDBACK,
        _async_handle_submit_developer_feedback,
        SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
)


async def _async_setup_services(hass: HomeAssistant) -> None:
    """Set up Lipro services."""
    if hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND):
        return  # Services already registered

    # Register services with functools.partial to avoid lambda closures.
    for (
        service_name,
        service_handler,
        service_schema,
        supports_response,
    ) in _SERVICE_REGISTRATIONS:
        register_kwargs: dict[str, Any] = {"supports_response": supports_response}
        if service_schema is not None:
            register_kwargs["schema"] = service_schema
        hass.services.async_register(
            DOMAIN,
            service_name,
            functools.partial(service_handler, hass),
            **register_kwargs,
        )


async def async_unload_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> bool:
    """Unload a config entry."""
    result = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Ensure coordinator resources are released on unload.
    if result:
        coordinator = getattr(entry, "runtime_data", None)
        if coordinator is not None:
            await coordinator.async_shutdown()

    # Unregister services when the last config entry is being unloaded
    if result and not any(
        e
        for e in hass.config_entries.async_entries(DOMAIN)
        if e.entry_id != entry.entry_id
    ):
        for service_name, *_ in _SERVICE_REGISTRATIONS:
            hass.services.async_remove(DOMAIN, service_name)

    return result


async def async_reload_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
