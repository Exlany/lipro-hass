"""Support-only ports and constants for anonymous-share client flows."""

from __future__ import annotations

from typing import Protocol

import aiohttp

from ..telemetry.models import OperationOutcome
from .share_client_support import JsonReadableResponse, WorkerResponsePayload


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
