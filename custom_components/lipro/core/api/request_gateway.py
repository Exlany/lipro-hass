"""Request gateway helpers for the formal REST façade.

This module keeps retry-aware mapping flows close to the REST façade without
inflating the composition root. It is a localized collaborator, not a second
public root.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Protocol, TypeVar

import aiohttp

from ...const.api import CONTENT_TYPE_FORM, IOT_API_URL, SMART_HOME_API_URL
from ...const.base import APP_VERSION_CODE, APP_VERSION_NAME
from .errors import LiproAuthError
from .request_codec import (
    build_smart_home_request_data,
    encode_iot_request_body,
    extract_smart_home_success_payload,
)

MappingRequestSender = Callable[[], Awaitable[tuple[int, Any, dict[str, str], str | None]]]
_MappingPayloadT = TypeVar("_MappingPayloadT")


class RestRequestGatewayFacade(Protocol):
    """Minimal façade contract consumed by the localized request gateway."""

    @property
    def access_token(self) -> str | None: ...

    @property
    def phone_id(self) -> str: ...

    @property
    def request_timeout(self) -> int: ...

    async def get_session(self) -> aiohttp.ClientSession: ...

    def smart_home_sign(self) -> str: ...

    def get_timestamp_ms(self) -> int: ...

    async def execute_request(
        self,
        request_ctx: Any,
        path: str,
    ) -> tuple[int, dict[str, Any], dict[str, str]]: ...

    async def execute_mapping_request_with_rate_limit(
        self,
        *,
        path: str,
        retry_count: int,
        send_request: MappingRequestSender,
    ) -> tuple[int, dict[str, Any], str | None]: ...

    def build_iot_headers(self, body: str) -> dict[str, str]: ...

    async def handle_auth_error_and_retry(
        self,
        path: str,
        request_token: str | None,
        is_retry: bool,
    ) -> bool: ...

    async def finalize_mapping_result(
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

    def unwrap_iot_success_payload(self, result: dict[str, Any]) -> Any: ...


class RestRequestGateway:
    """Host retry-aware request helpers behind one explicit collaborator."""

    def __init__(self, facade: RestRequestGatewayFacade) -> None:
        """Bind the gateway to the canonical REST façade instance."""
        self._facade = facade

    async def request_smart_home_mapping(
        self,
        path: str,
        data: dict[str, Any],
        require_auth: bool = True,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        """Return the raw Smart Home mapping payload plus request token."""
        del is_retry
        facade = self._facade
        url = f"{SMART_HOME_API_URL}{path}"

        async def _send_request() -> tuple[int, Any, dict[str, str], str | None]:
            request_token = facade.access_token
            if require_auth and not request_token:
                msg = "No access token available"
                raise LiproAuthError(msg)

            request_data = build_smart_home_request_data(
                sign=facade.smart_home_sign(),
                phone_id=facade.phone_id,
                timestamp_ms=facade.get_timestamp_ms(),
                app_version_name=APP_VERSION_NAME,
                app_version_code=APP_VERSION_CODE,
                data=data,
                access_token=request_token if require_auth else None,
            )
            session = await facade.get_session()
            status, result, headers = await facade.execute_request(
                session.post(
                    url,
                    data=request_data,
                    headers={"Content-Type": CONTENT_TYPE_FORM},
                    timeout=aiohttp.ClientTimeout(total=facade.request_timeout),
                ),
                path,
            )
            return status, result, headers, request_token

        _, result, request_token = await facade.execute_mapping_request_with_rate_limit(
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
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        """Finalize one Smart Home request through the explicit auth path."""
        facade = self._facade
        result, request_token = await self.request_smart_home_mapping(
            path,
            data,
            require_auth=require_auth,
            is_retry=is_retry,
            retry_count=retry_count,
        )
        return await facade.finalize_mapping_result(
            path=path,
            result=result,
            request_token=request_token,
            is_retry=is_retry,
            retry_on_auth_error=require_auth,
            retry_request=lambda: self.smart_home_request(
                path,
                data,
                require_auth=require_auth,
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
        """Return the raw IoT mapping payload plus request token."""
        facade = self._facade
        url = f"{IOT_API_URL}{path}"

        async def _send_request() -> tuple[int, Any, dict[str, str], str | None]:
            request_token = facade.access_token
            if not request_token:
                msg = "No access token available"
                raise LiproAuthError(msg)

            session = await facade.get_session()
            status, result, response_headers = await facade.execute_request(
                session.post(
                    url,
                    data=body,
                    headers=facade.build_iot_headers(body),
                    timeout=aiohttp.ClientTimeout(total=facade.request_timeout),
                ),
                path,
            )
            return status, result, response_headers, request_token

        status, result, request_token = await facade.execute_mapping_request_with_rate_limit(
            path=path,
            retry_count=retry_count,
            send_request=_send_request,
        )
        if status == 401:
            if await facade.handle_auth_error_and_retry(path, request_token, is_retry):
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
        """Encode and dispatch one IoT mapping request."""
        return await self.request_iot_mapping_raw(
            path,
            encode_iot_request_body(body_data),
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
        """Finalize one IoT request through the explicit auth path."""
        facade = self._facade
        result, request_token = await self.request_iot_mapping(
            path,
            body_data,
            is_retry=is_retry,
            retry_count=retry_count,
        )
        return await facade.finalize_mapping_result(
            path=path,
            result=result,
            request_token=request_token,
            is_retry=is_retry,
            retry_on_auth_error=True,
            retry_request=lambda: self.iot_request(path, body_data, is_retry=True),
            success_payload=facade.unwrap_iot_success_payload,
        )

    async def dispatch_retry_aware_call(
        self,
        call: Callable[..., Awaitable[_MappingPayloadT]],
        *args: object,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> _MappingPayloadT:
        """Dispatch one retry-aware helper while preserving patch seams."""
        if not is_retry and not retry_count:
            return await call(*args)
        return await call(*args, is_retry=is_retry, retry_count=retry_count)

    async def dispatch_retry_aware_smart_home_call(
        self,
        path: str,
        data: dict[str, Any],
        *,
        require_auth: bool,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        """Dispatch Smart Home calls while preserving retry semantics."""
        if not is_retry and not retry_count:
            if require_auth:
                return await self.smart_home_request(path, data)
            return await self.smart_home_request(path, data, require_auth=False)
        return await self.smart_home_request(
            path,
            data,
            require_auth=require_auth,
            is_retry=is_retry,
            retry_count=retry_count,
        )


__all__ = ["RestRequestGateway"]
