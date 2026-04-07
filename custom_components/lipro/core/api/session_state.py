"""Shared session state for REST collaborators."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    import aiohttp


@dataclass(slots=True)
class RestSessionState:
    """State owned by the formal REST facade session boundary."""

    phone_id: str
    session: aiohttp.ClientSession | None
    request_timeout: int
    entry_id: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    user_id: int | None = None
    biz_id: str | None = None
    on_token_refresh: Callable[[], Awaitable[None]] | None = None
    refresh_lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        *,
        user_id: int | None = None,
        biz_id: str | None = None,
    ) -> None:
        """Persist the latest authentication tokens into state."""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user_id = user_id
        self.biz_id = biz_id

    def clear_session(self) -> None:
        """Detach the injected aiohttp session reference."""
        self.session = None


__all__ = ["RestSessionState"]
