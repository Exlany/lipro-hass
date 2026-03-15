"""HTTP transport and request pipeline for Lipro REST protocol."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging
from typing import Any

import aiohttp

from ...const.api import (
    CONTENT_TYPE_FORM,
    CONTENT_TYPE_JSON,
    HEADER_ACCESS_TOKEN,
    HEADER_CACHE_CONTROL,
    HEADER_CONTENT_TYPE,
    HEADER_MERCHANT_CODE,
    HEADER_NONCE,
    HEADER_SIGN,
    HEADER_USER_AGENT,
    IOT_API_URL,
    MERCHANT_CODE,
    SMART_HOME_API_URL,
    USER_AGENT,
)
from ...const.base import APP_VERSION_CODE, APP_VERSION_NAME
from ...const.device_types import DEVICE_TYPE_MAP
from .client_auth_recovery import AuthRecoveryCoordinator
from .client_base import ClientSessionState
from .errors import LiproAuthError
from .request_codec import (
    build_smart_home_request_data,
    encode_iot_request_body,
    extract_smart_home_success_payload,
)
from .request_policy import RequestPolicy
from .response_safety import DEVICE_TYPE_HEX_PATTERN as _DEVICE_TYPE_HEX_PATTERN
from .transport_core import TransportCore
from .transport_retry import TransportRetry
from .transport_signing import TransportSigning

_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")

MappingRequestSender = Callable[[], Awaitable[tuple[int, Any, dict[str, str], str | None]]]


class TransportExecutor:
    """Explicit owner for signed request execution and transport retries."""

    def __init__(
        self,
        state: ClientSessionState,
        auth_recovery: AuthRecoveryCoordinator,
        request_policy: RequestPolicy,
    ) -> None:
        """Initialize transport execution collaborators around shared session state."""
        self._state = state
        self._auth_recovery = auth_recovery
        self._request_policy = request_policy
        self._transport_core = TransportCore(state.session, state.request_timeout)
        self._transport_signing = TransportSigning(state.phone_id)
        self._transport_retry = TransportRetry()

    def sync_session(self, session: aiohttp.ClientSession | None) -> None:
        """Keep the transport core aligned with state-owned session changes."""
        self._state.session = session
        self._transport_core.set_session(session)

    @property
    def phone_id(self) -> str:
        """Return the phone identifier used when signing requests."""
        return self._state.phone_id

    async def get_session(self) -> aiohttp.ClientSession:
        """Return the active aiohttp session, creating one if needed."""
        return await self._transport_core.get_session()

    def close(self) -> None:
        """Detach and close the transport-owned aiohttp session."""
        self._state.clear_session()
        self._transport_core.close_session()

    def smart_home_sign(self) -> str:
        """Return the Smart Home signature for the next request."""
        return self._transport_signing.smart_home_sign()

    def iot_sign(self, nonce: int, body: str) -> str:
        """Return the signed IoT request digest for one payload."""
        return self._transport_signing.iot_sign(self._state.access_token or "", nonce, body)

    def to_device_type_hex(self, device_type: int | str) -> str:
        """Normalize one device type into the transport hex representation."""
        if isinstance(device_type, int):
            return DEVICE_TYPE_MAP.get(device_type, f"ff{device_type:06x}")
        normalized = device_type.strip().lower()
        if _DEVICE_TYPE_HEX_PATTERN.fullmatch(normalized):
            return normalized
        if normalized.isdecimal():
            numeric_type = int(normalized)
            return DEVICE_TYPE_MAP.get(numeric_type, f"ff{numeric_type:06x}")

        msg = f"Invalid deviceType format: {device_type!r}"
        raise ValueError(msg)

    def get_timestamp_ms(self) -> int:
        """Return the signing timestamp in milliseconds."""
        return self._transport_signing.get_timestamp_ms()

    async def execute_request(
        self,
        request_ctx: Any,
        path: str,
    ) -> tuple[int, dict[str, Any], dict[str, str]]:
        """Execute one low-level HTTP request context and normalize the response."""
        return await self._transport_core.execute_request(request_ctx, path)

    @staticmethod
    def require_mapping_response(path: str, result: Any) -> dict[str, Any]:
        """Require one mapping response payload to be a JSON object."""
        return TransportCore.require_mapping_response(path, result)

    async def execute_mapping_request_with_rate_limit(
        self,
        *,
        path: str,
        retry_count: int,
        send_request: MappingRequestSender,
    ) -> tuple[int, dict[str, Any], str | None]:
        """Execute one mapping request with policy-owned rate-limit retries."""
        return await self._transport_retry.execute_with_rate_limit_retry(
            path=path,
            retry_count=retry_count,
            send_request=send_request,
            require_mapping_response=self.require_mapping_response,
            parse_retry_after=self._request_policy.parse_retry_after,
        )

    async def request_smart_home_mapping(
        self,
        path: str,
        data: dict[str, Any],
        require_auth: bool = True,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        """Request one Smart Home mapping payload and preserve retry context."""
        url = f"{SMART_HOME_API_URL}{path}"

        async def _send_request() -> tuple[int, Any, dict[str, str], str | None]:
            request_token = self._state.access_token
            if require_auth and not request_token:
                msg = "No access token available"
                raise LiproAuthError(msg)

            request_data = build_smart_home_request_data(
                sign=self.smart_home_sign(),
                phone_id=self._state.phone_id,
                timestamp_ms=self.get_timestamp_ms(),
                app_version_name=APP_VERSION_NAME,
                app_version_code=APP_VERSION_CODE,
                data=data,
                access_token=request_token if require_auth else None,
            )

            session = await self.get_session()
            status, result, headers = await self.execute_request(
                session.post(
                    url,
                    data=request_data,
                    headers={
                        HEADER_CONTENT_TYPE: CONTENT_TYPE_FORM,
                        HEADER_USER_AGENT: USER_AGENT,
                    },
                    timeout=aiohttp.ClientTimeout(total=self._state.request_timeout),
                ),
                path,
            )
            return status, result, headers, request_token

        _, result, request_token = await self.execute_mapping_request_with_rate_limit(
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
        """Execute one Smart Home request and finalize auth-aware mapping results."""
        result, request_token = await self.request_smart_home_mapping(
            path,
            data,
            require_auth=require_auth,
            is_retry=is_retry,
            retry_count=retry_count,
        )
        return await self._auth_recovery.finalize_mapping_result(
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

    def build_iot_headers(self, body: str) -> dict[str, str]:
        """Build signed headers for one IoT request payload."""
        nonce = self.get_timestamp_ms()
        sign = self.iot_sign(nonce, body)
        return {
            HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
            HEADER_CACHE_CONTROL: "no-cache",
            HEADER_USER_AGENT: USER_AGENT,
            HEADER_ACCESS_TOKEN: self._state.access_token or "",
            HEADER_MERCHANT_CODE: MERCHANT_CODE,
            HEADER_NONCE: str(nonce),
            HEADER_SIGN: sign,
        }

    async def request_iot_mapping_raw(
        self,
        path: str,
        body: str,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        """Request one raw IoT mapping payload and preserve retry context."""
        url = f"{IOT_API_URL}{path}"

        async def _send_request() -> tuple[int, Any, dict[str, str], str | None]:
            request_token = self._state.access_token
            if not request_token:
                msg = "No access token available"
                raise LiproAuthError(msg)

            session = await self.get_session()
            req_headers = self.build_iot_headers(body)
            status, result, resp_headers = await self.execute_request(
                session.post(
                    url,
                    data=body,
                    headers=req_headers,
                    timeout=aiohttp.ClientTimeout(total=self._state.request_timeout),
                ),
                path,
            )
            return status, result, resp_headers, request_token

        status, result, request_token = await self.execute_mapping_request_with_rate_limit(
            path=path,
            retry_count=retry_count,
            send_request=_send_request,
        )

        if status == 401:
            if await self._auth_recovery.handle_auth_error_and_retry(
                path,
                request_token,
                is_retry,
            ):
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
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        """Execute one IoT request and finalize auth-aware mapping results."""
        result, request_token = await self.request_iot_mapping(
            path,
            body_data,
            is_retry=is_retry,
            retry_count=retry_count,
        )
        return await self._auth_recovery.finalize_mapping_result(
            path=path,
            result=result,
            request_token=request_token,
            is_retry=is_retry,
            retry_on_auth_error=True,
            retry_request=lambda: self.iot_request(path, body_data, is_retry=True),
            success_payload=self._auth_recovery.unwrap_iot_success_payload,
        )


__all__ = ["TransportExecutor"]
