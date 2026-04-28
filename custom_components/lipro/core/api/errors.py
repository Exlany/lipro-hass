"""API error types for the Lipro integration."""

from __future__ import annotations

from ..exceptions import ApiAuthError, ApiNetworkError, LiproApiError


class LiproAuthError(ApiAuthError):
    """Authentication error (401 or token expired)."""


class LiproRefreshTokenExpiredError(LiproAuthError):
    """Refresh token expired error (20002, 1202)."""


class LiproConnectionError(ApiNetworkError):
    """Connection error."""


class LiproRateLimitError(LiproApiError):
    """Rate limit error (429 Too Many Requests)."""

    def __init__(
        self, message: str, retry_after: float | None = None, code: int | str = 429
    ) -> None:
        """Initialize one rate-limit error with optional retry metadata."""
        super().__init__(message, code)
        self.retry_after = retry_after


__all__ = [
    "LiproApiError",
    "LiproAuthError",
    "LiproConnectionError",
    "LiproRateLimitError",
    "LiproRefreshTokenExpiredError",
]
