"""Command runtime orchestrator for coordinator."""

from __future__ import annotations

from collections import deque
import logging
from typing import TYPE_CHECKING, Any, cast

from ...api import LiproApiError, LiproAuthError, LiproRefreshTokenExpiredError
from ...command.result import (
    COMMAND_FAILURE_REASON_COMMAND_RESULT_FAILED,
    COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED,
    CommandFailurePayload,
    apply_missing_msg_sn_failure,
    apply_push_failure,
    apply_successful_command_trace,
    build_command_api_error_failure,
    extract_msg_sn,
    is_command_push_failed,
)
from ...command.trace import build_command_trace, update_trace_with_exception
from ..types import (
    CommandFailureSummary,
    CommandReauthReason,
    CommandTrace,
    ReauthCallback,
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


def _coerce_error_type(trace: CommandTrace) -> str | None:
    value = trace.get("error")
    return value if isinstance(value, str) and value else None


def _copy_summary(
    summary: CommandFailureSummary | None,
) -> CommandFailureSummary | None:
    return cast(CommandFailureSummary, dict(summary)) if summary else None


def _build_failure_summary(
    *,
    failure: CommandFailurePayload,
    error_type: str | None,
    reauth_reason: CommandReauthReason | None = None,
) -> CommandFailureSummary:
    summary: CommandFailureSummary = {}

    for key in ("reason", "route", "device_id", "message"):
        value = failure.get(key)
        if isinstance(value, str) and value:
            summary[key] = value

    code = failure.get("code")
    if isinstance(code, (int, str)) and not isinstance(code, bool):
        summary["code"] = code

    if error_type is not None:
        summary["error_type"] = error_type

    if reauth_reason is not None:
        summary["reauth_reason"] = reauth_reason
        summary["failure_category"] = "auth"
    elif error_type is not None or summary:
        summary["failure_category"] = "protocol"

    return summary


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
        debug_mode: bool = False,
    ) -> None:
        """Initialize with component dependencies."""
        self._builder = builder
        self._sender = sender
        self._retry = retry
        self._confirmation = confirmation
        self._trigger_reauth = trigger_reauth
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

    def get_runtime_metrics(self) -> dict[str, Any]:
        """Return lightweight command-runtime telemetry."""
        confirmation_metrics_getter = getattr(
            self._confirmation, "get_runtime_metrics", None
        )
        confirmation_metrics = (
            confirmation_metrics_getter()
            if callable(confirmation_metrics_getter)
            else {}
        )
        if not isinstance(confirmation_metrics, dict):
            confirmation_metrics = {}
        return {
            "debug_enabled": self._debug_mode,
            "trace_count": len(self._traces),
            "last_failure": self.last_command_failure_summary,
            "confirmation": confirmation_metrics,
        }

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
        properties: dict[str, Any],
    ) -> dict[str, Any]:
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
        properties: dict[str, Any],
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
        properties: list[dict[str, str]] | None,
        fallback_device_id: str | None,
    ) -> tuple[bool, str]:
        """Send command to device with full flow."""
        success, route, _trace = await self._execute_device_command(
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
        )
        return success, route

    async def _execute_device_command(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        fallback_device_id: str | None,
    ) -> tuple[bool, str, CommandTrace]:
        """Execute the shared command flow and return trace for all callers."""
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
            return (
                await self._handle_api_error(
                    device=device, trace=trace, route="unknown", err=err
                ),
                "unknown",
                trace,
            )

        if is_command_push_failed(result):
            failure = apply_push_failure(
                trace=trace,
                route=route,
                command=command,
                device_name=device.name,
                device_serial=device.serial,
                logger=_LOGGER,
            )
            self._record_failure(
                trace=trace,
                failure=failure,
                error_type=_coerce_error_type(trace),
            )
            return False, route, trace

        msg_sn = extract_msg_sn(result)
        if not msg_sn:
            failure = apply_missing_msg_sn_failure(
                trace=trace,
                route=route,
                command=command,
                device_name=device.name,
                device_serial=device.serial,
                logger=_LOGGER,
            )
            self._record_failure(
                trace=trace,
                failure=failure,
                error_type=_coerce_error_type(trace),
            )
            return False, route, trace

        verified, _failure_summary = await self._verify_delivery(
            trace=trace,
            route=route,
            msg_sn=msg_sn,
            device=device,
        )
        if not verified:
            return False, route, trace

        self._finalize_success(
            device=device,
            command=command,
            properties=properties,
            route=route,
            trace=trace,
        )
        return True, route, trace

    async def _verify_delivery(
        self,
        *,
        trace: CommandTrace,
        route: str,
        msg_sn: str,
        device: LiproDevice,
    ) -> tuple[bool, CommandFailureSummary | None]:
        """Verify command delivery via polling and normalize non-success outcomes."""
        retry_delays = self._retry.build_retry_delays()
        verified, command_result_state = await self._sender.verify_command_delivery(
            msg_sn=msg_sn,
            retry_delays=retry_delays,
            trace=trace,
            device=device,
        )
        if verified:
            return True, None

        trace["route"] = route
        trace["success"] = False
        if command_result_state == "failed":
            trace["error"] = "CommandResultRejected"
            trace["error_message"] = COMMAND_FAILURE_REASON_COMMAND_RESULT_FAILED
            return False, self._record_failure(
                trace=trace,
                failure={
                    "reason": COMMAND_FAILURE_REASON_COMMAND_RESULT_FAILED,
                    "code": COMMAND_FAILURE_REASON_COMMAND_RESULT_FAILED,
                    "route": route,
                    "device_id": device.serial,
                },
                error_type="CommandResultRejected",
            )

        trace["error"] = "CommandResultUnconfirmed"
        trace["error_message"] = COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED
        return False, self._record_failure(
            trace=trace,
            failure={
                "reason": COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED,
                "code": COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED,
                "route": route,
                "device_id": device.serial,
            },
            error_type="CommandResultUnconfirmed",
        )

    def _finalize_success(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        route: str,
        trace: CommandTrace,
    ) -> None:
        """Finalize successful command."""
        skip_immediate = self._builder.should_skip_immediate_refresh(
            command=command, properties=properties
        )
        self._confirmation.track_command_expectation(
            device_serial=device.serial, command=command, properties=properties
        )
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
        self._last_failure_summary = None

    async def _handle_api_error(
        self,
        *,
        device: LiproDevice,
        trace: CommandTrace,
        route: str,
        err: LiproApiError,
    ) -> bool:
        """Handle API errors."""
        failure = build_command_api_error_failure(
            trace=trace,
            route=route,
            device_serial=device.serial,
            err=err,
            update_trace_with_exception=update_trace_with_exception,
        )
        reauth_reason: CommandReauthReason | None = None
        if isinstance(err, LiproRefreshTokenExpiredError):
            reauth_reason = "auth_expired"
        elif isinstance(err, LiproAuthError):
            reauth_reason = "auth_error"

        self._record_failure(
            trace=trace,
            failure=failure,
            error_type=type(err).__name__,
            reauth_reason=reauth_reason,
        )
        if reauth_reason is not None:
            await self._trigger_reauth(reauth_reason)
        return False


__all__ = ["CommandRuntime"]
