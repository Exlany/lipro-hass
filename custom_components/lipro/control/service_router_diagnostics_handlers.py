"""Diagnostics and developer handler family for ``control.service_router``."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, ServiceCall

from ..const.base import DOMAIN
from ..services import contracts as _contracts
from ..services.diagnostics import (
    async_handle_fetch_body_sensor_history as _async_handle_fetch_body_sensor_history_service,
    async_handle_fetch_door_sensor_history as _async_handle_fetch_door_sensor_history_service,
    async_handle_get_city as _async_handle_get_city_service,
    async_handle_get_developer_report as _async_handle_get_developer_report_service,
    async_handle_query_command_result as _async_handle_query_command_result_service,
    async_handle_query_user_cloud as _async_handle_query_user_cloud_service,
    async_handle_submit_developer_feedback as _async_handle_submit_developer_feedback_service,
)
from ..services.diagnostics.types import (
    AnonymousShareManagerFactory,
    CapabilityResponse,
    ClientSessionGetter,
    DeveloperFeedbackResponse,
    DeveloperReportResponse,
    QueryCommandResultResponse,
    RuntimeCoordinatorIterator,
    SensorHistoryResponse,
)
from ..services.errors import raise_service_error as _raise_service_error
from .developer_router_support import (
    async_handle_fetch_sensor_history as _async_handle_fetch_sensor_history_support,
    collect_developer_reports as _collect_developer_reports,
    raise_optional_capability_error as _raise_optional_capability_error,
)
from .service_router_support import (
    DeviceAndCoordinatorGetter as RuntimeDeviceAndCoordinatorGetter,
)


async def async_handle_get_developer_report(
    hass: HomeAssistant,
    call: ServiceCall,
) -> DeveloperReportResponse:
    """Handle the developer report service."""
    return await _async_handle_get_developer_report_service(
        hass,
        call,
        collect_reports=_collect_developer_reports,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
    )


async def async_handle_submit_developer_feedback(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_share_manager: AnonymousShareManagerFactory,
    get_client_session: ClientSessionGetter,
) -> DeveloperFeedbackResponse:
    """Handle the developer feedback submission service."""
    return await _async_handle_submit_developer_feedback_service(
        hass,
        call,
        collect_reports=_collect_developer_reports,
        get_anonymous_share_manager=get_share_manager,
        get_client_session=get_client_session,
        domain=DOMAIN,
        service_submit_developer_feedback=_contracts.SERVICE_SUBMIT_DEVELOPER_FEEDBACK,
        attr_note=_contracts.ATTR_NOTE,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
        raise_service_error=_raise_service_error,
    )


async def async_handle_query_command_result(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: RuntimeDeviceAndCoordinatorGetter,
) -> QueryCommandResultResponse:
    """Handle the developer command-result query service."""
    return await _async_handle_query_command_result_service(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        attr_msg_sn=_contracts.ATTR_MSG_SN,
        attr_max_attempts=_contracts.ATTR_MAX_ATTEMPTS,
        attr_time_budget_seconds=_contracts.ATTR_TIME_BUDGET_SECONDS,
        raise_service_error=_raise_service_error,
    )


async def async_handle_get_city(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    iter_runtime_coordinators: RuntimeCoordinatorIterator,
) -> CapabilityResponse:
    """Handle the developer city query service."""
    return await _async_handle_get_city_service(
        hass,
        call,
        iter_runtime_coordinators=iter_runtime_coordinators,
        raise_optional_error=_raise_optional_capability_error,
        service_get_city=_contracts.SERVICE_GET_CITY,
    )


async def async_handle_query_user_cloud(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    iter_runtime_coordinators: RuntimeCoordinatorIterator,
) -> CapabilityResponse:
    """Handle the developer user-cloud query service."""
    return await _async_handle_query_user_cloud_service(
        hass,
        call,
        iter_runtime_coordinators=iter_runtime_coordinators,
        raise_optional_error=_raise_optional_capability_error,
        service_query_user_cloud=_contracts.SERVICE_QUERY_USER_CLOUD,
    )


async def async_handle_fetch_body_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: RuntimeDeviceAndCoordinatorGetter,
) -> SensorHistoryResponse:
    """Handle the developer body-sensor history service."""
    return await _async_handle_fetch_sensor_history_support(
        hass=hass,
        call=call,
        service_handler=_async_handle_fetch_body_sensor_history_service,
        service_name_kw="service_fetch_body_sensor_history",
        service_name=_contracts.SERVICE_FETCH_BODY_SENSOR_HISTORY,
        get_device_and_coordinator=get_device_and_coordinator,
    )


async def async_handle_fetch_door_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: RuntimeDeviceAndCoordinatorGetter,
) -> SensorHistoryResponse:
    """Handle the developer door-sensor history service."""
    return await _async_handle_fetch_sensor_history_support(
        hass=hass,
        call=call,
        service_handler=_async_handle_fetch_door_sensor_history_service,
        service_name_kw="service_fetch_door_sensor_history",
        service_name=_contracts.SERVICE_FETCH_DOOR_SENSOR_HISTORY,
        get_device_and_coordinator=get_device_and_coordinator,
    )


__all__ = [
    "async_handle_fetch_body_sensor_history",
    "async_handle_fetch_door_sensor_history",
    "async_handle_get_city",
    "async_handle_get_developer_report",
    "async_handle_query_command_result",
    "async_handle_query_user_cloud",
    "async_handle_submit_developer_feedback",
]
