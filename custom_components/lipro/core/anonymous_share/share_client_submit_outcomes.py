"""Local outcome builders for the anonymous-share submit flow."""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

import aiohttp

from ..telemetry.models import OperationOutcome, build_operation_outcome_from_exception
from ..utils.log_safety import safe_error_placeholder
from .share_client_ports import _SHARE_SUBMIT_ORIGIN, ShareWorkerClientLike
from .share_client_support import (
    ResponseHeadersLike,
    build_http_failure_outcome,
    build_rate_limited_outcome,
    schedule_retry_deadline,
    submit_failure_reason_code,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from logging import Logger


def build_submit_http_failure(
    *,
    label: str,
    logger: Logger,
    last_status: int | None,
) -> OperationOutcome:
    """Translate a terminal HTTP status without a typed branch into the default outcome."""
    logger.warning(
        "%s upload failed with status %s",
        label,
        last_status if last_status is not None else "?",
    )
    return build_http_failure_outcome(
        failure_origin=_SHARE_SUBMIT_ORIGIN,
        http_status=last_status,
        reason_code=submit_failure_reason_code(last_status),
    )


def build_timeout_submit_outcome(
    err: TimeoutError,
    *,
    label: str,
    logger: Logger,
) -> OperationOutcome:
    """Translate one timeout into the canonical retryable submit outcome."""
    logger.warning("%s upload timed out", label)
    return build_operation_outcome_from_exception(
        err,
        kind="failed",
        reason_code="timeout",
        failure_origin=_SHARE_SUBMIT_ORIGIN,
        failure_category="network",
        handling_policy="retry",
    )


def build_client_error_submit_outcome(
    err: aiohttp.ClientError,
    *,
    label: str,
    logger: Logger,
) -> OperationOutcome:
    """Translate one aiohttp client error into the canonical retryable outcome."""
    logger.warning("%s upload failed: %s", label, safe_error_placeholder(err))
    return build_operation_outcome_from_exception(
        err,
        kind="failed",
        reason_code="client_error",
        failure_origin=_SHARE_SUBMIT_ORIGIN,
        failure_category="network",
        handling_policy="retry",
    )


def build_unexpected_submit_outcome(
    err: Exception,
    *,
    label: str,
    logger: Logger,
    reason_code: str,
    failure_category: str,
    handling_policy: str,
) -> OperationOutcome:
    """Translate one unexpected submit exception after redacting its message."""
    with suppress(AttributeError, RuntimeError, TypeError, ValueError):
        err.args = (safe_error_placeholder(err),)
    logger.exception("Unexpected error during %s upload", label.lower())
    return build_operation_outcome_from_exception(
        err,
        kind="failed",
        reason_code=reason_code,
        failure_origin=_SHARE_SUBMIT_ORIGIN,
        failure_category=failure_category,
        handling_policy=handling_policy,
    )


def build_rate_limited_submit_outcome(
    client: ShareWorkerClientLike,
    *,
    headers: ResponseHeadersLike,
    now: Callable[[], float],
) -> OperationOutcome:
    """Project one rate-limited submit response into the canonical outcome."""
    retry_after = client.parse_retry_after(headers)
    retry_deadline = schedule_retry_deadline(retry_after_seconds=retry_after, now=now)
    if retry_deadline is not None:
        client.next_upload_attempt_at = retry_deadline
    return build_rate_limited_outcome(
        failure_origin=_SHARE_SUBMIT_ORIGIN,
        retry_after_seconds=retry_after,
    )
