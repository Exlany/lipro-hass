"""Formal control-plane router for HA service callbacks."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, ServiceCall

from ..const.base import DOMAIN, IOT_DEVICE_ID_PREFIX
from ..core.utils.redaction import redact_identifier as _redact_identifier
from ..services import contracts as _contracts
from ..services.contracts import RefreshDevicesResult, SendCommandResult
from ..services.diagnostics.types import (
    CapabilityResponse,
    DeveloperFeedbackResponse,
    DeveloperReportResponse,
    QueryCommandResultResponse,
    SensorHistoryResponse,
)
from ..services.share import ShareServiceResponse
from . import service_router_handlers as _handlers, service_router_support as _support

_LOGGER = logging.getLogger(__name__)
_SERIAL_PATTERN = _support.build_serial_pattern(IOT_DEVICE_ID_PREFIX)
_summarize_service_properties = _support.summarize_service_properties
_log_send_command_call = _support.build_send_command_logger(
    logger=_LOGGER,
    redact_identifier=_redact_identifier,
)
_get_device_and_coordinator = _support.build_device_and_coordinator_getter(
    domain=DOMAIN,
    serial_pattern=_SERIAL_PATTERN,
    attr_device_id=_contracts.ATTR_DEVICE_ID,
)
_get_developer_device_and_coordinator = (
    _support.build_developer_device_and_coordinator_getter(
        _get_device_and_coordinator,
    )
)


async def async_handle_send_command(
    hass: HomeAssistant,
    call: ServiceCall,
) -> SendCommandResult:
    """Handle the send_command service call."""
    return await _handlers.async_handle_send_command(
        hass,
        call,
        get_device_and_coordinator=_get_device_and_coordinator,
        summarize_service_properties=_summarize_service_properties,
        log_send_command_call=_log_send_command_call,
        logger=_LOGGER,
    )


async def async_handle_get_schedules(
    hass: HomeAssistant,
    call: ServiceCall,
) -> dict[str, object]:
    """Handle the get_schedules service call."""
    return await _handlers.async_handle_get_schedules(
        hass,
        call,
        get_device_and_coordinator=_get_device_and_coordinator,
        logger=_LOGGER,
    )


async def async_handle_add_schedule(
    hass: HomeAssistant,
    call: ServiceCall,
) -> dict[str, object]:
    """Handle the add_schedule service call."""
    return await _handlers.async_handle_add_schedule(
        hass,
        call,
        get_device_and_coordinator=_get_device_and_coordinator,
        logger=_LOGGER,
    )


async def async_handle_delete_schedules(
    hass: HomeAssistant,
    call: ServiceCall,
) -> dict[str, object]:
    """Handle the delete_schedules service call."""
    return await _handlers.async_handle_delete_schedules(
        hass,
        call,
        get_device_and_coordinator=_get_device_and_coordinator,
        logger=_LOGGER,
    )


async def async_handle_submit_anonymous_share(
    hass: HomeAssistant,
    call: ServiceCall,
) -> ShareServiceResponse:
    """Handle the submit_anonymous_share service call."""
    return await _handlers.async_handle_submit_anonymous_share(
        hass,
        call,
        get_share_manager=_support.get_anonymous_share_manager,
        get_client_session=_support.get_client_session,
    )


async def async_handle_get_anonymous_share_report(
    hass: HomeAssistant,
    call: ServiceCall,
) -> ShareServiceResponse:
    """Handle the get_anonymous_share_report service call."""
    return await _handlers.async_handle_get_anonymous_share_report(
        hass,
        call,
        get_share_manager=_support.get_anonymous_share_manager,
    )


async def async_handle_get_developer_report(
    hass: HomeAssistant,
    call: ServiceCall,
) -> DeveloperReportResponse:
    """Handle the get_developer_report service call."""
    return await _handlers.async_handle_get_developer_report(hass, call)


async def async_handle_submit_developer_feedback(
    hass: HomeAssistant,
    call: ServiceCall,
) -> DeveloperFeedbackResponse:
    """Handle the submit_developer_feedback service call."""
    return await _handlers.async_handle_submit_developer_feedback(
        hass,
        call,
        get_share_manager=_support.get_anonymous_share_manager,
        get_client_session=_support.get_client_session,
    )


async def async_handle_query_command_result(
    hass: HomeAssistant,
    call: ServiceCall,
) -> QueryCommandResultResponse:
    """Developer-only service: query command result status by msgSn."""
    return await _handlers.async_handle_query_command_result(
        hass,
        call,
        get_device_and_coordinator=_get_developer_device_and_coordinator,
    )


async def async_handle_get_city(
    hass: HomeAssistant,
    call: ServiceCall,
) -> CapabilityResponse:
    """Developer-only service: get city information."""
    return await _handlers.async_handle_get_city(
        hass,
        call,
        iter_runtime_coordinators=_support.build_developer_runtime_coordinator_iterator(
            hass
        ),
    )


async def async_handle_query_user_cloud(
    hass: HomeAssistant,
    call: ServiceCall,
) -> CapabilityResponse:
    """Developer-only service: query user cloud information."""
    return await _handlers.async_handle_query_user_cloud(
        hass,
        call,
        iter_runtime_coordinators=_support.build_developer_runtime_coordinator_iterator(
            hass
        ),
    )


async def async_handle_fetch_body_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
) -> SensorHistoryResponse:
    """Developer-only service: fetch body-sensor history payload."""
    return await _handlers.async_handle_fetch_body_sensor_history(
        hass,
        call,
        get_device_and_coordinator=_get_developer_device_and_coordinator,
    )


async def async_handle_fetch_door_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
) -> SensorHistoryResponse:
    """Developer-only service: fetch door-sensor history payload."""
    return await _handlers.async_handle_fetch_door_sensor_history(
        hass,
        call,
        get_device_and_coordinator=_get_developer_device_and_coordinator,
    )


async def async_handle_refresh_devices(
    hass: HomeAssistant,
    call: ServiceCall,
) -> RefreshDevicesResult:
    """Handle the refresh_devices service call."""
    return await _handlers.async_handle_refresh_devices(hass, call)


__all__ = [
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
]
