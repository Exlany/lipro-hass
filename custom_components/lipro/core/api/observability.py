"""Observability helpers for the Lipro API client."""

from __future__ import annotations

from ..anonymous_share import get_anonymous_share_manager


def record_api_error(
    endpoint: str,
    code: str | int,
    message: str,
    method: str = "",
    *,
    entry_id: str | None = None,
) -> None:
    """Record API error for anonymous share."""
    share_manager = get_anonymous_share_manager(entry_id=entry_id)
    share_manager.record_api_error(endpoint, code, message, method=method)


__all__ = ["record_api_error"]
