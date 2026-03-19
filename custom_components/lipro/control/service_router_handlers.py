"""Private handler implementations wired by ``control.service_router``."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging
from typing import cast

from homeassistant.core import HomeAssistant, ServiceCall

from ..const.base import DOMAIN
from ..services import contracts as _contracts
from ..services.command import (
    DeviceAndCoordinatorGetter,
    SendCommandLogger,
    ServicePropertySummarizer,
    async_handle_send_command as _async_handle_send_command_service,
)
from ..services.contracts import RefreshDevicesResult, SendCommandResult
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
    AnonymousShareManagerFactory as DiagnosticsShareManagerFactory,
    CapabilityResponse,
    ClientSessionGetter,
    DeveloperFeedbackResponse,
    DeveloperReportResponse,
    QueryCommandResultResponse,
    RuntimeCoordinatorIterator,
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
    ClientSessionFactory as ShareClientSessionFactory,
    ShareServiceResponse,
    async_handle_get_anonymous_share_report as _async_handle_get_anonymous_share_report_service,
    async_handle_submit_anonymous_share as _async_handle_submit_anonymous_share_service,
)
from .developer_router_support import (
    async_handle_fetch_sensor_history as _async_handle_fetch_sensor_history_support,
    collect_developer_reports as _collect_developer_reports,
    raise_optional_capability_error as _raise_optional_capability_error,
)
from .service_router_support import (
    DeviceAndCoordinatorGetter as RuntimeDeviceAndCoordinatorGetter,
)

type ScheduleHandler = Callable[..., Awaitable[dict[str, object]]]


async def _async_handle_schedule_request(
    service_handler: ScheduleHandler,
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: RuntimeDeviceAndCoordinatorGetter,
    logger: logging.Logger,
    **kwargs: object,
) -> dict[str, object]:
    """Run one schedule handler with the formal router collaborators."""
    return await service_handler(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        raise_service_error=_raise_service_error,
        logger=logger,
        **kwargs,
    )


async def async_handle_send_command(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: RuntimeDeviceAndCoordinatorGetter,
    summarize_service_properties: ServicePropertySummarizer,
    log_send_command_call: SendCommandLogger,
    logger: logging.Logger,
) -> SendCommandResult:
    """Handle the public send-command service."""
    return await _async_handle_send_command_service(
        hass,
        call,
        get_device_and_coordinator=cast(
            DeviceAndCoordinatorGetter,
            get_device_and_coordinator,
        ),
        summarize_service_properties=summarize_service_properties,
        log_send_command_call=log_send_command_call,
        resolve_command_failure_translation_key=_resolve_command_failure_translation_key,
        raise_service_error=_raise_service_error,
        logger=logger,
        attr_command=_contracts.ATTR_COMMAND,
        attr_properties=_contracts.ATTR_PROPERTIES,
        attr_device_id=_contracts.ATTR_DEVICE_ID,
    )


async def async_handle_get_schedules(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: RuntimeDeviceAndCoordinatorGetter,
    logger: logging.Logger,
) -> dict[str, object]:
    """Handle the public get-schedules service."""
    return await _async_handle_schedule_request(
        _async_handle_get_schedules_service,
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        logger=logger,
    )


async def async_handle_add_schedule(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: RuntimeDeviceAndCoordinatorGetter,
    logger: logging.Logger,
) -> dict[str, object]:
    """Handle the public add-schedule service."""
    return await _async_handle_schedule_request(
        _async_handle_add_schedule_service,
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        logger=logger,
        domain=DOMAIN,
        attr_days=_contracts.ATTR_DAYS,
        attr_times=_contracts.ATTR_TIMES,
        attr_events=_contracts.ATTR_EVENTS,
    )


async def async_handle_delete_schedules(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: RuntimeDeviceAndCoordinatorGetter,
    logger: logging.Logger,
) -> dict[str, object]:
    """Handle the public delete-schedules service."""
    return await _async_handle_schedule_request(
        _async_handle_delete_schedules_service,
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        logger=logger,
        attr_schedule_ids=_contracts.ATTR_SCHEDULE_IDS,
    )


async def async_handle_submit_anonymous_share(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_share_manager: ShareAnonymousShareManagerFactory,
    get_client_session: ShareClientSessionFactory,
) -> ShareServiceResponse:
    """Handle the public anonymous-share submission service."""
    return await _async_handle_submit_anonymous_share_service(
        hass,
        call,
        get_anonymous_share_manager=get_share_manager,
        get_client_session=get_client_session,
        raise_service_error=_raise_service_error,
        domain=DOMAIN,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
    )


async def async_handle_get_anonymous_share_report(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_share_manager: ShareAnonymousShareManagerFactory,
) -> ShareServiceResponse:
    """Handle the public anonymous-share preview service."""
    return await _async_handle_get_anonymous_share_report_service(
        hass,
        call,
        get_anonymous_share_manager=get_share_manager,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
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
    get_share_manager: DiagnosticsShareManagerFactory,
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


async def async_handle_refresh_devices(
    hass: HomeAssistant,
    call: ServiceCall,
) -> RefreshDevicesResult:
    """Handle the public refresh-devices service."""
    return await _async_handle_refresh_devices_service(
        hass,
        call,
        domain=DOMAIN,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
    )


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
