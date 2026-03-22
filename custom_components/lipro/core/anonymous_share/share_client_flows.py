# ruff: noqa: SLF001

"""Internal token-refresh and submit-flow helpers for the share worker client."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from contextlib import suppress
import json
from typing import TYPE_CHECKING, Any

import aiohttp

from ..telemetry.models import (
    OperationOutcome,
    build_operation_outcome,
    build_operation_outcome_from_exception,
)
from ..utils.log_safety import safe_error_placeholder
from .const import SHARE_REPORT_URL, SHARE_TOKEN_REFRESH_URL
from .share_client_support import (
    backoff_active,
    build_submit_variants,
    has_valid_installation_id,
    refresh_due,
    schedule_retry_deadline,
    submit_failure_reason_code,
)

if TYPE_CHECKING:
    from logging import Logger

    from .share_client import ShareWorkerClient

_TOKEN_REFRESH_ORIGIN = "anonymous_share.refresh_install_token"
_SHARE_SUBMIT_ORIGIN = "anonymous_share.submit_share_payload"
_TOKEN_INVALID_CODES = {
    "TOKEN_EXPIRED",
    "TOKEN_REVOKED",
    "TOKEN_VERSION_REVOKED",
    "TOKEN_KEY_NOT_FOUND",
    "TOKEN_SIGNATURE_INVALID",
    "TOKEN_CLAIMS_INVALID",
    "TOKEN_STATE_MISSING",
}
_SUBMIT_TOKEN_REJECT_CODES = {
    "TOKEN_VERSION_REVOKED",
    "TOKEN_REVOKED",
    "TOKEN_EXPIRED",
    "TOKEN_REQUIRED",
    "TOKEN_MISSING",
    "TOKEN_STATE_MISSING",
    "TOKEN_KEY_NOT_FOUND",
    "TOKEN_SIGNATURE_INVALID",
    "TOKEN_CLAIMS_INVALID",
    "TOKEN_INSTALLATION_MISMATCH",
}


def _http_failure_outcome(
    *,
    failure_origin: str,
    http_status: int | None,
    reason_code: str = "http_error",
) -> OperationOutcome:
    return build_operation_outcome(
        kind="failed",
        reason_code=reason_code,
        failure_origin=failure_origin,
        error_type=(f"HttpStatus{http_status}" if http_status is not None else None),
        failure_category="protocol",
        handling_policy="inspect",
        http_status=http_status,
    )


def _rate_limited_outcome(
    *,
    failure_origin: str,
    retry_after_seconds: float | None,
) -> OperationOutcome:
    return build_operation_outcome(
        kind="failed",
        reason_code="rate_limited",
        failure_origin=failure_origin,
        error_type="RateLimitError",
        failure_category="network",
        handling_policy="retry",
        http_status=429,
        retry_after_seconds=retry_after_seconds,
    )


async def safe_read_json(
    response: aiohttp.ClientResponse,
) -> dict[str, Any] | None:
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
    client: ShareWorkerClient,
    session: aiohttp.ClientSession,
    *,
    logger: Logger,
    now: Callable[[], float],
) -> OperationOutcome:
    """Refresh the install token via `/api/token/refresh` with typed outcome."""
    if not client.install_token:
        return build_operation_outcome(kind="skipped", reason_code="missing_install_token")
    if backoff_active(next_upload_attempt_at=client.next_upload_attempt_at, now=now):
        return build_operation_outcome(kind="skipped", reason_code="backoff_active")

    try:
        async with session.post(
            SHARE_TOKEN_REFRESH_URL,
            headers=client.build_upload_headers(install_token=client.install_token),
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            payload = await client._safe_read_json(response)
            if response.status == 200 and payload:
                if client.apply_token_payload(payload):
                    return build_operation_outcome(kind="success", reason_code="refresh_success")
                return build_operation_outcome(
                    kind="failed",
                    reason_code="invalid_refresh_payload",
                    failure_origin=_TOKEN_REFRESH_ORIGIN,
                    error_type="InvalidTokenPayload",
                    failure_category="protocol",
                    handling_policy="inspect",
                    http_status=200,
                )

            code = payload.get("code") if payload else None
            if response.status == 401 and code in _TOKEN_INVALID_CODES:
                client.clear_install_token()
                return build_operation_outcome(
                    kind="failed",
                    reason_code="token_invalid",
                    failure_origin=_TOKEN_REFRESH_ORIGIN,
                    error_type="InstallTokenRejected",
                    failure_category="auth",
                    handling_policy="reauth",
                    http_status=401,
                )

            if response.status == 429:
                retry_after = client.parse_retry_after(response.headers)
                retry_deadline = schedule_retry_deadline(retry_after_seconds=retry_after, now=now)
                if retry_deadline is not None:
                    client.next_upload_attempt_at = retry_deadline
                return _rate_limited_outcome(
                    failure_origin=_TOKEN_REFRESH_ORIGIN,
                    retry_after_seconds=retry_after,
                )

            return _http_failure_outcome(
                failure_origin=_TOKEN_REFRESH_ORIGIN,
                http_status=response.status,
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


async def submit_share_payload_with_outcome(
    client: ShareWorkerClient,
    session: aiohttp.ClientSession,
    report: dict[str, Any],
    *,
    label: str,
    ensure_loaded: Callable[[], Awaitable[None]],
    logger: Logger,
    now: Callable[[], float],
    build_lite_variant: Callable[[dict[str, Any]], dict[str, Any]],
) -> OperationOutcome:
    """Submit one payload to the share endpoint with typed failure semantics."""
    await ensure_loaded()

    if backoff_active(next_upload_attempt_at=client.next_upload_attempt_at, now=now):
        return build_operation_outcome(kind="skipped", reason_code="backoff_active")

    if not has_valid_installation_id(report):
        logger.warning("%s upload skipped: missing installation_id", label)
        return build_operation_outcome(
            kind="failed",
            reason_code="missing_installation_id",
            failure_origin=_SHARE_SUBMIT_ORIGIN,
            error_type="MissingInstallationId",
            failure_category="protocol",
            handling_policy="inspect",
        )

    if refresh_due(
        install_token=client.install_token,
        token_refresh_after=client.token_refresh_after,
        token_expires_at=client.token_expires_at,
        now_seconds=int(now()),
    ):
        await client.refresh_install_token(session)

    try:
        submit_variants = build_submit_variants(
            report,
            install_token=client.install_token,
            build_lite_variant=build_lite_variant,
        )
        last_status: int | None = None

        for submit_variant in submit_variants:
            for token in submit_variant.token_attempts:
                async with session.post(
                    SHARE_REPORT_URL,
                    json=submit_variant.payload,
                    headers=client.build_upload_headers(install_token=token),
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    last_status = response.status
                    payload = await client._safe_read_json(response)

                    if response.status == 200:
                        if payload:
                            client.apply_token_payload(payload)
                        return build_operation_outcome(
                            kind="success",
                            reason_code=submit_variant.success_reason_code,
                        )

                    code = payload.get("code") if payload else None
                    if response.status == 429:
                        retry_after = client.parse_retry_after(response.headers)
                        retry_deadline = schedule_retry_deadline(
                            retry_after_seconds=retry_after,
                            now=now,
                        )
                        if retry_deadline is not None:
                            client.next_upload_attempt_at = retry_deadline
                        return _rate_limited_outcome(
                            failure_origin=_SHARE_SUBMIT_ORIGIN,
                            retry_after_seconds=retry_after,
                        )

                    if (
                        response.status == 413
                        and submit_variant.fallback_on_payload_too_large
                    ):
                        break

                    if response.status == 401 and code in _SUBMIT_TOKEN_REJECT_CODES:
                        if token:
                            client.clear_install_token()
                            continue
                        return build_operation_outcome(
                            kind="failed",
                            reason_code="token_rejected",
                            failure_origin=_SHARE_SUBMIT_ORIGIN,
                            error_type="InstallTokenRejected",
                            failure_category="auth",
                            handling_policy="reauth",
                            http_status=401,
                        )

                    if response.status == 400 and code == "INVALID_SCHEMA":
                        return build_operation_outcome(
                            kind="failed",
                            reason_code="invalid_schema",
                            failure_origin=_SHARE_SUBMIT_ORIGIN,
                            error_type="InvalidSchema",
                            failure_category="protocol",
                            handling_policy="inspect",
                            http_status=400,
                        )

        logger.warning(
            "%s upload failed with status %s",
            label,
            last_status if last_status is not None else "?",
        )
        return _http_failure_outcome(
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
