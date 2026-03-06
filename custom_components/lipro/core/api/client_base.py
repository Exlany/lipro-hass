"""Typing base for LiproClient mixins.

This module defines a minimal base class for client mixins so mypy can
type-check extracted endpoint helpers that access internal client methods.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    import aiohttp

    from .auth_service import AuthApiService
    from .schedule_service import ScheduleApiService


class _ClientBase:
    """Shared base for client mixins (typing only)."""

    # Initialized in LiproClient.__init__.
    _auth_api: AuthApiService
    _schedule_api: ScheduleApiService
    _phone_id: str
    _session: aiohttp.ClientSession | None
    _request_timeout: int
    _access_token: str | None
    _refresh_token: str | None
    _user_id: int | None
    _biz_id: str | None
    _on_token_refresh: Callable[[], Awaitable[None]] | None
    _refresh_lock: asyncio.Lock
    _command_pacing_lock: asyncio.Lock
    _command_pacing_target_locks: dict[str, asyncio.Lock]
    _last_change_state_at: dict[str, float]
    _change_state_min_interval: dict[str, float]
    _change_state_busy_count: dict[str, int]

    async def _smart_home_request(  # pragma: no cover
        self,
        path: str,
        data: dict[str, Any],
        require_auth: bool = True,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        raise NotImplementedError

    async def _iot_request(  # pragma: no cover
        self,
        path: str,
        body_data: dict[str, Any],
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        raise NotImplementedError

    async def _request_iot_mapping(  # pragma: no cover
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        raise NotImplementedError

    async def _iot_request_with_busy_retry(  # pragma: no cover
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        target_id: str,
        command: str,
    ) -> dict[str, Any]:
        raise NotImplementedError

    def _to_device_type_hex(  # pragma: no cover
        self, device_type: int | str
    ) -> str:
        raise NotImplementedError

    def _is_success_code(self, code: Any) -> bool:  # pragma: no cover
        raise NotImplementedError

    def _unwrap_iot_success_payload(  # pragma: no cover
        self, result: dict[str, Any]
    ) -> Any:
        raise NotImplementedError

    @staticmethod
    def _require_mapping_response(  # pragma: no cover
        path: str, result: Any
    ) -> dict[str, Any]:
        raise NotImplementedError

    @staticmethod
    def _is_invalid_param_error_code(code: Any) -> bool:  # pragma: no cover
        raise NotImplementedError


__all__ = ["_ClientBase"]
