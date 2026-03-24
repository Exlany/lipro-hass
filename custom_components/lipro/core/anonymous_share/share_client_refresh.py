"""Support-only token-refresh flow helpers for the anonymous-share client."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import aiohttp

from ..telemetry.models import (
    OperationOutcome,
    build_operation_outcome,
    build_operation_outcome_from_exception,
)
from .const import SHARE_TOKEN_REFRESH_URL
from .share_client_ports import _TOKEN_REFRESH_ORIGIN, ShareWorkerClientLike
from .share_client_support import (
    ResponseHeadersLike,
    WorkerResponsePayload,
    backoff_active,
    build_http_failure_outcome,
    build_invalid_refresh_payload_outcome,
    build_rate_limited_outcome,
    build_token_invalid_outcome,
    extract_response_code,
    is_refresh_token_invalid,
    schedule_retry_deadline,
)

if TYPE_CHECKING:
    from logging import Logger


async def refresh_install_token_with_outcome(
    client: ShareWorkerClientLike,
    session: aiohttp.ClientSession,
    *,
    logger: Logger,
    now: Callable[[], float],
) -> OperationOutcome:
    """Refresh the install token via `/api/token/refresh` with typed outcome."""
    del logger
    if not client.install_token:
        return build_operation_outcome(
            kind="skipped", reason_code="missing_install_token"
        )
    if backoff_active(next_upload_attempt_at=client.next_upload_attempt_at, now=now):
        return build_operation_outcome(kind="skipped", reason_code="backoff_active")

    try:
        async with session.post(
            SHARE_TOKEN_REFRESH_URL,
            headers=client.build_upload_headers(install_token=client.install_token),
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            payload = await client.safe_read_json(response)
            return _resolve_refresh_response_outcome(
                client,
                http_status=response.status,
                response_headers=response.headers,
                payload=payload,
                now=now,
            )
    except TimeoutError as err:
        return build_operation_outcome_from_exception(
            err,
            kind="failed",
            reason_code="timeout",
            failure_origin=_TOKEN_REFRESH_ORIGIN,
            failure_category="network",
            handling_policy="retry",
        )
    except aiohttp.ClientError as err:
        return build_operation_outcome_from_exception(
            err,
            kind="failed",
            reason_code="client_error",
            failure_origin=_TOKEN_REFRESH_ORIGIN,
            failure_category="network",
            handling_policy="retry",
        )
    except OSError as err:
        return build_operation_outcome_from_exception(
            err,
            kind="failed",
            reason_code="os_error",
            failure_origin=_TOKEN_REFRESH_ORIGIN,
            failure_category="network",
            handling_policy="retry",
        )
    except ValueError as err:
        return build_operation_outcome_from_exception(
            err,
            kind="failed",
            reason_code="value_error",
            failure_origin=_TOKEN_REFRESH_ORIGIN,
            failure_category="protocol",
            handling_policy="inspect",
        )


def _resolve_refresh_response_outcome(
    client: ShareWorkerClientLike,
    *,
    http_status: int,
    response_headers: ResponseHeadersLike,
    payload: WorkerResponsePayload | None,
    now: Callable[[], float],
) -> OperationOutcome:
    """Resolve one refresh response into the canonical typed outcome."""
    if http_status == 200:
        if payload is not None and client.apply_token_payload(payload):
            return build_operation_outcome(
                kind="success",
                reason_code="refresh_success",
            )
        return build_invalid_refresh_payload_outcome(
            failure_origin=_TOKEN_REFRESH_ORIGIN,
        )

    code = extract_response_code(payload)
    if is_refresh_token_invalid(http_status=http_status, code=code):
        client.clear_install_token()
        return build_token_invalid_outcome(
            failure_origin=_TOKEN_REFRESH_ORIGIN,
        )

    if http_status == 429:
        retry_after = client.parse_retry_after(response_headers)
        retry_deadline = schedule_retry_deadline(
            retry_after_seconds=retry_after,
            now=now,
        )
        if retry_deadline is not None:
            client.next_upload_attempt_at = retry_deadline
        return build_rate_limited_outcome(
            failure_origin=_TOKEN_REFRESH_ORIGIN,
            retry_after_seconds=retry_after,
        )

    return build_http_failure_outcome(
        failure_origin=_TOKEN_REFRESH_ORIGIN,
        http_status=http_status,
    )
