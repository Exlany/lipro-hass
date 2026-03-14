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

    async def smart_home_request(
        self,
        path: str,
        data: dict[str, Any],
        require_auth: bool = True,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        """Execute one Smart Home request through the formal transport pipeline."""
        if require_auth is True and not is_retry and not retry_count:
            return await self._smart_home_request(path, data)
        return await self._smart_home_request(
            path,
            data,
            require_auth=require_auth,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def iot_request(
        self,
        path: str,
        body_data: dict[str, Any],
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        """Execute one IoT request through the formal transport pipeline."""
        if not is_retry and not retry_count:
            return await self._iot_request(path, body_data)
        return await self._iot_request(
            path,
            body_data,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def request_iot_mapping(
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        """Request one IoT mapping payload with retry context preserved."""
        if not is_retry and not retry_count:
            return await self._request_iot_mapping(path, body_data)
        return await self._request_iot_mapping(
            path,
            body_data,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def request_iot_mapping_raw(
        self,
        path: str,
        body: str,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        """Request one raw IoT mapping payload without result finalization."""
        if not is_retry and not retry_count:
            return await self._request_iot_mapping_raw(path, body)
        return await self._request_iot_mapping_raw(
            path,
            body,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def iot_request_with_busy_retry(
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        target_id: str,
        command: str,
    ) -> dict[str, Any]:
        """Execute one paced IoT request with command-busy retry handling."""
        return await self._iot_request_with_busy_retry(
            path,
            body_data,
            target_id=target_id,
            command=command,
        )

    def to_device_type_hex(self, device_type: int | str) -> str:
        """Normalize one device type into the transport hex representation."""
        return self._to_device_type_hex(device_type)

    def is_success_code(self, code: Any) -> bool:
        """Return whether one response code represents a success payload."""
        return self._is_success_code(code)

    def unwrap_iot_success_payload(self, result: dict[str, Any]) -> Any:
        """Extract the canonical success payload from one IoT response."""
        return self._unwrap_iot_success_payload(result)

    def require_mapping_response(self, path: str, result: Any) -> dict[str, Any]:
        """Require one mapping response payload to be a JSON object."""
        return self._require_mapping_response(path, result)

    def is_invalid_param_error_code(self, code: Any) -> bool:
        """Return whether one code denotes an invalid-parameter response."""
        return self._is_invalid_param_error_code(code)


__all__ = ["ClientSessionState", "_ClientBase"]
