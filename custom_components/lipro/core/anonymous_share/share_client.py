"""Worker client for anonymous sharing uploads."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
import logging
import time

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
from .share_client_support import (
    JsonReadableResponse,
    SharePayload,
    WorkerResponsePayload,
    extract_token_payload,
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
    def parse_retry_after(headers: object) -> float | None:
        """Parse Retry-After seconds (best-effort) via shared HTTP helper."""
        if not isinstance(headers, Mapping):
            return None
        normalized_headers = {
            key: value
            for key, value in headers.items()
            if isinstance(key, str) and isinstance(value, str)
        }
        try:
            seconds = parse_http_retry_after(normalized_headers)
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

    def apply_token_payload(self, payload: WorkerResponsePayload) -> bool:
        """Update local token state from response payload."""
        token_payload = extract_token_payload(payload)
        if token_payload is None:
            return False
        self.install_token = token_payload["install_token"]
        self.token_expires_at = token_payload.get("token_expires_at", 0)
        self.token_refresh_after = token_payload.get("token_refresh_after", 0)
        return True

    async def safe_read_json(
        self, response: JsonReadableResponse
    ) -> WorkerResponsePayload | None:
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
        report: SharePayload,
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
