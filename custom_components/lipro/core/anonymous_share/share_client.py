"""Worker client for anonymous sharing uploads."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging
import time
from typing import Any

import aiohttp

from ...const.base import VERSION
from ..telemetry.models import OperationOutcome
from ..utils.retry_after import parse_retry_after as parse_http_retry_after
from .const import SHARE_API_KEY
from .report_builder import build_lite_report
from .share_client_flows import (
    refresh_install_token_with_outcome as _refresh_install_token_with_outcome_flow,
    safe_read_json as _safe_read_json_flow,
    submit_share_payload_with_outcome as _submit_share_payload_with_outcome_flow,
)

_LOGGER = logging.getLogger(__package__ or __name__)

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
        except AttributeError, TypeError, ValueError:
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
        return await _safe_read_json_flow(response)

    async def refresh_install_token_with_outcome(
        self, session: aiohttp.ClientSession
    ) -> OperationOutcome:
        """Refresh install token via `/api/token/refresh` with typed outcome."""
        return await _refresh_install_token_with_outcome_flow(
            self,
            session,
            logger=_LOGGER,
            now=time.time,
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
        return await _submit_share_payload_with_outcome_flow(
            self,
            session,
            report,
            label=label,
            ensure_loaded=ensure_loaded,
            logger=_LOGGER,
            now=time.time,
            build_lite_variant=build_lite_report,
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
