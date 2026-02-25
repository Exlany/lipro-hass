"""The Lipro Smart Home integration."""

from __future__ import annotations

from datetime import UTC, datetime
import functools
import logging
import re
from typing import TYPE_CHECKING, Any, Final

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
    MIN_REQUEST_TIMEOUT,
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
    request_timeout = entry.options.get(CONF_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT)
    request_timeout = max(
        MIN_REQUEST_TIMEOUT, min(MAX_REQUEST_TIMEOUT, request_timeout)
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
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

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
    device_id = call.data.get(ATTR_DEVICE_ID)

    # If no device_id provided, try to get it from target entities
    if not device_id:
        entity_ids = call.data.get(ATTR_ENTITY_ID, [])
        if isinstance(entity_ids, str):
            entity_ids = [entity_ids]

        if not entity_ids:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_device_specified",
            )

        # Get device_id from the first entity's device
        ent_reg = er.async_get(hass)
        for entity_id in entity_ids:
            entity_entry = ent_reg.async_get(entity_id)
            if entity_entry and entity_entry.unique_id:
                unique_id = entity_entry.unique_id
                if unique_id.startswith("lipro_") and len(unique_id) > 6:
                    # Extract serial from unique_id: "lipro_{serial}[_{suffix}]"
                    # Serial formats: "03ab" + 12 hex, or "mesh_group_" + digits
                    raw = unique_id[6:]
                    match = _SERIAL_PATTERN.match(raw)
                    if match:
                        device_id = match.group(1)
                        break

        if not device_id:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="cannot_determine_device",
            )

    # Find the device across all config entries
    for entry in hass.config_entries.async_entries(DOMAIN):
        coordinator = entry.runtime_data
        if not coordinator:
            continue

        # Prefer direct serial lookup, then fall back to alias lookup
        # (gateway ID / member device ID mapped by coordinator).
        device = coordinator.get_device(device_id)
        if not device:
            device = coordinator.get_device_by_id(device_id)

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

    if requested_device_id and requested_device_id != device.serial:
        _LOGGER.info(
            "Service call: send_command requested_id=%s resolved_to=%s, "
            "command=%s, property_summary=%s",
            requested_device_id,
            device.serial,
            command,
            properties_summary,
        )
    else:
        _LOGGER.info(
            "Service call: send_command to %s, command=%s, property_summary=%s",
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
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="command_failed",
            )
        result: dict[str, Any] = {"success": True, "serial": device.serial}
        if requested_device_id and requested_device_id != device.serial:
            result["requested_device_id"] = requested_device_id
            result["resolved_device_id"] = device.serial
        return result
    except HomeAssistantError:
        raise
    except LiproApiError as err:
        _LOGGER.warning("API error sending command: %s", err)
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="command_failed",
        ) from err


async def _async_handle_get_schedules(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the get_schedules service call."""
    device, coordinator = await _get_device_and_coordinator(hass, call)
    mesh_gateway_id = device.extra_data.get("gateway_device_id", "")
    raw_mesh_member_ids = device.extra_data.get("group_member_ids", [])
    mesh_member_ids = raw_mesh_member_ids if isinstance(raw_mesh_member_ids, list) else []

    _LOGGER.info("Service call: get_schedules for %s", device.serial)

    try:
        schedules = await coordinator.client.get_device_schedules(
            device.iot_device_id,
            device.device_type_hex,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

        # Format schedules for response
        formatted = []
        for schedule in schedules:
            sched_info = schedule.get("schedule", {})
            times = sched_info.get("time", [])
            events = sched_info.get("evt", [])

            # Convert times to HH:MM format
            time_strs = []
            for t in times:
                hours = t // 3600
                minutes = (t % 3600) // 60
                time_strs.append(f"{hours:02d}:{minutes:02d}")

            formatted.append(
                {
                    "id": schedule.get("id"),
                    "active": schedule.get("active", True),
                    "days": sched_info.get("days", []),
                    "times": time_strs,
                    "events": events,
                }
            )

        return {
            "serial": device.serial,
            "schedules": formatted,
        }
    except LiproApiError as err:
        _LOGGER.warning("API error getting schedules: %s", err)
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="schedule_fetch_failed",
        ) from err


async def _async_handle_add_schedule(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the add_schedule service call."""
    device, coordinator = await _get_device_and_coordinator(hass, call)
    mesh_gateway_id = device.extra_data.get("gateway_device_id", "")
    raw_mesh_member_ids = device.extra_data.get("group_member_ids", [])
    mesh_member_ids = raw_mesh_member_ids if isinstance(raw_mesh_member_ids, list) else []

    days = call.data[ATTR_DAYS]
    times = call.data[ATTR_TIMES]
    events = call.data[ATTR_EVENTS]

    if len(times) != len(events):
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="times_events_mismatch",
        )

    _LOGGER.info(
        "Service call: add_schedule for %s, days=%s, times=%s, events=%s",
        device.serial,
        days,
        times,
        events,
    )

    try:
        schedules = await coordinator.client.add_device_schedule(
            device.iot_device_id,
            device.device_type_hex,
            days,
            times,
            events,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

        return {
            "success": True,
            "serial": device.serial,
            "schedule_count": len(schedules),
        }
    except LiproApiError as err:
        _LOGGER.warning("API error adding schedule: %s", err)
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="schedule_add_failed",
        ) from err


async def _async_handle_delete_schedules(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the delete_schedules service call."""
    device, coordinator = await _get_device_and_coordinator(hass, call)
    mesh_gateway_id = device.extra_data.get("gateway_device_id", "")
    raw_mesh_member_ids = device.extra_data.get("group_member_ids", [])
    mesh_member_ids = raw_mesh_member_ids if isinstance(raw_mesh_member_ids, list) else []

    schedule_ids = call.data[ATTR_SCHEDULE_IDS]

    _LOGGER.info(
        "Service call: delete_schedules for %s, ids=%s",
        device.serial,
        schedule_ids,
    )

    try:
        remaining = await coordinator.client.delete_device_schedules(
            device.iot_device_id,
            device.device_type_hex,
            schedule_ids,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

        return {
            "success": True,
            "serial": device.serial,
            "remaining_count": len(remaining),
        }
    except LiproApiError as err:
        _LOGGER.warning("API error deleting schedules: %s", err)
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="schedule_delete_failed",
        ) from err


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
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="anonymous_share_submit_failed",
        )

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
    for entry in hass.config_entries.async_entries(DOMAIN):
        coordinator = entry.runtime_data
        if coordinator is None or not hasattr(coordinator, "build_developer_report"):
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
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="developer_feedback_submit_failed",
        )

    return {
        "success": True,
        "submitted_entries": len(reports),
    }


async def _async_setup_services(hass: HomeAssistant) -> None:
    """Set up Lipro services."""
    if hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND):
        return  # Services already registered

    # Register services with functools.partial to avoid lambda closures
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_COMMAND,
        functools.partial(_async_handle_send_command, hass),
        schema=SERVICE_SEND_COMMAND_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_SCHEDULES,
        functools.partial(_async_handle_get_schedules, hass),
        schema=SERVICE_GET_SCHEDULES_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_SCHEDULE,
        functools.partial(_async_handle_add_schedule, hass),
        schema=SERVICE_ADD_SCHEDULE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_SCHEDULES,
        functools.partial(_async_handle_delete_schedules, hass),
        schema=SERVICE_DELETE_SCHEDULES_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    # Anonymous share services (no schema needed)
    hass.services.async_register(
        DOMAIN,
        SERVICE_SUBMIT_ANONYMOUS_SHARE,
        functools.partial(_async_handle_submit_anonymous_share, hass),
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_ANONYMOUS_SHARE_REPORT,
        functools.partial(_async_handle_get_anonymous_share_report, hass),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_DEVELOPER_REPORT,
        functools.partial(_async_handle_get_developer_report, hass),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SUBMIT_DEVELOPER_FEEDBACK,
        functools.partial(_async_handle_submit_developer_feedback, hass),
        schema=SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )


async def async_unload_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> bool:
    """Unload a config entry."""
    # Note: HA automatically calls coordinator.async_shutdown() during unload
    result = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Unregister services when the last config entry is being unloaded
    if result and not any(
        e
        for e in hass.config_entries.async_entries(DOMAIN)
        if e.entry_id != entry.entry_id
    ):
        for service_name in (
            SERVICE_SEND_COMMAND,
            SERVICE_GET_SCHEDULES,
            SERVICE_ADD_SCHEDULE,
            SERVICE_DELETE_SCHEDULES,
            SERVICE_SUBMIT_ANONYMOUS_SHARE,
            SERVICE_GET_ANONYMOUS_SHARE_REPORT,
            SERVICE_GET_DEVELOPER_REPORT,
            SERVICE_SUBMIT_DEVELOPER_FEEDBACK,
        ):
            hass.services.async_remove(DOMAIN, service_name)

    return result


async def async_reload_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
