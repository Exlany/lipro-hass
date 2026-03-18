# ruff: noqa: D107,SLF001
"""Request-pipeline collaborator for the REST child façade."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Protocol, TypeVar

import aiohttp

from ...const.api import (
    CONTENT_TYPE_FORM,
    HEADER_CONTENT_TYPE,
    HEADER_USER_AGENT,
    IOT_API_URL,
    SMART_HOME_API_URL,
    USER_AGENT,
)
from ...const.base import APP_VERSION_CODE, APP_VERSION_NAME
from .errors import LiproAuthError
from .request_codec import (
    build_smart_home_request_data,
    encode_iot_request_body,
    extract_smart_home_success_payload,
)
from .request_policy import RequestPolicy

_MappingPayloadT = TypeVar("_MappingPayloadT")
MappingRequestSender = Callable[[], Awaitable[tuple[int, Any, dict[str, str], str | None]]]


class _ClientRequestPort(Protocol):
    @property
    def _access_token(self) -> str | None: ...

    @property
    def _phone_id(self) -> str: ...

    @property
    def _request_timeout(self) -> int: ...

    @property
    def _request_policy(self) -> RequestPolicy: ...

    async def _get_session(self) -> aiohttp.ClientSession: ...
    def _smart_home_sign(self) -> str: ...
    def _get_timestamp_ms(self) -> int: ...
    async def _execute_request(
        self,
        request_ctx: Any,
        path: str,
    ) -> tuple[int, dict[str, Any], dict[str, str]]: ...
    async def _execute_mapping_request_with_rate_limit(
        self,
        *,
        path: str,
        retry_count: int,
        send_request: MappingRequestSender,
    ) -> tuple[int, dict[str, Any], str | None]: ...
    def _build_iot_headers(self, body: str) -> dict[str, str]: ...
    async def _handle_auth_error_and_retry(
        self,
        path: str,
        request_token: str | None,
        is_retry: bool,
    ) -> bool: ...
    async def _finalize_mapping_result(
        self,
        *,
        path: str,
        result: dict[str, Any],
        request_token: str | None,
        is_retry: bool,
        retry_on_auth_error: bool,
        retry_request: Callable[[], Awaitable[_MappingPayloadT]] | None,
        success_payload: Callable[[dict[str, Any]], _MappingPayloadT],
    ) -> _MappingPayloadT: ...
    @staticmethod
    def _unwrap_iot_success_payload(result: dict[str, Any]) -> Any: ...


class ClientRequestGateway:
    """Localize request-pipeline complexity away from `LiproRestFacade`."""

    def __init__(self, client: _ClientRequestPort) -> None:
        self._client = client

    async def request_smart_home_mapping(
        self,
        path: str,
        data: dict[str, Any],
        require_auth: bool = True,
        *,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        """Request one Smart Home mapping payload while preserving retry context."""
        url = f"{SMART_HOME_API_URL}{path}"

        async def _send_request() -> tuple[int, Any, dict[str, str], str | None]:
            request_token = self._client._access_token
            if require_auth and not request_token:
                msg = "No access token available"
                raise LiproAuthError(msg)

            request_data = build_smart_home_request_data(
                sign=self._client._smart_home_sign(),
                phone_id=self._client._phone_id,
                timestamp_ms=self._client._get_timestamp_ms(),
                app_version_name=APP_VERSION_NAME,
                app_version_code=APP_VERSION_CODE,
                data=data,
                access_token=request_token if require_auth else None,
            )

            session = await self._client._get_session()
            status, result, headers = await self._client._execute_request(
                session.post(
                    url,
                    data=request_data,
                    headers={
                        HEADER_CONTENT_TYPE: CONTENT_TYPE_FORM,
                        HEADER_USER_AGENT: USER_AGENT,
                    },
                    timeout=aiohttp.ClientTimeout(total=self._client._request_timeout),
                ),
                path,
            )
            return status, result, headers, request_token

        _, result, request_token = await self._client._execute_mapping_request_with_rate_limit(
            path=path,
            retry_count=retry_count,
            send_request=_send_request,
        )
        return result, request_token

    async def smart_home_request(
        self,
        path: str,
        data: dict[str, Any],
        require_auth: bool = True,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        """Execute one Smart Home request and finalize mapping semantics."""
        result, request_token = await self.request_smart_home_mapping(
            path,
            data,
            require_auth=require_auth,
            retry_count=retry_count,
        )
        return await self._client._finalize_mapping_result(
            path=path,
            result=result,
            request_token=request_token,
            is_retry=is_retry,
            retry_on_auth_error=require_auth,
            retry_request=lambda: self.smart_home_request(
                path,
                data,
                require_auth,
                is_retry=True,
            ),
            success_payload=extract_smart_home_success_payload,
        )

    async def request_iot_mapping_raw(
        self,
        path: str,
        body: str,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        """Request one raw IoT mapping payload while preserving retry context."""
        url = f"{IOT_API_URL}{path}"

        async def _send_request() -> tuple[int, Any, dict[str, str], str | None]:
            request_token = self._client._access_token
            if not request_token:
                msg = "No access token available"
                raise LiproAuthError(msg)

            session = await self._client._get_session()
            req_headers = self._client._build_iot_headers(body)
            status, result, resp_headers = await self._client._execute_request(
                session.post(
                    url,
                    data=body,
                    headers=req_headers,
                    timeout=aiohttp.ClientTimeout(total=self._client._request_timeout),
                ),
                path,
            )
            return status, result, resp_headers, request_token

        status, result, request_token = await self._client._execute_mapping_request_with_rate_limit(
            path=path,
            retry_count=retry_count,
            send_request=_send_request,
        )

        if status == 401:
            if await self._client._handle_auth_error_and_retry(path, request_token, is_retry):
                return await self.request_iot_mapping_raw(
                    path,
                    body,
                    is_retry=True,
                )
            msg = "HTTP 401 Unauthorized"
            raise LiproAuthError(msg, 401)

        return result, request_token

    async def request_iot_mapping(
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        """Encode and request one IoT mapping payload."""
        body = encode_iot_request_body(body_data)
        return await self.request_iot_mapping_raw(
            path,
            body,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def iot_request(
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        """Execute one IoT request and finalize mapping semantics."""
        result, request_token = await self.request_iot_mapping(
            path,
            body_data,
            is_retry=is_retry,
            retry_count=retry_count,
        )
        return await self._client._finalize_mapping_result(
            path=path,
            result=result,
            request_token=request_token,
            is_retry=is_retry,
            retry_on_auth_error=True,
            retry_request=lambda: self.iot_request(path, body_data, is_retry=True),
            success_payload=self._client._unwrap_iot_success_payload,
        )

    async def iot_request_with_busy_retry(
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        target_id: str,
        command: str,
        logger: Any,
    ) -> dict[str, Any]:
        """Execute one IoT command with the formal busy-retry policy."""
        result = await self._client._request_policy.iot_request_with_busy_retry(
            path,
            body_data,
            target_id=target_id,
            command=command,
            iot_request=self.iot_request,
            logger=logger,
        )
        return dict(result)


__all__ = ["ClientRequestGateway"]
