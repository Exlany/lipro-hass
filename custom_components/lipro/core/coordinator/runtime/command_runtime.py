"""Command runtime orchestrator for coordinator."""

from __future__ import annotations

from collections import deque
import logging
from typing import TYPE_CHECKING, cast

from ...command.dispatch import CommandRoute
from ...command.result import CommandFailurePayload
from ...utils.redaction import redact_identifier as _redact_identifier
from ..types import (
    CommandFailureSummary,
    CommandReauthReason,
    CommandTrace,
    PropertyDict,
    ReauthCallback,
    RuntimeMetrics,
)
from .command.sender import CommandDispatchApiError
from .command_runtime_outcome_support import (
    _finalize_success as _finalize_success_support,
    _handle_api_error as _handle_api_error_support,
    _verify_delivery as _verify_delivery_support,
)
from .command_runtime_support import (
    CommandProperties,
    IdentifierRedactor,
    _build_failure_summary,
    _build_request_trace,
    _build_runtime_metrics,
    _CommandRequest,
    _copy_summary,
    _handle_command_dispatch_result as _handle_command_dispatch_result_support,
)

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
        trigger_reauth: ReauthCallback,
        redact_identifier: IdentifierRedactor = _redact_identifier,
        debug_mode: bool = False,
    ) -> None:
        """Initialize with component dependencies."""
        self._builder = builder
        self._sender = sender
        self._retry = retry
        self._confirmation = confirmation
        self._trigger_reauth = trigger_reauth
        self._redact_identifier = redact_identifier
        self._debug_mode = debug_mode
        self._traces: deque[CommandTrace] = deque(maxlen=_MAX_TRACES)
        self._last_failure: CommandTrace | None = None
        self._last_failure_summary: CommandFailureSummary | None = None

    @property
    def last_command_failure(self) -> CommandTrace | None:
        """Get latest command failure trace."""
        return dict(self._last_failure) if self._last_failure else None

    @property
    def last_command_failure_summary(self) -> CommandFailureSummary | None:
        """Get latest normalized command failure summary."""
        return _copy_summary(self._last_failure_summary)

    def get_recent_traces(self, *, limit: int | None = None) -> list[CommandTrace]:
        """Return recent command traces in newest-first order."""
        traces = [dict(trace) for trace in reversed(self._traces)]
        if limit is None or limit >= len(traces):
            return traces
        return traces[:limit]

    def get_runtime_metrics(self) -> RuntimeMetrics:
        """Return lightweight command-runtime telemetry."""
        return _build_runtime_metrics(
            debug_enabled=self._debug_mode,
            trace_count=len(self._traces),
            last_failure=self._last_failure_summary,
            confirmation_metrics=self._confirmation.get_runtime_metrics(),
        )

    def _record_trace(self, trace: CommandTrace) -> None:
        """Record trace if debug enabled."""
        if self._debug_mode:
            self._traces.append(trace)

    def _record_failure(
        self,
        *,
        trace: CommandTrace,
        failure: CommandFailurePayload,
        error_type: str | None,
        reauth_reason: CommandReauthReason | None = None,
    ) -> CommandFailureSummary:
        """Persist the latest failure trace plus a normalized consumer summary."""
        summary = _build_failure_summary(
            failure=failure,
            error_type=error_type,
            reauth_reason=reauth_reason,
        )
        self._last_failure = trace
        self._last_failure_summary = summary
        self._record_trace(trace)
        return cast(CommandFailureSummary, dict(summary))

    def filter_pending_state_properties(
        self,
        *,
        device_serial: str,
        properties: PropertyDict,
    ) -> PropertyDict:
        """Filter stale property values while waiting for command confirmation."""
        filtered, _blocked_keys = self._confirmation.filter_pending_command_mismatches(
            device_serial=device_serial,
            properties=properties,
        )
        return filtered

    def observe_state_confirmation(
        self,
        *,
        device_serial: str,
        properties: PropertyDict,
    ) -> float | None:
        """Learn confirmation latency from incoming device state updates."""
        return self._confirmation.observe_command_confirmation(
            device_serial=device_serial,
            properties=properties,
        )

    async def send_device_command(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: CommandProperties,
        fallback_device_id: str | None,
    ) -> tuple[bool, CommandRoute]:
        """Send command to device with full flow."""
        request = _CommandRequest(
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
        )
        success, route, _trace = await self._execute_device_command(request=request)
        return success, route

    def _build_trace_for_request(self, request: _CommandRequest) -> CommandTrace:
        """Build the canonical command trace for one request."""
        return _build_request_trace(
            request=request,
            redact_identifier=self._redact_identifier,
        )

    def _handle_command_dispatch_result(
        self,
        *,
        request: _CommandRequest,
        result: object,
        trace: CommandTrace,
        route: CommandRoute,
    ) -> str | None:
        """Validate the dispatch-stage result and return its message serial number."""
        return _handle_command_dispatch_result_support(
            request=request,
            result=result,
            trace=trace,
            route=route,
            logger=_LOGGER,
            record_failure=self._record_failure,
        )

    async def _verify_delivery_and_finalize(
        self,
        *,
        request: _CommandRequest,
        trace: CommandTrace,
        route: CommandRoute,
        msg_sn: str,
    ) -> bool:
        """Verify delivery, then finalize success bookkeeping when confirmed."""
        verified = await self._verify_delivery(
            trace=trace,
            route=route,
            msg_sn=msg_sn,
            device=request.device,
        )
        if not verified:
            return False
        _finalize_success_support(
            request=request,
            route=route,
            trace=trace,
            builder=self._builder,
            confirmation=self._confirmation,
            record_trace=self._record_trace,
            clear_failure_state=self._clear_failure_state,
        )
        return True

    async def _send_command_with_trace(
        self,
        *,
        request: _CommandRequest,
        trace: CommandTrace,
    ) -> tuple[object | None, CommandRoute]:
        """Send one command and normalize API errors into the shared failure path."""
        try:
            return await self._sender.send_command(
                device=request.device,
                command=request.command,
                properties=request.properties,
                fallback_device_id=request.fallback_device_id,
                trace=trace,
            )
        except CommandDispatchApiError as err:
            await _handle_api_error_support(
                request=request,
                trace=trace,
                route=err.route,
                err=err.error,
                record_failure=self._record_failure,
                trigger_reauth=self._trigger_reauth,
            )
            return None, err.route

    async def _execute_device_command(
        self,
        *,
        request: _CommandRequest,
    ) -> tuple[bool, CommandRoute, CommandTrace]:
        """Execute the shared command flow and return trace for all callers."""
        trace = self._build_trace_for_request(request)
        result, route = await self._send_command_with_trace(
            request=request,
            trace=trace,
        )
        if result is None:
            return False, route, trace

        msg_sn = self._handle_command_dispatch_result(
            request=request,
            result=result,
            trace=trace,
            route=route,
        )
        if msg_sn is None:
            return False, route, trace
        if not await self._verify_delivery_and_finalize(
            request=request,
            trace=trace,
            route=route,
            msg_sn=msg_sn,
        ):
            return False, route, trace
        return True, route, trace

    async def _verify_delivery(
        self,
        *,
        trace: CommandTrace,
        route: CommandRoute,
        msg_sn: str,
        device: LiproDevice,
    ) -> bool:
        """Verify command delivery via polling and normalize non-success outcomes."""
        return await _verify_delivery_support(
            trace=trace,
            route=route,
            msg_sn=msg_sn,
            device=device,
            sender=self._sender,
            retry=self._retry,
            record_failure=self._record_failure,
        )

    def _clear_failure_state(self) -> None:
        """Clear the latest failure snapshot after a successful command."""
        self._last_failure = None
        self._last_failure_summary = None


__all__ = ["CommandRuntime"]
