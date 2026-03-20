"""Worker client for anonymous sharing uploads."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from contextlib import suppress
from inspect import isawaitable
import json
import logging
import time
from typing import Any

import aiohttp

from ...const.base import VERSION
from ..telemetry.models import (
    OperationOutcome,
    build_operation_outcome,
    build_operation_outcome_from_exception,
)
from ..utils.log_safety import safe_error_placeholder
from ..utils.retry_after import parse_retry_after as parse_http_retry_after
from .const import SHARE_API_KEY, SHARE_REPORT_URL, SHARE_TOKEN_REFRESH_URL
from .report_builder import build_lite_report

_LOGGER = logging.getLogger(__package__ or __name__)

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


class ShareWorkerClient:
    """HTTP client for submitting anonymous share payloads to the Worker."""

    def __init__(self) -> None:
        """Initialize the client with in-memory token state."""
        self.install_token: str | None = None
        self.token_expires_at: int = 0
        self.token_refresh_after: int = 0
        self.next_upload_attempt_at: float = 0.0

    @staticmethod
    def build_upload_headers(*, install_token: str | None = None) -> dict[str, str]:
        """Build common headers for share uploads."""
        headers = {
            "User-Agent": f"HomeAssistant/Lipro {VERSION}",
            "X-API-Key": SHARE_API_KEY,
        }
        if install_token:
            headers["Authorization"] = f"Bearer {install_token}"
        return headers

    @staticmethod
    def parse_retry_after(headers: Any) -> float | None:
        """Parse Retry-After seconds (best-effort) via shared HTTP helper."""
        try:
            seconds = parse_http_retry_after(headers)
        except (AttributeError, TypeError, ValueError):
            return None
        if seconds is None:
            return None
        return max(0.1, seconds)

    def clear_install_token(self) -> None:
        """Clear local install-token state."""
        self.install_token = None
        self.token_expires_at = 0
        self.token_refresh_after = 0

    def apply_token_payload(self, payload: dict[str, Any]) -> bool:
        """Update local token state from response payload."""
        token = payload.get("install_token")
        if not isinstance(token, str) or not token:
            return False
        self.install_token = token
        self.token_expires_at = int(payload.get("token_expires_at") or 0)
        self.token_refresh_after = int(payload.get("token_refresh_after") or 0)
        return True

    async def _safe_read_json(
        self,
        response: aiohttp.ClientResponse,
    ) -> dict[str, Any] | None:
        """Best-effort JSON parsing for Worker responses."""
        try:
            json_reader = getattr(response, "json", None)
            if not callable(json_reader):
                return None
            result = response.json(content_type=None)
            data = await result if isawaitable(result) else result
        except (
            AttributeError,
            aiohttp.ContentTypeError,
            json.JSONDecodeError,
            ValueError,
        ):
            return None
        return data if isinstance(data, dict) else None

    async def refresh_install_token_with_outcome(
        self, session: aiohttp.ClientSession
    ) -> OperationOutcome:
        """Refresh install token via `/api/token/refresh` with typed outcome."""
        if not self.install_token:
            return build_operation_outcome(
                kind="skipped",
                reason_code="missing_install_token",
            )
        if time.time() < self.next_upload_attempt_at:
            return build_operation_outcome(
                kind="skipped",
                reason_code="backoff_active",
            )

        try:
            async with session.post(
                SHARE_TOKEN_REFRESH_URL,
                headers=self.build_upload_headers(install_token=self.install_token),
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                payload = await self._safe_read_json(response)
                if response.status == 200 and payload:
                    if self.apply_token_payload(payload):
                        return build_operation_outcome(
                            kind="success",
                            reason_code="refresh_success",
                        )
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
                    self.clear_install_token()
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
                    retry_after = self.parse_retry_after(response.headers)
                    if retry_after is not None:
                        self.next_upload_attempt_at = time.time() + min(60.0, retry_after)
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

    async def refresh_install_token(self, session: aiohttp.ClientSession) -> bool:
        """Refresh install token via `/api/token/refresh` when needed."""
        return (await self.refresh_install_token_with_outcome(session)).is_success

    async def submit_share_payload_with_outcome(
        self,
        session: aiohttp.ClientSession,
        report: dict[str, Any],
        *,
        label: str,
        ensure_loaded: Callable[[], Awaitable[None]],
    ) -> OperationOutcome:
        """Submit one payload to the share endpoint with typed failure semantics."""
        await ensure_loaded()

        if time.time() < self.next_upload_attempt_at:
            return build_operation_outcome(
                kind="skipped",
                reason_code="backoff_active",
            )

        installation_id = report.get("installation_id")
        if not isinstance(installation_id, str) or not installation_id:
            _LOGGER.warning("%s upload skipped: missing installation_id", label)
            return build_operation_outcome(
                kind="failed",
                reason_code="missing_installation_id",
                failure_origin=_SHARE_SUBMIT_ORIGIN,
                error_type="MissingInstallationId",
                failure_category="protocol",
                handling_policy="inspect",
            )

        if self.install_token:
            now_sec = int(time.time())
            if (self.token_refresh_after and now_sec >= self.token_refresh_after) or (
                self.token_expires_at and (self.token_expires_at - now_sec) <= 60
            ):
                await self.refresh_install_token(session)

        token_attempts: list[str | None] = (
            [self.install_token, None] if self.install_token else [None]
        )

        try:
            payload_variants = [report, build_lite_report(report)]
            last_status: int | None = None

            for variant_index, report_variant in enumerate(payload_variants):
                for token in token_attempts:
                    async with session.post(
                        SHARE_REPORT_URL,
                        json=report_variant,
                        headers=self.build_upload_headers(install_token=token),
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as response:
                        last_status = response.status
                        payload = await self._safe_read_json(response)

                        if response.status == 200:
                            if payload:
                                self.apply_token_payload(payload)
                            return build_operation_outcome(
                                kind="success",
                                reason_code=(
                                    "submitted_lite_payload"
                                    if variant_index == 1
                                    else "submitted"
                                ),
                            )

                        code = payload.get("code") if payload else None
                        if response.status == 429:
                            retry_after = self.parse_retry_after(response.headers)
                            if retry_after is not None:
                                self.next_upload_attempt_at = time.time() + min(60.0, retry_after)
                            return _rate_limited_outcome(
                                failure_origin=_SHARE_SUBMIT_ORIGIN,
                                retry_after_seconds=retry_after,
                            )

                        if response.status == 413 and variant_index == 0:
                            break

                        if response.status == 401 and code in _SUBMIT_TOKEN_REJECT_CODES:
                            if token:
                                self.clear_install_token()
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

            _LOGGER.warning(
                "%s upload failed with status %s",
                label,
                last_status if last_status is not None else "?",
            )
            return _http_failure_outcome(
                failure_origin=_SHARE_SUBMIT_ORIGIN,
                http_status=last_status,
                reason_code=(
                    "payload_too_large" if last_status == 413 else "http_error"
                ),
            )
        except TimeoutError as err:
            _LOGGER.warning("%s upload timed out", label)
            return build_operation_outcome_from_exception(
                err,
                kind="failed",
                reason_code="timeout",
                failure_origin=_SHARE_SUBMIT_ORIGIN,
                failure_category="network",
                handling_policy="retry",
            )
        except aiohttp.ClientError as err:
            _LOGGER.warning("%s upload failed: %s", label, safe_error_placeholder(err))
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
            _LOGGER.exception("Unexpected error during %s upload", label.lower())
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
            _LOGGER.exception("Unexpected error during %s upload", label.lower())
            return build_operation_outcome_from_exception(
                err,
                kind="failed",
                reason_code="value_error",
                failure_origin=_SHARE_SUBMIT_ORIGIN,
                failure_category="protocol",
                handling_policy="inspect",
            )

    async def submit_share_payload(
        self,
        session: aiohttp.ClientSession,
        report: dict[str, Any],
        *,
        label: str,
        ensure_loaded: Callable[[], Awaitable[None]],
    ) -> bool:
        """Submit one payload to share endpoint with legacy bool compatibility."""
        return (
            await self.submit_share_payload_with_outcome(
                session,
                report,
                label=label,
                ensure_loaded=ensure_loaded,
            )
        ).is_success
