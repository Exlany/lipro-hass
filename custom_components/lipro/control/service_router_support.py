"""Private support helpers for the formal control-plane service router."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from functools import partial
import logging
import re
from typing import cast

from homeassistant.core import HomeAssistant, ServiceCall

from ..core import LiproDevice
from ..runtime_types import LiproCoordinator
from ..services.command import SendCommandLogger
from ..services.contracts import ServicePropertySummary
from ..services.device_lookup import (
    get_device_and_coordinator as _get_device_and_coordinator_service,
)
from ..services.diagnostics.types import RuntimeCoordinatorIterator
from .developer_router_support import (
    build_developer_runtime_coordinator_iterator as _build_developer_runtime_coordinator_iterator,
    get_developer_device_and_coordinator as _get_developer_device_and_coordinator_support,
)

type DeviceAndCoordinatorGetter = Callable[
    [HomeAssistant, ServiceCall],
    Awaitable[tuple[LiproDevice, LiproCoordinator]],
]
type IdentifierRedactor = Callable[[str | None], str | None]


def build_serial_pattern(iot_device_id_prefix: str) -> re.Pattern[str]:
    """Build the shared resolver pattern for serials and mesh-group ids."""
    return re.compile(
        rf"({re.escape(iot_device_id_prefix)}[0-9A-Fa-f]{{12}}|mesh_group_\d+)(?:_|$)"
    )


def summarize_service_properties(properties: object) -> ServicePropertySummary:
    """Build a log-safe summary for service properties."""
    if not isinstance(properties, list):
        return {"count": 0, "keys": []}

    keys: list[str] = []
    for item in properties:
        if not isinstance(item, dict):
            continue
        key = item.get("key")
        if isinstance(key, str):
            keys.append(key)
    return {"count": len(properties), "keys": keys}


def log_send_command_call(
    *,
    logger: logging.Logger,
    requested_device_id: str | None,
    resolved_serial: str,
    command: str,
    properties_summary: ServicePropertySummary,
    redact_identifier: IdentifierRedactor,
) -> bool:
    """Log send-command routing details and return alias-resolution state."""
    is_alias_resolution = bool(
        requested_device_id and requested_device_id != resolved_serial
    )

    if is_alias_resolution and requested_device_id is not None:
        logger.info(
            "Service call: send_command requested_id=%s resolved_to=%s, "
            "command=%s, property_summary=%s",
            redact_identifier(requested_device_id),
            redact_identifier(resolved_serial),
            command,
            properties_summary,
        )
    else:
        logger.info(
            "Service call: send_command to %s, command=%s, property_summary=%s",
            redact_identifier(resolved_serial),
            command,
            properties_summary,
        )

    return is_alias_resolution


def build_send_command_logger(
    *,
    logger: logging.Logger,
    redact_identifier: IdentifierRedactor,
) -> SendCommandLogger:
    """Bind logger/redaction collaborators for send-command audit logging."""

    def _bound_send_command_logger(
        requested_device_id: str | None,
        resolved_serial: str,
        command: str,
        properties_summary: ServicePropertySummary,
    ) -> bool:
        return log_send_command_call(
            logger=logger,
            requested_device_id=requested_device_id,
            resolved_serial=resolved_serial,
            command=command,
            properties_summary=properties_summary,
            redact_identifier=redact_identifier,
        )

    return _bound_send_command_logger


async def async_get_device_and_coordinator(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    domain: str,
    serial_pattern: re.Pattern[str],
    attr_device_id: str,
) -> tuple[LiproDevice, LiproCoordinator]:
    """Resolve one device/coordinator pair from a service call."""
    return await _get_device_and_coordinator_service(
        hass,
        call,
        domain=domain,
        serial_pattern=serial_pattern,
        attr_device_id=attr_device_id,
    )


def build_device_and_coordinator_getter(
    *,
    domain: str,
    serial_pattern: re.Pattern[str],
    attr_device_id: str,
) -> DeviceAndCoordinatorGetter:
    """Bind the public device resolver for router handler reuse."""
    return cast(
        DeviceAndCoordinatorGetter,
        partial(
            async_get_device_and_coordinator,
            domain=domain,
            serial_pattern=serial_pattern,
            attr_device_id=attr_device_id,
        ),
    )


async def async_get_developer_device_and_coordinator(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: DeviceAndCoordinatorGetter,
) -> tuple[LiproDevice, LiproCoordinator]:
    """Resolve one device/coordinator pair while enforcing developer mode."""
    return await _get_developer_device_and_coordinator_support(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
    )


def build_developer_device_and_coordinator_getter(
    get_device_and_coordinator: DeviceAndCoordinatorGetter,
) -> DeviceAndCoordinatorGetter:
    """Bind developer-mode gating on top of the public device resolver."""
    return cast(
        DeviceAndCoordinatorGetter,
        partial(
            async_get_developer_device_and_coordinator,
            get_device_and_coordinator=get_device_and_coordinator,
        ),
    )


def build_developer_runtime_coordinator_iterator(
    hass: HomeAssistant,
) -> RuntimeCoordinatorIterator:
    """Freeze the current debug-enabled runtime view for one service call."""
    return _build_developer_runtime_coordinator_iterator(hass)


__all__ = [
    "DeviceAndCoordinatorGetter",
    "IdentifierRedactor",
    "async_get_developer_device_and_coordinator",
    "async_get_device_and_coordinator",
    "build_developer_device_and_coordinator_getter",
    "build_developer_runtime_coordinator_iterator",
    "build_device_and_coordinator_getter",
    "build_send_command_logger",
    "build_serial_pattern",
    "log_send_command_call",
    "summarize_service_properties",
]
