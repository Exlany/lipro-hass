"""Formal callback family home for service-router handlers."""

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
from .runtime_access import (
    iter_runtime_entry_coordinators as _iter_runtime_entry_coordinators,
)
from .service_router_diagnostics_handlers import (
    async_handle_fetch_body_sensor_history,
    async_handle_fetch_door_sensor_history,
    async_handle_get_city,
    async_handle_get_developer_report,
    async_handle_query_command_result,
    async_handle_query_user_cloud,
    async_handle_submit_developer_feedback,
)
from .service_router_support import (
    DeviceAndCoordinatorGetter as RuntimeDeviceAndCoordinatorGetter,
)

type ScheduleHandler = Callable[..., Awaitable[dict[str, object]]]


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
        iter_runtime_entry_coordinators=_iter_runtime_entry_coordinators,
    )


__all__ = [
    'async_handle_add_schedule',
    'async_handle_delete_schedules',
    'async_handle_fetch_body_sensor_history',
    'async_handle_fetch_door_sensor_history',
    'async_handle_get_anonymous_share_report',
    'async_handle_get_city',
    'async_handle_get_developer_report',
    'async_handle_get_schedules',
    'async_handle_query_command_result',
    'async_handle_query_user_cloud',
    'async_handle_refresh_devices',
    'async_handle_send_command',
    'async_handle_submit_anonymous_share',
    'async_handle_submit_developer_feedback',
]
