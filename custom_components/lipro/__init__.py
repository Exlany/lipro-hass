"""The Lipro Smart Home integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

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

from .config_flow import CONF_PASSWORD_HASH
from .const import (
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REQUEST_TIMEOUT,
    CONF_SCAN_INTERVAL,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .core import (
    LiproApiError,
    LiproAuthError,
    LiproAuthManager,
    LiproClient,
    LiproConnectionError,
    LiproDataUpdateCoordinator,
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
SERVICE_SEND_COMMAND = "send_command"
SERVICE_GET_SCHEDULES = "get_schedules"
SERVICE_ADD_SCHEDULE = "add_schedule"
SERVICE_DELETE_SCHEDULES = "delete_schedules"
SERVICE_SUBMIT_ANONYMOUS_SHARE = "submit_anonymous_share"
SERVICE_GET_ANONYMOUS_SHARE_REPORT = "get_anonymous_share_report"

ATTR_DEVICE_ID = "device_id"
ATTR_COMMAND = "command"
ATTR_PROPERTIES = "properties"
ATTR_DAYS = "days"
ATTR_TIMES = "times"
ATTR_EVENTS = "events"
ATTR_SCHEDULE_IDS = "schedule_ids"

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


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Lipro component."""
    await _async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> bool:
    """Set up Lipro from a config entry."""
    phone_id = entry.data[CONF_PHONE_ID]
    phone = entry.data[CONF_PHONE]
    password_hash = entry.data[CONF_PASSWORD_HASH]

    # Get request timeout from options
    request_timeout = entry.options.get(CONF_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT)

    session = async_get_clientsession(hass)
    client = LiproClient(phone_id, session, request_timeout=request_timeout)
    auth_manager = LiproAuthManager(client)

    # Set stored tokens if available
    if "access_token" in entry.data and "refresh_token" in entry.data:
        auth_manager.set_tokens(
            entry.data["access_token"],
            entry.data["refresh_token"],
            entry.data.get("user_id"),
            entry.data.get("expires_at"),
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
    if auth_data["access_token"] != entry.data.get("access_token") or auth_data[
        "refresh_token"
    ] != entry.data.get("refresh_token"):
        hass.config_entries.async_update_entry(
            entry,
            data={
                **entry.data,
                "access_token": auth_data["access_token"],
                "refresh_token": auth_data["refresh_token"],
                "expires_at": auth_data["expires_at"],
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
) -> tuple[Any, LiproDataUpdateCoordinator]:
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
                    parts = unique_id[6:].split("_")
                    if parts and parts[0]:
                        device_id = parts[0]
                        break

        if not device_id:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="cannot_determine_device",
            )

    # Find the device across all config entries
    for entry in hass.config_entries.async_entries(DOMAIN):
        if hasattr(entry, "runtime_data") and entry.runtime_data:
            device = entry.runtime_data.get_device(device_id)
            if device:
                return device, entry.runtime_data

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

    device, coordinator = await _get_device_and_coordinator(hass, call)

    _LOGGER.info(
        "Service call: send_command to %s, command=%s, properties=%s",
        device.serial,
        command,
        properties,
    )

    try:
        success = await coordinator.async_send_command(device, command, properties)
        if not success:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="command_failed",
            )
        return {"success": True, "device_id": device.serial}
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

    _LOGGER.info("Service call: get_schedules for %s", device.serial)

    try:
        schedules = await coordinator.client.get_device_schedules(
            device.iot_device_id,
            device.device_type_hex,
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
            "device_id": device.serial,
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
        )

        return {
            "success": True,
            "device_id": device.serial,
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
        )

        return {
            "success": True,
            "device_id": device.serial,
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
    share_manager = get_anonymous_share_manager()

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

    success = await share_manager.submit_report(force=True)

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
    share_manager = get_anonymous_share_manager()
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


async def _async_setup_services(hass: HomeAssistant) -> None:
    """Set up Lipro services."""
    if hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND):
        return  # Services already registered

    # Register services with lambda wrappers to pass hass
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_COMMAND,
        lambda call: _async_handle_send_command(hass, call),
        schema=SERVICE_SEND_COMMAND_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_SCHEDULES,
        lambda call: _async_handle_get_schedules(hass, call),
        schema=SERVICE_GET_SCHEDULES_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_SCHEDULE,
        lambda call: _async_handle_add_schedule(hass, call),
        schema=SERVICE_ADD_SCHEDULE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_SCHEDULES,
        lambda call: _async_handle_delete_schedules(hass, call),
        schema=SERVICE_DELETE_SCHEDULES_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    # Anonymous share services (no schema needed)
    hass.services.async_register(
        DOMAIN,
        SERVICE_SUBMIT_ANONYMOUS_SHARE,
        lambda call: _async_handle_submit_anonymous_share(hass, call),
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_ANONYMOUS_SHARE_REPORT,
        lambda call: _async_handle_get_anonymous_share_report(hass, call),
        supports_response=SupportsResponse.ONLY,
    )


async def async_unload_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> bool:
    """Unload a config entry."""
    # Shutdown coordinator (stops MQTT, closes API session, clears data)
    coordinator = entry.runtime_data
    if coordinator:
        await coordinator.async_shutdown()

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
