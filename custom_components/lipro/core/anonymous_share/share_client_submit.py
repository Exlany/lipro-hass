"""Support-only submit flow helpers for the anonymous-share client."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import TYPE_CHECKING

import aiohttp

from ..telemetry.models import (
    OperationOutcome,
    build_operation_outcome,
    build_operation_outcome_from_exception,
)
from ..utils.log_safety import safe_error_placeholder
from .const import SHARE_REPORT_URL
from .share_client_ports import _SHARE_SUBMIT_ORIGIN, ShareWorkerClientLike
from .share_client_support import (
    ResponseHeadersLike,
    SharePayload,
    SubmitVariant,
    WorkerResponsePayload,
    backoff_active,
    build_http_failure_outcome,
    build_invalid_schema_outcome,
    build_rate_limited_outcome,
    build_submit_variants,
    build_token_rejected_outcome,
    extract_response_code,
    has_valid_installation_id,
    is_submit_token_rejected,
    refresh_due,
    schedule_retry_deadline,
    submit_failure_reason_code,
)

if TYPE_CHECKING:
    from logging import Logger


async def submit_share_payload_with_outcome(
    client: ShareWorkerClientLike,
    session: aiohttp.ClientSession,
    report: SharePayload,
    *,
    label: str,
    ensure_loaded: Callable[[], Awaitable[None]],
    logger: Logger,
    now: Callable[[], float],
    build_lite_variant: Callable[[SharePayload], SharePayload],
) -> OperationOutcome:
    """Submit one payload to the share endpoint with typed failure semantics."""
    preflight_outcome = await _preflight_submit_share_payload(
        client,
        report,
        label=label,
        ensure_loaded=ensure_loaded,
        logger=logger,
        now=now,
    )
    if preflight_outcome is not None:
        return preflight_outcome

    refresh_outcome = await _refresh_submit_token_if_due(client, session, now=now)
    if refresh_outcome is not None:
        return refresh_outcome

    return await _submit_share_report_variants(
        client,
        session,
        report,
        label=label,
        logger=logger,
        now=now,
        build_lite_variant=build_lite_variant,
    )


async def _submit_share_report_variants(
    client: ShareWorkerClientLike,
    session: aiohttp.ClientSession,
    report: SharePayload,
    *,
    label: str,
    logger: Logger,
    now: Callable[[], float],
    build_lite_variant: Callable[[SharePayload], SharePayload],
) -> OperationOutcome:
    """Submit all share payload variants while preserving typed terminal outcomes."""
    try:
        submit_variants = build_submit_variants(
            report,
            install_token=client.install_token,
            build_lite_variant=build_lite_variant,
        )
        outcome, last_status = await _submit_report_variants(
            client,
            session,
            submit_variants=submit_variants,
            now=now,
        )
        if outcome is not None:
            return outcome
        return _build_submit_http_failure(label=label, logger=logger, last_status=last_status)
    except TimeoutError as err:
        return _build_timeout_submit_outcome(err, label=label, logger=logger)
    except aiohttp.ClientError as err:
        return _build_client_error_submit_outcome(err, label=label, logger=logger)
    except OSError as err:
        return _build_unexpected_submit_outcome(
            err,
            label=label,
            logger=logger,
            reason_code="os_error",
            failure_category="network",
            handling_policy="retry",
        )
    except ValueError as err:
        return _build_unexpected_submit_outcome(
            err,
            label=label,
            logger=logger,
            reason_code="value_error",
            failure_category="protocol",
            handling_policy="inspect",
        )


def _build_submit_http_failure(
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


def _build_timeout_submit_outcome(
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


def _build_client_error_submit_outcome(
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


def _build_unexpected_submit_outcome(
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


async def _preflight_submit_share_payload(
    client: ShareWorkerClientLike,
    report: SharePayload,
    *,
    label: str,
    ensure_loaded: Callable[[], Awaitable[None]],
    logger: Logger,
    now: Callable[[], float],
) -> OperationOutcome | None:
    """Run the shared preflight checks before the submit attempt loop."""
    await ensure_loaded()

    if backoff_active(next_upload_attempt_at=client.next_upload_attempt_at, now=now):
        return build_operation_outcome(kind="skipped", reason_code="backoff_active")

    if has_valid_installation_id(report):
        return None

    logger.warning("%s upload skipped: missing installation_id", label)
    return build_operation_outcome(
        kind="failed",
        reason_code="missing_installation_id",
        failure_origin=_SHARE_SUBMIT_ORIGIN,
        error_type="MissingInstallationId",
        failure_category="protocol",
        handling_policy="inspect",
    )


async def _refresh_submit_token_if_due(
    client: ShareWorkerClientLike,
    session: aiohttp.ClientSession,
    *,
    now: Callable[[], float],
) -> OperationOutcome | None:
    """Refresh the install token when the cached schedule says it is due."""
    if not refresh_due(
        install_token=client.install_token,
        token_refresh_after=client.token_refresh_after,
        token_expires_at=client.token_expires_at,
        now_seconds=int(now()),
    ):
        return None

    refresh_outcome = await client.refresh_install_token_with_outcome(session)
    if refresh_outcome.is_success:
        return None
    return refresh_outcome


async def _submit_report_variants(
    client: ShareWorkerClientLike,
    session: aiohttp.ClientSession,
    *,
    submit_variants: tuple[SubmitVariant, ...],
    now: Callable[[], float],
) -> tuple[OperationOutcome | None, int | None]:
    """Submit all report variants until one returns a terminal outcome."""
    last_status: int | None = None
    for submit_variant in submit_variants:
        outcome, last_status = await _submit_one_variant(
            client,
            session,
            submit_variant=submit_variant,
            now=now,
        )
        if outcome is not None:
            return outcome, last_status
    return None, last_status


async def _submit_one_variant(
    client: ShareWorkerClientLike,
    session: aiohttp.ClientSession,
    *,
    submit_variant: SubmitVariant,
    now: Callable[[], float],
) -> tuple[OperationOutcome | None, int | None]:
    """Submit one variant across its token attempts until a terminal outcome emerges."""
    last_status: int | None = None
    for token in submit_variant.token_attempts:
        last_status, response_headers, payload = await _submit_variant_token_attempt(
            client,
            session,
            submit_variant=submit_variant,
            token=token,
        )
        outcome, advance_to_next_variant = _resolve_submit_attempt_outcome(
            client,
            submit_variant=submit_variant,
            token=token,
            http_status=last_status,
            response_headers=response_headers,
            payload=payload,
            now=now,
        )
        if outcome is not None:
            return outcome, last_status
        if advance_to_next_variant:
            break
    return None, last_status


async def _submit_variant_token_attempt(
    client: ShareWorkerClientLike,
    session: aiohttp.ClientSession,
    *,
    submit_variant: SubmitVariant,
    token: str | None,
) -> tuple[int, ResponseHeadersLike, WorkerResponsePayload | None]:
    """Submit one payload/token attempt and return the raw HTTP result."""
    async with session.post(
        SHARE_REPORT_URL,
        json=submit_variant.payload,
        headers=client.build_upload_headers(install_token=token),
        timeout=aiohttp.ClientTimeout(total=30),
    ) as response:
        payload = await client.safe_read_json(response)
        return response.status, response.headers, payload


def _resolve_submit_attempt_outcome(
    client: ShareWorkerClientLike,
    *,
    submit_variant: SubmitVariant,
    token: str | None,
    http_status: int,
    response_headers: ResponseHeadersLike,
    payload: WorkerResponsePayload | None,
    now: Callable[[], float],
) -> tuple[OperationOutcome | None, bool]:
    """Resolve one submit attempt into an outcome or loop-control decision."""
    if http_status == 200:
        if payload:
            client.apply_token_payload(payload)
        return (
            build_operation_outcome(
                kind="success",
                reason_code=submit_variant.success_reason_code,
            ),
            False,
        )

    code = extract_response_code(payload)
    if http_status == 429:
        return (
            _build_rate_limited_submit_outcome(
                client,
                headers=response_headers,
                now=now,
            ),
            False,
        )

    if http_status == 413 and submit_variant.fallback_on_payload_too_large:
        return None, True

    if is_submit_token_rejected(http_status=http_status, code=code):
        if token:
            client.clear_install_token()
            return None, False
        return (
            build_token_rejected_outcome(
                failure_origin=_SHARE_SUBMIT_ORIGIN,
            ),
            False,
        )

    if http_status == 400 and code == "INVALID_SCHEMA":
        return (
            build_invalid_schema_outcome(
                failure_origin=_SHARE_SUBMIT_ORIGIN,
            ),
            False,
        )

    return None, False


def _build_rate_limited_submit_outcome(
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
