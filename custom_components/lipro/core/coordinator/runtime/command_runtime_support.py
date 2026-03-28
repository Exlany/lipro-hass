"""Internal request and failure helpers for the command runtime."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Literal, cast

from ...command.result import (
    COMMAND_FAILURE_REASON_COMMAND_RESULT_FAILED,
    COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED,
    CommandFailurePayload,
    apply_missing_msg_sn_failure,
    apply_push_failure,
)
from ..types import CommandFailureSummary, CommandReauthReason, CommandTrace

if TYPE_CHECKING:
    from ...device import LiproDevice

type CommandProperties = list[dict[str, str]] | None


@dataclass(frozen=True, slots=True)
class _CommandRequest:
    """Immutable request context shared across command-runtime stages."""

    device: LiproDevice
    command: str
    properties: CommandProperties
    fallback_device_id: str | None


def _coerce_error_type(trace: CommandTrace) -> str | None:
    value = trace.get('error')
    return value if isinstance(value, str) and value else None


def _copy_summary(
    summary: CommandFailureSummary | None,
) -> CommandFailureSummary | None:
    return cast(CommandFailureSummary, dict(summary)) if summary else None


def _command_result_failure_details(
    command_result_state: str | None,
) -> tuple[
    Literal['command_result_failed', 'command_result_unconfirmed'],
    Literal['CommandResultRejected', 'CommandResultUnconfirmed'],
]:
    """Return canonical failure metadata for one verification outcome."""
    if command_result_state == 'failed':
        return (
            COMMAND_FAILURE_REASON_COMMAND_RESULT_FAILED,
            'CommandResultRejected',
        )
    return (
        COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED,
        'CommandResultUnconfirmed',
    )


def _build_failure_summary(
    *,
    failure: CommandFailurePayload,
    error_type: str | None,
    reauth_reason: CommandReauthReason | None = None,
) -> CommandFailureSummary:
    summary: CommandFailureSummary = {}

    for key in ('reason', 'route', 'device_id', 'message'):
        value = failure.get(key)
        if isinstance(value, str) and value:
            summary[key] = value

    code = failure.get('code')
    if isinstance(code, (int, str)) and not isinstance(code, bool):
        summary['code'] = code

    if error_type is not None:
        summary['error_type'] = error_type

    if reauth_reason is not None:
        summary['reauth_reason'] = reauth_reason
        summary['failure_category'] = 'auth'
    elif error_type is not None or summary:
        summary['failure_category'] = 'protocol'

    return summary


def _build_push_delivery_failure(
    *,
    request: _CommandRequest,
    trace: CommandTrace,
    route: str,
    logger: logging.Logger,
) -> CommandFailurePayload:
    """Build the canonical push-failure payload for one dispatch attempt."""
    return apply_push_failure(
        trace=trace,
        route=route,
        command=request.command,
        device_name=request.device.name,
        device_serial=request.device.serial,
        logger=logger,
    )


def _build_missing_msg_sn_failure(
    *,
    request: _CommandRequest,
    trace: CommandTrace,
    route: str,
    logger: logging.Logger,
) -> CommandFailurePayload:
    """Build the canonical missing-msgSn payload for one dispatch attempt."""
    return apply_missing_msg_sn_failure(
        trace=trace,
        route=route,
        command=request.command,
        device_name=request.device.name,
        device_serial=request.device.serial,
        logger=logger,
    )


__all__ = [
    'CommandProperties',
    '_CommandRequest',
    '_build_failure_summary',
    '_build_missing_msg_sn_failure',
    '_build_push_delivery_failure',
    '_coerce_error_type',
    '_command_result_failure_details',
    '_copy_summary',
]
