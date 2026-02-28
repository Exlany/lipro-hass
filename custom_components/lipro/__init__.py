"""The Lipro Smart Home integration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterator
import functools
import logging
import re
from typing import TYPE_CHECKING, Any, Final, NoReturn

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
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
from .services.command import (
    async_handle_send_command as _async_handle_send_command_service,
    async_send_command_with_service_errors as _async_send_command_with_service_errors_service,
)
from .services.device_lookup import (
    get_device_and_coordinator as _get_device_and_coordinator_service,
    iter_runtime_coordinators as _iter_runtime_coordinators_service,
)
from .services.diagnostics import (
    async_call_optional_capability as _async_call_optional_capability_service,
    async_handle_fetch_body_sensor_history as _async_handle_fetch_body_sensor_history_service,
    async_handle_fetch_door_sensor_history as _async_handle_fetch_door_sensor_history_service,
    async_handle_get_city as _async_handle_get_city_service,
    async_handle_get_developer_report as _async_handle_get_developer_report_service,
    async_handle_query_command_result as _async_handle_query_command_result_service,
    async_handle_submit_developer_feedback as _async_handle_submit_developer_feedback_service,
    build_sensor_history_result as _build_sensor_history_result_service,
    collect_developer_reports as _collect_developer_reports_service,
    raise_optional_capability_error as _raise_optional_capability_error_service,
)
from .services.errors import (
    raise_service_error as _raise_service_error_shared,
    resolve_command_failure_translation_key as _resolve_command_failure_translation_key_shared,
)
from .services.schedule import (
    async_handle_add_schedule as _async_handle_add_schedule_service,
    async_handle_delete_schedules as _async_handle_delete_schedules_service,
    async_handle_get_schedules as _async_handle_get_schedules_service,
)
from .services.share import (
    async_handle_get_anonymous_share_report as _async_handle_get_anonymous_share_report_service,
    async_handle_submit_anonymous_share as _async_handle_submit_anonymous_share_service,
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
    Platform.UPDATE,
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
SERVICE_QUERY_COMMAND_RESULT: Final = "query_command_result"
SERVICE_GET_CITY: Final = "get_city"
SERVICE_FETCH_BODY_SENSOR_HISTORY: Final = "fetch_body_sensor_history"
SERVICE_FETCH_DOOR_SENSOR_HISTORY: Final = "fetch_door_sensor_history"

ATTR_DEVICE_ID: Final = "device_id"
ATTR_COMMAND: Final = "command"
ATTR_PROPERTIES: Final = "properties"
ATTR_DAYS: Final = "days"
ATTR_TIMES: Final = "times"
ATTR_EVENTS: Final = "events"
ATTR_SCHEDULE_IDS: Final = "schedule_ids"
ATTR_NOTE: Final = "note"
ATTR_MSG_SN: Final = "msg_sn"
ATTR_SENSOR_DEVICE_ID: Final = "sensor_device_id"
ATTR_MESH_TYPE: Final = "mesh_type"
FIRMWARE_SUPPORT_MANIFEST: Final = "firmware_support_manifest.json"

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

SERVICE_QUERY_COMMAND_RESULT_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_MSG_SN): cv.string,
    },
)

SERVICE_FETCH_SENSOR_HISTORY_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_SENSOR_DEVICE_ID): cv.string,
        vol.Optional(ATTR_MESH_TYPE, default="2"): cv.string,
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


def _raise_service_error(
    translation_key: str,
    *,
    err: Exception | None = None,
) -> NoReturn:
    """Raise a translated HomeAssistantError, preserving the original cause."""
    _raise_service_error_shared(translation_key, err=err)


def _resolve_command_failure_translation_key(
    *,
    failure: dict[str, Any] | None = None,
    err: LiproApiError | None = None,
) -> str:
    """Map command failure context to a user-facing translation key."""
    return _resolve_command_failure_translation_key_shared(
        failure=failure,
        err=err,
    )


async def _async_send_command_with_service_errors(
    coordinator: LiproDataUpdateCoordinator,
    device: LiproDevice,
    *,
    command: str,
    properties: list[dict[str, str]] | None,
    requested_device_id: str | None,
    failure_log: str,
    api_error_log: str,
) -> None:
    """Send one command and map API/push failures to translated service errors."""
    await _async_send_command_with_service_errors_service(
        coordinator,
        device,
        command=command,
        properties=properties,
        requested_device_id=requested_device_id,
        failure_log=failure_log,
        api_error_log=api_error_log,
        resolve_command_failure_translation_key=_resolve_command_failure_translation_key,
        raise_service_error=_raise_service_error,
        logger=_LOGGER,
    )


def _iter_runtime_coordinators(
    hass: HomeAssistant,
) -> Iterator[LiproDataUpdateCoordinator]:
    """Iterate all active coordinators for the Lipro domain."""
    yield from _iter_runtime_coordinators_service(hass, domain=DOMAIN)


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


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Lipro component."""
    await _async_setup_services(hass)
    return True


def _build_entry_auth_context(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
) -> tuple[LiproClient, LiproAuthManager]:
    """Build API client and auth manager from config entry data."""
    phone_id = entry.data[CONF_PHONE_ID]
    phone = entry.data[CONF_PHONE]
    password_hash = entry.data[CONF_PASSWORD_HASH]

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

    if CONF_ACCESS_TOKEN in entry.data and CONF_REFRESH_TOKEN in entry.data:
        auth_manager.set_tokens(
            entry.data[CONF_ACCESS_TOKEN],
            entry.data[CONF_REFRESH_TOKEN],
            entry.data.get(CONF_USER_ID),
            entry.data.get(CONF_EXPIRES_AT),
        )

    auth_manager.set_credentials(phone, password_hash, password_is_hashed=True)
    return client, auth_manager


async def _async_authenticate_entry(auth_manager: LiproAuthManager) -> None:
    """Authenticate one config entry and map failures to HA setup exceptions."""
    try:
        await auth_manager.ensure_valid_token()
    except LiproAuthError as err:
        msg = f"Authentication failed: {err}"
        raise ConfigEntryAuthFailed(msg) from err
    except LiproConnectionError as err:
        msg = f"Connection failed: {err}"
        raise ConfigEntryNotReady(msg) from err


def _persist_entry_tokens_if_changed(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    auth_manager: LiproAuthManager,
) -> None:
    """Persist refreshed access/refresh tokens when they changed."""
    auth_data = auth_manager.get_auth_data()
    if auth_data[CONF_ACCESS_TOKEN] == entry.data.get(CONF_ACCESS_TOKEN) and auth_data[
        CONF_REFRESH_TOKEN
    ] == entry.data.get(CONF_REFRESH_TOKEN):
        return

    hass.config_entries.async_update_entry(
        entry,
        data={
            **entry.data,
            CONF_ACCESS_TOKEN: auth_data[CONF_ACCESS_TOKEN],
            CONF_REFRESH_TOKEN: auth_data[CONF_REFRESH_TOKEN],
            CONF_EXPIRES_AT: auth_data[CONF_EXPIRES_AT],
        },
    )


async def async_setup_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> bool:
    """Set up Lipro from a config entry."""
    client, auth_manager = _build_entry_auth_context(hass, entry)
    await _async_authenticate_entry(auth_manager)

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
    _persist_entry_tokens_if_changed(hass, entry, auth_manager)

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
    return await _get_device_and_coordinator_service(
        hass,
        call,
        domain=DOMAIN,
        serial_pattern=_SERIAL_PATTERN,
        attr_device_id=ATTR_DEVICE_ID,
    )


async def _async_handle_send_command(
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
        attr_command=ATTR_COMMAND,
        attr_properties=ATTR_PROPERTIES,
        attr_device_id=ATTR_DEVICE_ID,
    )


async def _async_handle_get_schedules(
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


async def _async_handle_add_schedule(
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
        attr_days=ATTR_DAYS,
        attr_times=ATTR_TIMES,
        attr_events=ATTR_EVENTS,
    )


async def _async_handle_delete_schedules(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the delete_schedules service call."""
    return await _async_handle_delete_schedules_service(
        hass,
        call,
        get_device_and_coordinator=_get_device_and_coordinator,
        raise_service_error=_raise_service_error,
        logger=_LOGGER,
        attr_schedule_ids=ATTR_SCHEDULE_IDS,
    )


async def _async_handle_submit_anonymous_share(
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
    )


async def _async_handle_get_anonymous_share_report(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the get_anonymous_share_report service call."""
    return await _async_handle_get_anonymous_share_report_service(
        hass,
        call,
        get_anonymous_share_manager=get_anonymous_share_manager,
    )


def _collect_developer_reports(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Collect developer reports from active config entries."""
    return _collect_developer_reports_service(
        hass,
        iter_runtime_coordinators=_iter_runtime_coordinators,
    )


async def _async_handle_get_developer_report(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Handle the get_developer_report service call."""
    return await _async_handle_get_developer_report_service(
        hass,
        call,
        collect_reports=_collect_developer_reports,
    )


async def _async_handle_submit_developer_feedback(
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
        service_submit_developer_feedback=SERVICE_SUBMIT_DEVELOPER_FEEDBACK,
        attr_note=ATTR_NOTE,
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
    """Call optional capability API and map LiproApiError to service error."""
    return await _async_call_optional_capability_service(
        capability,
        method,
        raise_optional_error=_raise_optional_capability_error,
        **kwargs,
    )


def _build_sensor_history_result(
    serial: str,
    sensor_device_id: str,
    mesh_type: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    """Build common service response for sensor history diagnostics."""
    return _build_sensor_history_result_service(
        serial,
        sensor_device_id,
        mesh_type,
        result,
    )


async def _async_handle_query_command_result(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Developer-only service: query command delivery result by msgSn."""
    return await _async_handle_query_command_result_service(
        hass,
        call,
        get_device_and_coordinator=_get_device_and_coordinator,
        async_call_optional_capability=_async_call_optional_capability,
        attr_msg_sn=ATTR_MSG_SN,
        service_query_command_result=SERVICE_QUERY_COMMAND_RESULT,
    )


async def _async_handle_get_city(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Developer-only service: fetch city metadata."""
    return await _async_handle_get_city_service(
        hass,
        call,
        iter_runtime_coordinators=_iter_runtime_coordinators,
        raise_optional_error=_raise_optional_capability_error,
        service_get_city=SERVICE_GET_CITY,
    )


async def _async_handle_fetch_sensor_history(
    *,
    hass: HomeAssistant,
    call: ServiceCall,
    service_handler: Callable[..., Awaitable[dict[str, Any]]],
    service_name_kw: str,
    service_name: str,
) -> dict[str, Any]:
    """Shared wrapper for body/door sensor-history services."""
    handler_kwargs: dict[str, Any] = {
        "get_device_and_coordinator": _get_device_and_coordinator,
        "async_call_optional_capability": _async_call_optional_capability,
        "build_sensor_history_result": _build_sensor_history_result,
        "attr_sensor_device_id": ATTR_SENSOR_DEVICE_ID,
        "attr_mesh_type": ATTR_MESH_TYPE,
        service_name_kw: service_name,
    }
    return await service_handler(
        hass,
        call,
        **handler_kwargs,
    )


async def _async_handle_fetch_body_sensor_history(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Developer-only service: fetch body-sensor history payload."""
    return await _async_handle_fetch_sensor_history(
        hass=hass,
        call=call,
        service_handler=_async_handle_fetch_body_sensor_history_service,
        service_name_kw="service_fetch_body_sensor_history",
        service_name=SERVICE_FETCH_BODY_SENSOR_HISTORY,
    )


async def _async_handle_fetch_door_sensor_history(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, Any]:
    """Developer-only service: fetch door-sensor history payload."""
    return await _async_handle_fetch_sensor_history(
        hass=hass,
        call=call,
        service_handler=_async_handle_fetch_door_sensor_history_service,
        service_name_kw="service_fetch_door_sensor_history",
        service_name=SERVICE_FETCH_DOOR_SENSOR_HISTORY,
    )


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
    (
        SERVICE_QUERY_COMMAND_RESULT,
        _async_handle_query_command_result,
        SERVICE_QUERY_COMMAND_RESULT_SCHEMA,
        SupportsResponse.ONLY,
    ),
    (
        SERVICE_GET_CITY,
        _async_handle_get_city,
        None,
        SupportsResponse.ONLY,
    ),
    (
        SERVICE_FETCH_BODY_SENSOR_HISTORY,
        _async_handle_fetch_body_sensor_history,
        SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
        SupportsResponse.ONLY,
    ),
    (
        SERVICE_FETCH_DOOR_SENSOR_HISTORY,
        _async_handle_fetch_door_sensor_history,
        SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
        SupportsResponse.ONLY,
    ),
)


def _async_register_service(
    hass: HomeAssistant,
    service_name: str,
    service_handler: Callable[[HomeAssistant, ServiceCall], Awaitable[dict[str, Any]]],
    service_schema: vol.Schema | None,
    supports_response: SupportsResponse,
) -> None:
    """Register one Lipro service."""
    register_kwargs: dict[str, Any] = {"supports_response": supports_response}
    if service_schema is not None:
        register_kwargs["schema"] = service_schema
    hass.services.async_register(
        DOMAIN,
        service_name,
        functools.partial(service_handler, hass),
        **register_kwargs,
    )


def _async_remove_services(hass: HomeAssistant) -> None:
    """Remove all Lipro services registered by this integration."""
    for service_name, *_ in _SERVICE_REGISTRATIONS:
        hass.services.async_remove(DOMAIN, service_name)


async def _async_setup_services(hass: HomeAssistant) -> None:
    """Set up Lipro services."""
    if hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND):
        return  # Services already registered

    for (
        service_name,
        service_handler,
        service_schema,
        supports_response,
    ) in _SERVICE_REGISTRATIONS:
        _async_register_service(
            hass,
            service_name,
            service_handler,
            service_schema,
            supports_response,
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
        _async_remove_services(hass)

    return result


async def async_reload_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
