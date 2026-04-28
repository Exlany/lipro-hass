"""Local attempt loop helpers for the anonymous-share submit flow."""

from __future__ import annotations

from collections.abc import Callable

import aiohttp

from ..telemetry.models import OperationOutcome, build_operation_outcome
from .const import SHARE_REPORT_URL
from .share_client_ports import _SHARE_SUBMIT_ORIGIN, ShareWorkerClientLike
from .share_client_submit_outcomes import build_rate_limited_submit_outcome
from .share_client_support import (
    ResponseHeadersLike,
    SubmitVariant,
    WorkerResponsePayload,
    build_invalid_schema_outcome,
    build_token_rejected_outcome,
    extract_response_code,
    is_submit_token_rejected,
)


async def submit_report_variants(
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


def _resolve_retryable_submit_attempt(
    client: ShareWorkerClientLike,
    *,
    submit_variant: SubmitVariant,
    http_status: int,
    response_headers: ResponseHeadersLike,
    now: Callable[[], float],
) -> tuple[OperationOutcome | None, bool] | None:
    """Resolve retry-oriented submit branches for one attempt."""
    if http_status == 429:
        return (
            build_rate_limited_submit_outcome(
                client,
                headers=response_headers,
                now=now,
            ),
            False,
        )
    if http_status == 413 and submit_variant.fallback_on_payload_too_large:
        return None, True
    return None


def _resolve_submit_token_rejection(
    client: ShareWorkerClientLike,
    *,
    token: str | None,
    http_status: int,
    code: object,
) -> tuple[OperationOutcome | None, bool] | None:
    """Resolve token-rejection branches for one submit attempt."""
    if not is_submit_token_rejected(http_status=http_status, code=code):
        return None
    if token:
        client.clear_install_token()
        return None, False
    return (
        build_token_rejected_outcome(
            failure_origin=_SHARE_SUBMIT_ORIGIN,
        ),
        False,
    )


def _resolve_invalid_schema_submit_attempt(
    *,
    http_status: int,
    code: object,
) -> tuple[OperationOutcome, bool] | None:
    """Resolve the invalid-schema terminal branch for one submit attempt."""
    if http_status != 400 or code != "INVALID_SCHEMA":
        return None
    return (
        build_invalid_schema_outcome(
            failure_origin=_SHARE_SUBMIT_ORIGIN,
        ),
        False,
    )


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
    retryable_result = _resolve_retryable_submit_attempt(
        client,
        submit_variant=submit_variant,
        http_status=http_status,
        response_headers=response_headers,
        now=now,
    )
    if retryable_result is not None:
        return retryable_result

    token_rejection_result = _resolve_submit_token_rejection(
        client,
        token=token,
        http_status=http_status,
        code=code,
    )
    if token_rejection_result is not None:
        return token_rejection_result

    invalid_schema_result = _resolve_invalid_schema_submit_attempt(
        http_status=http_status,
        code=code,
    )
    if invalid_schema_result is not None:
        return invalid_schema_result

    return None, False
