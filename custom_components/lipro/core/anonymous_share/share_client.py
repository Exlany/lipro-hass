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

from ...const import VERSION
from ..utils.log_safety import safe_error_placeholder
from .const import SHARE_API_KEY, SHARE_REPORT_URL, SHARE_TOKEN_REFRESH_URL
from .report_builder import build_lite_report

_LOGGER = logging.getLogger(__package__ or __name__)

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


class ShareWorkerClient:
    """HTTP client for submitting anonymous share payloads to the Worker."""

    def __init__(self) -> None:
        """Initialize the client with in-memory token state."""
        self.install_token: str | None = None
        self.token_expires_at: int = 0  # epoch seconds
        self.token_refresh_after: int = 0  # epoch seconds
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
        """Parse Retry-After seconds (best-effort)."""
        try:
            value = headers.get("Retry-After") or headers.get("retry-after")
            if not value:
                return None
            seconds = float(str(value).strip())
            if seconds <= 0:
                return 0.1
            return seconds
        except (AttributeError, TypeError, ValueError):
            return None

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

    async def refresh_install_token(self, session: aiohttp.ClientSession) -> bool:
        """Refresh install token via /api/token/refresh when needed."""
        if not self.install_token:
            return False
        if time.time() < self.next_upload_attempt_at:
            return False

        try:
            async with session.post(
                SHARE_TOKEN_REFRESH_URL,
                headers=self.build_upload_headers(install_token=self.install_token),
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                payload = await self._safe_read_json(response)
                if response.status == 200 and payload:
                    if self.apply_token_payload(payload):
                        return True

                code = payload.get("code") if payload else None
                if response.status == 401 and code in _TOKEN_INVALID_CODES:
                    self.clear_install_token()
                    return False

                if response.status == 429:
                    retry_after = self.parse_retry_after(response.headers)
                    if retry_after is not None:
                        self.next_upload_attempt_at = time.time() + min(
                            60.0, retry_after
                        )
                    return False

                return False
        except TimeoutError:
            return False
        except aiohttp.ClientError:
            return False
        except (OSError, ValueError):
            return False

    async def submit_share_payload(
        self,
        session: aiohttp.ClientSession,
        report: dict[str, Any],
        *,
        label: str,
        ensure_loaded: Callable[[], Awaitable[None]],
    ) -> bool:
        """Submit one payload to share endpoint with unified error handling."""
        await ensure_loaded()

        if time.time() < self.next_upload_attempt_at:
            return False

        installation_id = report.get("installation_id")
        if not isinstance(installation_id, str) or not installation_id:
            _LOGGER.warning("%s upload skipped: missing installation_id", label)
            return False

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
                            return True

                        code = payload.get("code") if payload else None

                        if response.status == 429:
                            retry_after = self.parse_retry_after(response.headers)
                            if retry_after is not None:
                                self.next_upload_attempt_at = time.time() + min(
                                    60.0, retry_after
                                )
                            return False

                        if response.status == 413 and variant_index == 0:
                            break

                        if (
                            response.status == 401
                            and code in _SUBMIT_TOKEN_REJECT_CODES
                        ):
                            if token:
                                self.clear_install_token()
                                continue
                            return False

                        if response.status == 400 and code == "INVALID_SCHEMA":
                            return False

                # continue to next variant

            _LOGGER.warning(
                "%s upload failed with status %s",
                label,
                last_status if last_status is not None else "?",
            )
            return False
        except TimeoutError:
            _LOGGER.warning("%s upload timed out", label)
            return False
        except aiohttp.ClientError as err:
            _LOGGER.warning("%s upload failed: %s", label, safe_error_placeholder(err))
            return False
        except (OSError, ValueError) as err:
            with suppress(Exception):
                err.args = (safe_error_placeholder(err),)
            _LOGGER.exception("Unexpected error during %s upload", label.lower())
            return False
