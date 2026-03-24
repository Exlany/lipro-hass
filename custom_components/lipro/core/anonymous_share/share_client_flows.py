"""Internal token-refresh and submit-flow helpers for the share worker client."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from contextlib import suppress
import json
from typing import TYPE_CHECKING, Protocol

import aiohttp

from ..telemetry.models import (
    OperationOutcome,
    build_operation_outcome,
    build_operation_outcome_from_exception,
)
from ..utils.log_safety import safe_error_placeholder
from .const import SHARE_REPORT_URL, SHARE_TOKEN_REFRESH_URL
from .share_client_support import (
    JsonReadableResponse,
    ResponseHeadersLike,
    SharePayload,
    SubmitVariant,
    WorkerResponsePayload,
    backoff_active,
    build_http_failure_outcome,
    build_invalid_refresh_payload_outcome,
    build_invalid_schema_outcome,
    build_rate_limited_outcome,
    build_submit_variants,
    build_token_invalid_outcome,
    build_token_rejected_outcome,
    extract_response_code,
    has_valid_installation_id,
    is_refresh_token_invalid,
    is_submit_token_rejected,
    refresh_due,
    schedule_retry_deadline,
    submit_failure_reason_code,
)

if TYPE_CHECKING:
    from logging import Logger


class ShareWorkerClientLike(Protocol):
    """Share-client surface consumed by token-refresh and submit flows."""

    install_token: str | None
    token_expires_at: int
    token_refresh_after: int
    next_upload_attempt_at: float

    def build_upload_headers(
        self,
        *,
        install_token: str | None = None,
    ) -> dict[str, str]:
        """Build request headers for one upload attempt."""

    def parse_retry_after(self, headers: object) -> float | None:
        """Parse Retry-After seconds from one response header bag."""

    def clear_install_token(self) -> None:
        """Clear cached install-token state."""

    def apply_token_payload(self, payload: WorkerResponsePayload) -> bool:
        """Apply one token payload to the client cache."""

    async def safe_read_json(
        self,
        response: JsonReadableResponse,
    ) -> WorkerResponsePayload | None:
        """Best-effort response JSON parsing."""

    async def refresh_install_token(
        self,
        session: aiohttp.ClientSession,
    ) -> bool:
        """Refresh the install token when the submit flow requests it."""

    async def refresh_install_token_with_outcome(
        self,
        session: aiohttp.ClientSession,
    ) -> OperationOutcome:
        """Refresh the install token when the submit flow needs typed feedback."""


_TOKEN_REFRESH_ORIGIN = "anonymous_share.refresh_install_token"
_SHARE_SUBMIT_ORIGIN = "anonymous_share.submit_share_payload"


async def safe_read_json(
    response: JsonReadableResponse,
) -> WorkerResponsePayload | None:
    """Best-effort JSON parsing for Worker responses."""
    try:
        json_reader = getattr(response, "json", None)
        if not callable(json_reader):
            return None
        result = response.json(content_type=None)
        if isinstance(result, Awaitable):
            data = await result
        else:
            data = result
    except (
        AttributeError,
        aiohttp.ContentTypeError,
        json.JSONDecodeError,
        ValueError,
    ):
        return None
    return data if isinstance(data, dict) else None


async def refresh_install_token_with_outcome(
    client: ShareWorkerClientLike,
    session: aiohttp.ClientSession,
    *,
    logger: Logger,
    now: Callable[[], float],
) -> OperationOutcome:
    """Refresh the install token via `/api/token/refresh` with typed outcome."""
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
    except TimeoutError as err:
        logger.warning("%s upload timed out", label)
        return build_operation_outcome_from_exception(
            err,
            kind="failed",
            reason_code="timeout",
            failure_origin=_SHARE_SUBMIT_ORIGIN,
            failure_category="network",
            handling_policy="retry",
        )
    except aiohttp.ClientError as err:
        logger.warning("%s upload failed: %s", label, safe_error_placeholder(err))
        return build_operation_outcome_from_exception(
            err,
            kind="failed",
            reason_code="client_error",
            failure_origin=_SHARE_SUBMIT_ORIGIN,
            failure_category="network",
            handling_policy="retry",
        )
    except OSError as err:
        with suppress(AttributeError, RuntimeError, TypeError, ValueError):
            err.args = (safe_error_placeholder(err),)
        logger.exception("Unexpected error during %s upload", label.lower())
        return build_operation_outcome_from_exception(
            err,
            kind="failed",
            reason_code="os_error",
            failure_origin=_SHARE_SUBMIT_ORIGIN,
            failure_category="network",
            handling_policy="retry",
        )
    except ValueError as err:
        with suppress(AttributeError, RuntimeError, TypeError, ValueError):
            err.args = (safe_error_placeholder(err),)
        logger.exception("Unexpected error during %s upload", label.lower())
        return build_operation_outcome_from_exception(
            err,
            kind="failed",
            reason_code="value_error",
            failure_origin=_SHARE_SUBMIT_ORIGIN,
            failure_category="protocol",
            handling_policy="inspect",
        )


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
