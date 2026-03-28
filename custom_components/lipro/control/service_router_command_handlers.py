"""Command-dispatch handler family for ``control.service_router``."""

from __future__ import annotations

import logging
from typing import cast

from homeassistant.core import HomeAssistant, ServiceCall

from ..services import contracts as _contracts
from ..services.command import (
    DeviceAndCoordinatorGetter,
    SendCommandLogger,
    ServicePropertySummarizer,
    async_handle_send_command as _async_handle_send_command_service,
)
from ..services.contracts import SendCommandResult
from ..services.errors import (
    raise_service_error as _raise_service_error,
    resolve_command_failure_translation_key as _resolve_command_failure_translation_key,
)
from .service_router_support import (
    DeviceAndCoordinatorGetter as RuntimeDeviceAndCoordinatorGetter,
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


__all__ = ['async_handle_send_command']
