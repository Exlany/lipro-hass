"""Schedule handler family for ``control.service_router``."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging

from homeassistant.core import HomeAssistant, ServiceCall

from ..const.base import DOMAIN
from ..services import contracts as _contracts
from ..services.errors import raise_service_error as _raise_service_error
from ..services.schedule import (
    async_handle_add_schedule as _async_handle_add_schedule_service,
    async_handle_delete_schedules as _async_handle_delete_schedules_service,
    async_handle_get_schedules as _async_handle_get_schedules_service,
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


__all__ = [
    'async_handle_add_schedule',
    'async_handle_delete_schedules',
    'async_handle_get_schedules',
]
