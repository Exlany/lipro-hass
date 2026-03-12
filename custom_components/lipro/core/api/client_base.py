"""Shared state and typing base for Lipro REST protocol collaborators."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    import aiohttp

    from .auth_service import AuthApiService
    from .schedule_service import ScheduleApiService


@dataclass(slots=True)
class ClientSessionState:
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


class _ClientBase:
    """Shared protocol surface expected by endpoint mixins and helpers.

    This remains as a temporary typing anchor during Phase 2. The formal REST
    root is now ``LiproRestFacade`` with explicit collaborators.
    """

    _auth_api: AuthApiService
    _schedule_api: ScheduleApiService
    _session_state: ClientSessionState

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

    async def _request_iot_mapping_raw(  # pragma: no cover
        self,
        path: str,
        body: str,
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


__all__ = ["ClientSessionState", "_ClientBase"]
