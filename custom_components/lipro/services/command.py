"""Command service handlers for Lipro integration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import logging
from typing import NoReturn, Protocol, cast

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from ..const.base import DOMAIN
from ..core import LiproApiError
from ..core.utils.log_safety import safe_error_placeholder as _safe_error_placeholder
from ..core.utils.redaction import redact_identifier as _redact_identifier
from .contracts import (
    SERVICE_SEND_COMMAND_SCHEMA,
    CommandFailureSummary,
    SendCommandResult,
    ServiceProperty,
    ServicePropertySummary,
)
from .execution import ServiceErrorRaiser

type CommandProperties = list[ServiceProperty]


@dataclass(slots=True, frozen=True)
class _SendCommandRequest:
    command: str
    properties: CommandProperties | None
    requested_device_id: str | None
    properties_summary: ServicePropertySummary


@dataclass(slots=True, frozen=True)
class _SendCommandExecution:
    device: CommandDevice
    coordinator: CommandCoordinator
    is_alias_resolution: bool


class CommandDevice(Protocol):
    """Service-layer command device contract."""

    serial: str


class CommandService(Protocol):
    """Command service contract used by the send_command service."""

    @property
    def last_failure(self) -> CommandFailureSummary | None:
        """Return the latest command failure payload, if any."""

    async def async_send_command(
        self,
        device: CommandDevice,
        command: str,
        properties: CommandProperties | None = None,
        fallback_device_id: str | None = None,
    ) -> bool:
        """Dispatch one command via the coordinator."""


class CommandCoordinator(Protocol):
    """Coordinator contract used by the send_command service."""

    command_service: CommandService


class DeviceAndCoordinatorGetter(Protocol):
    """Resolve one device/coordinator pair for a service call."""

    async def __call__(
        self,
        hass: HomeAssistant,
        call: ServiceCall,
    ) -> tuple[CommandDevice, CommandCoordinator]:
        """Return the resolved device and coordinator."""


class ServicePropertySummarizer(Protocol):
    """Summarize send_command properties for logging."""

    def __call__(
        self,
        properties: CommandProperties | None,
    ) -> ServicePropertySummary:
        """Return one log-safe property summary."""


class SendCommandLogger(Protocol):
    """Emit the send_command audit log and report alias resolution."""

    def __call__(
        self,
        requested_device_id: str | None,
        resolved_serial: str,
        command: str,
        properties_summary: ServicePropertySummary,
    ) -> bool:
        """Return whether alias resolution happened."""


class CommandFailureTranslationResolver(Protocol):
    """Resolve command failures into translated service keys."""

    def __call__(
        self,
        *,
        failure: Mapping[str, object] | None = None,
        err: LiproApiError | None = None,
    ) -> str:
        """Return one translated command failure key."""


def _raise_invalid_send_command_request(
    *, logger: logging.Logger, field_name: str
) -> NoReturn:
    """Raise one translated service validation error for invalid direct payloads."""
    logger.warning("Rejecting invalid send_command field type: %s", field_name)
    raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="invalid_command_request",
    )


def _validate_send_command_payload_types(
    payload: Mapping[str, object],
    *,
    logger: logging.Logger,
    attr_command: str,
    attr_properties: str,
    attr_device_id: str,
) -> None:
    """Reject direct handler payloads that rely on voluptuous type coercion."""
    if not isinstance(payload.get(attr_command), str):
        _raise_invalid_send_command_request(logger=logger, field_name=attr_command)

    if attr_device_id in payload and not isinstance(payload.get(attr_device_id), str):
        _raise_invalid_send_command_request(logger=logger, field_name=attr_device_id)

    if attr_properties not in payload:
        return

    properties = payload.get(attr_properties)
    if not isinstance(properties, list):
        _raise_invalid_send_command_request(logger=logger, field_name=attr_properties)

    for item in properties:
        if not isinstance(item, dict):
            _raise_invalid_send_command_request(
                logger=logger, field_name=attr_properties
            )
        key = item.get("key")
        value = item.get("value")
        if not isinstance(key, str) or not isinstance(value, str):
            _raise_invalid_send_command_request(
                logger=logger, field_name=attr_properties
            )


def _validate_send_command_payload(
    call: ServiceCall,
    *,
    logger: logging.Logger,
    attr_command: str,
    attr_properties: str,
    attr_device_id: str,
) -> dict[str, object]:
    """Validate one direct handler payload against the formal service schema."""
    payload: dict[str, object] = {attr_command: call.data[attr_command]}
    for attr_name in (attr_properties, attr_device_id):
        if attr_name in call.data:
            payload[attr_name] = call.data[attr_name]

    _validate_send_command_payload_types(
        payload,
        logger=logger,
        attr_command=attr_command,
        attr_properties=attr_properties,
        attr_device_id=attr_device_id,
    )
    try:
        return cast(dict[str, object], SERVICE_SEND_COMMAND_SCHEMA(payload))
    except vol.Invalid as err:
        logger.warning("Rejecting invalid send_command service payload: %s", err)
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="invalid_command_request",
        ) from err


def _build_send_command_request(
    call: ServiceCall,
    *,
    summarize_service_properties: ServicePropertySummarizer,
    logger: logging.Logger,
    attr_command: str,
    attr_properties: str,
    attr_device_id: str,
) -> _SendCommandRequest:
    """Build one normalized send-command request payload from service data."""
    payload = _validate_send_command_payload(
        call,
        logger=logger,
        attr_command=attr_command,
        attr_properties=attr_properties,
        attr_device_id=attr_device_id,
    )
    command = cast(str, payload[attr_command])
    properties = cast(CommandProperties | None, payload.get(attr_properties))
    requested_device_id = cast(str | None, payload.get(attr_device_id))
    return _SendCommandRequest(
        command=command,
        properties=properties,
        requested_device_id=requested_device_id,
        properties_summary=summarize_service_properties(properties),
    )


def _build_failure_summary(
    failure_context: CommandFailureSummary | None,
) -> CommandFailureSummary | None:
    """Return a trimmed failure summary for warning logs."""
    if failure_context is None:
        return None
    summary: CommandFailureSummary = {}
    for key in ("reason", "code", "route"):
        value = failure_context.get(key)
        if isinstance(value, (int, str)) and not isinstance(value, bool):
            summary[key] = value
    return summary or None


def _raise_send_command_failure(
    *,
    command: str,
    requested_device_id: str | None,
    device_serial: str,
    failure_context: CommandFailureSummary | None,
    failure_log: str,
    resolve_command_failure_translation_key: CommandFailureTranslationResolver,
    raise_service_error: ServiceErrorRaiser,
    logger: logging.Logger,
) -> NoReturn:
    logger.warning(
        failure_log,
        command,
        _redact_identifier(requested_device_id) or "***",
        _redact_identifier(device_serial) or "***",
        _build_failure_summary(failure_context),
    )
    raise_service_error(
        resolve_command_failure_translation_key(
            failure=failure_context,
        )
    )


async def async_send_command_with_service_errors(
    coordinator: CommandCoordinator,
    device: CommandDevice,
    *,
    command: str,
    properties: CommandProperties | None,
    requested_device_id: str | None,
    failure_log: str,
    api_error_log: str,
    resolve_command_failure_translation_key: CommandFailureTranslationResolver,
    raise_service_error: ServiceErrorRaiser,
    logger: logging.Logger,
) -> None:
    """Send one command and map API/push failures to translated service errors."""
    try:
        success = await coordinator.command_service.async_send_command(
            device,
            command,
            properties,
            fallback_device_id=requested_device_id,
        )
        if success:
            return

        _raise_send_command_failure(
            command=command,
            requested_device_id=requested_device_id,
            device_serial=device.serial,
            failure_context=coordinator.command_service.last_failure,
            failure_log=failure_log,
            resolve_command_failure_translation_key=resolve_command_failure_translation_key,
            raise_service_error=raise_service_error,
            logger=logger,
        )
    except HomeAssistantError:
        raise
    except LiproApiError as err:
        logger.warning(api_error_log, _safe_error_placeholder(err))
        raise_service_error(
            resolve_command_failure_translation_key(err=err),
            err=err,
        )


def build_send_command_result(
    resolved_serial: str,
    *,
    requested_device_id: str | None,
    is_alias_resolution: bool,
) -> SendCommandResult:
    """Build send_command response payload with alias metadata."""
    result: SendCommandResult = {
        "success": True,
        "serial": resolved_serial,
    }
    if is_alias_resolution and requested_device_id:
        result["requested_device_id"] = requested_device_id
        result["resolved_device_id"] = resolved_serial
    return result


async def _prepare_send_command_execution(
    *,
    hass: HomeAssistant,
    call: ServiceCall,
    request: _SendCommandRequest,
    get_device_and_coordinator: DeviceAndCoordinatorGetter,
    log_send_command_call: SendCommandLogger,
) -> _SendCommandExecution:
    device, coordinator = await get_device_and_coordinator(hass, call)
    return _SendCommandExecution(
        device=device,
        coordinator=coordinator,
        is_alias_resolution=log_send_command_call(
            request.requested_device_id,
            device.serial,
            request.command,
            request.properties_summary,
        ),
    )


async def async_handle_send_command(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: DeviceAndCoordinatorGetter,
    summarize_service_properties: ServicePropertySummarizer,
    log_send_command_call: SendCommandLogger,
    resolve_command_failure_translation_key: CommandFailureTranslationResolver,
    raise_service_error: ServiceErrorRaiser,
    logger: logging.Logger,
    attr_command: str,
    attr_properties: str,
    attr_device_id: str,
) -> SendCommandResult:
    """Handle the send_command service call."""
    request = _build_send_command_request(
        call,
        summarize_service_properties=summarize_service_properties,
        logger=logger,
        attr_command=attr_command,
        attr_properties=attr_properties,
        attr_device_id=attr_device_id,
    )
    execution = await _prepare_send_command_execution(
        hass=hass,
        call=call,
        request=request,
        get_device_and_coordinator=get_device_and_coordinator,
        log_send_command_call=log_send_command_call,
    )
    await async_send_command_with_service_errors(
        execution.coordinator,
        execution.device,
        command=request.command,
        properties=request.properties,
        requested_device_id=request.requested_device_id,
        failure_log=(
            "send_command failed (command=%s, device_id=%s, "
            "resolved_serial=%s, failure=%s)"
        ),
        api_error_log="API error sending command: %s",
        resolve_command_failure_translation_key=resolve_command_failure_translation_key,
        raise_service_error=raise_service_error,
        logger=logger,
    )
    return build_send_command_result(
        execution.device.serial,
        requested_device_id=request.requested_device_id,
        is_alias_resolution=execution.is_alias_resolution,
    )
