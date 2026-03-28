"""Localized outcome helpers for ``CommandRuntime``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol

from ...api import LiproApiError, LiproAuthError, LiproRefreshTokenExpiredError
from ...command.result import (
    CommandFailurePayload,
    apply_successful_command_trace,
    build_command_api_error_failure,
)
from ...command.trace import update_trace_with_exception
from ..types import (
    CommandFailureSummary,
    CommandReauthReason,
    CommandTrace,
    ReauthCallback,
)
from .command_runtime_support import _CommandRequest

if TYPE_CHECKING:
    from .command import CommandBuilder, ConfirmationManager


class RecordFailureCallback(Protocol):
    """Persist one normalized failure summary through the owning runtime."""

    def __call__(
        self,
        *,
        trace: CommandTrace,
        failure: CommandFailurePayload,
        error_type: str | None,
        reauth_reason: CommandReauthReason | None = None,
    ) -> CommandFailureSummary: ...


class RecordTraceCallback(Protocol):
    """Record one trace through the owning runtime."""

    def __call__(self, trace: CommandTrace) -> None: ...


class ClearFailureStateCallback(Protocol):
    """Clear the owning runtime's last-failure snapshot."""

    def __call__(self) -> None: ...


def _record_command_result_failure(
    *,
    trace: CommandTrace,
    route: str,
    device_serial: str,
    reason: Literal['command_result_failed', 'command_result_unconfirmed'],
    error_type: Literal['CommandResultRejected', 'CommandResultUnconfirmed'],
    record_failure: RecordFailureCallback,
) -> CommandFailureSummary:
    """Record one normalized command-result verification failure."""
    trace['route'] = route
    trace['success'] = False
    trace['error'] = error_type
    trace['error_message'] = reason
    return record_failure(
        trace=trace,
        failure={
            'reason': reason,
            'code': reason,
            'route': route,
            'device_id': device_serial,
        },
        error_type=error_type,
    )


def _finalize_success(
    *,
    request: _CommandRequest,
    route: str,
    trace: CommandTrace,
    builder: CommandBuilder,
    confirmation: ConfirmationManager,
    record_trace: RecordTraceCallback,
    clear_failure_state: ClearFailureStateCallback,
) -> None:
    """Apply success bookkeeping for one confirmed command."""
    skip_immediate = builder.should_skip_immediate_refresh(
        command=request.command,
        properties=request.properties,
    )
    confirmation.track_command_expectation(
        device_serial=request.device.serial,
        command=request.command,
        properties=request.properties,
    )
    adaptive_delay = confirmation.get_adaptive_post_refresh_delay(
        request.device.serial,
    )
    confirmation.schedule_post_command_refresh(
        skip_immediate=skip_immediate,
        device_serial=request.device.serial,
    )
    apply_successful_command_trace(
        trace=trace,
        route=route,
        adaptive_delay_seconds=adaptive_delay,
        skip_immediate_refresh=skip_immediate,
    )
    record_trace(trace)
    clear_failure_state()


def _resolve_reauth_reason(err: LiproApiError) -> CommandReauthReason | None:
    """Resolve the re-auth trigger reason for one API error."""
    if isinstance(err, LiproRefreshTokenExpiredError):
        return 'auth_expired'
    if isinstance(err, LiproAuthError):
        return 'auth_error'
    return None


async def _handle_api_error(
    *,
    request: _CommandRequest,
    trace: CommandTrace,
    route: str,
    err: LiproApiError,
    record_failure: RecordFailureCallback,
    trigger_reauth: ReauthCallback,
) -> None:
    """Normalize one API error and trigger re-auth when needed."""
    failure = build_command_api_error_failure(
        trace=trace,
        route=route,
        device_serial=request.device.serial,
        err=err,
        update_trace_with_exception=update_trace_with_exception,
    )
    reauth_reason = _resolve_reauth_reason(err)
    record_failure(
        trace=trace,
        failure=failure,
        error_type=type(err).__name__,
        reauth_reason=reauth_reason,
    )
    if reauth_reason is not None:
        await trigger_reauth(reauth_reason)


__all__ = [
    '_finalize_success',
    '_handle_api_error',
    '_record_command_result_failure',
    '_resolve_reauth_reason',
]
