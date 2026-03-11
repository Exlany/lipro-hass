"""Command runtime orchestrator for coordinator."""

from __future__ import annotations

from collections import deque
import logging
from typing import TYPE_CHECKING, Any

from ...api import LiproApiError, LiproAuthError, LiproRefreshTokenExpiredError
from ...command.result import (
    apply_missing_msg_sn_failure,
    apply_push_failure,
    apply_successful_command_trace,
    build_command_api_error_failure,
    extract_msg_sn,
    is_command_push_failed,
)
from ...command.trace import build_command_trace, update_trace_with_exception
from ..types import (
    CommandPayload,
    CommandTrace,
    ConnectStatusRefreshSetter,
    DeviceKeyNormalizer,
    ReauthCallback,
)
from .protocols import CommandResult

if TYPE_CHECKING:
    from ...device import LiproDevice
    from .command import (
        CommandBuilder,
        CommandSender,
        ConfirmationManager,
        RetryStrategy,
    )

_LOGGER = logging.getLogger(__name__)
_MAX_TRACES = 100


class CommandRuntime:
    """Orchestrate command execution with builder/sender/confirmation components."""

    def __init__(
        self,
        *,
        builder: CommandBuilder,
        sender: CommandSender,
        retry: RetryStrategy,
        confirmation: ConfirmationManager,
        connect_status_priority_ids: set[str],
        normalize_device_key: DeviceKeyNormalizer,
        force_connect_status_refresh_setter: ConnectStatusRefreshSetter,
        trigger_reauth: ReauthCallback,
        debug_mode: bool = False,
    ) -> None:
        """Initialize with component dependencies."""
        self._builder = builder
        self._sender = sender
        self._retry = retry
        self._confirmation = confirmation
        self._connect_status_priority_ids = connect_status_priority_ids
        self._normalize_device_key = normalize_device_key
        self._force_connect_status_refresh_setter = force_connect_status_refresh_setter
        self._trigger_reauth = trigger_reauth
        self._debug_mode = debug_mode
        self._traces: deque[CommandTrace] = deque(maxlen=_MAX_TRACES)
        self._last_failure: CommandTrace | None = None

    @property
    def last_command_failure(self) -> CommandTrace | None:
        """Get latest command failure."""
        return dict(self._last_failure) if self._last_failure else None

    def _record_trace(self, trace: CommandTrace) -> None:
        """Record trace if debug enabled."""
        if self._debug_mode:
            self._traces.append(trace)

    async def send_command(
        self,
        device_id: str,
        command: CommandPayload,
        *,
        wait_confirmation: bool = True,
        timeout: float = 5.0,
    ) -> CommandResult:
        """Send command (protocol compliance stub)."""
        raise NotImplementedError("Use send_device_command")

    async def send_batch_commands(
        self, commands: list[tuple[str, dict[str, Any]]]
    ) -> list[CommandResult]:
        """Send batch commands (protocol compliance stub)."""
        raise NotImplementedError("Use send_device_command for each")

    async def send_device_command(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        fallback_device_id: str | None,
    ) -> tuple[bool, str]:
        """Send command to device with full flow."""
        trace = build_command_trace(
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
            redact_identifier=lambda x: x,
        )

        try:
            result, route = await self._sender.send_command(
                device=device,
                command=command,
                properties=properties,
                fallback_device_id=fallback_device_id,
                trace=trace,
            )
        except LiproApiError as err:
            return await self._handle_api_error(
                device=device, trace=trace, route="unknown", err=err
            ), "unknown"

        if is_command_push_failed(result):
            self._last_failure = apply_push_failure(
                trace=trace,
                route=route,
                command=command,
                device_name=device.name,
                device_serial=device.serial,
                logger=_LOGGER,
            )
            self._record_trace(trace)
            return False, route

        msg_sn = extract_msg_sn(result)
        if not msg_sn:
            self._last_failure = apply_missing_msg_sn_failure(
                trace=trace,
                route=route,
                command=command,
                device_name=device.name,
                device_serial=device.serial,
                logger=_LOGGER,
            )
            self._record_trace(trace)
            return False, route

        if not await self._verify_delivery(
            trace=trace, route=route, msg_sn=msg_sn, device=device
        ):
            return False, route

        self._finalize_success(
            device=device,
            command=command,
            properties=properties,
            route=route,
            trace=trace,
        )
        return True, route

    async def _verify_delivery(
        self, *, trace: dict[str, Any], route: str, msg_sn: str, device: LiproDevice
    ) -> bool:
        """Verify command delivery via polling."""
        retry_delays = self._retry.build_retry_delays()
        verified, _ = await self._sender.verify_command_delivery(
            msg_sn=msg_sn, retry_delays=retry_delays, trace=trace, device=device
        )
        return verified

    def _finalize_success(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        route: str,
        trace: dict[str, Any],
    ) -> None:
        """Finalize successful command."""
        skip_immediate = self._builder.should_skip_immediate_refresh(
            command=command, properties=properties
        )
        self._confirmation.track_command_expectation(
            device_serial=device.serial, command=command, properties=properties
        )
        if not device.is_group:
            self._connect_status_priority_ids.add(
                self._normalize_device_key(device.serial)
            )
        self._force_connect_status_refresh_setter(True)
        adaptive_delay = self._confirmation.get_adaptive_post_refresh_delay(
            device.serial
        )
        self._confirmation.schedule_post_command_refresh(
            skip_immediate=skip_immediate, device_serial=device.serial
        )
        apply_successful_command_trace(
            trace=trace,
            route=route,
            adaptive_delay_seconds=adaptive_delay,
            skip_immediate_refresh=skip_immediate,
        )
        self._record_trace(trace)
        self._last_failure = None

    async def _handle_api_error(
        self,
        *,
        device: LiproDevice,
        trace: CommandTrace,
        route: str,
        err: LiproApiError,
    ) -> bool:
        """Handle API errors."""
        self._last_failure = build_command_api_error_failure(
            trace=trace,
            route=route,
            device_serial=device.serial,
            err=err,
            update_trace_with_exception=update_trace_with_exception,
        )
        self._record_trace(trace)
        if isinstance(err, LiproRefreshTokenExpiredError | LiproAuthError):
            await self._trigger_reauth(
                "auth_expired"
                if isinstance(err, LiproRefreshTokenExpiredError)
                else "auth_error"
            )
        return False


__all__ = ["CommandRuntime"]
