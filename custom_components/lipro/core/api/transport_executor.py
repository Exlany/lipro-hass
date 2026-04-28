"""HTTP transport primitives for Lipro REST protocol."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

import aiohttp

from ...const.api import (
    CONTENT_TYPE_JSON,
    HEADER_ACCESS_TOKEN,
    HEADER_CACHE_CONTROL,
    HEADER_CONTENT_TYPE,
    HEADER_MERCHANT_CODE,
    HEADER_NONCE,
    HEADER_SIGN,
    HEADER_USER_AGENT,
    MERCHANT_CODE,
    USER_AGENT,
)
from ...const.device_types import DEVICE_TYPE_MAP
from .auth_recovery import RestAuthRecoveryCoordinator
from .request_policy import RequestPolicy
from .response_safety import DEVICE_TYPE_HEX_PATTERN as _DEVICE_TYPE_HEX_PATTERN
from .session_state import RestSessionState
from .transport_core import TransportCore
from .transport_retry import TransportRetry
from .transport_signing import TransportSigning
from .types import JsonObject

type ResponseHeaders = dict[str, str]
MappingRequestSender = Callable[
    [],
    Awaitable[tuple[int, object, ResponseHeaders, str | None]],
]


class RestTransportExecutor:
    """Explicit owner for session/signing/HTTP execution and replay glue."""

    def __init__(
        self,
        state: RestSessionState,
        auth_recovery: RestAuthRecoveryCoordinator,
        request_policy: RequestPolicy,
    ) -> None:
        """Initialize transport execution collaborators around shared session state."""
        del auth_recovery
        self._state = state
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
        return self._transport_signing.iot_sign(
            self._state.access_token or "", nonce, body
        )

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
        request_ctx: object,
        path: str,
    ) -> tuple[int, JsonObject, ResponseHeaders]:
        """Execute one low-level HTTP request context and normalize the response."""
        return await self._transport_core.execute_request(request_ctx, path)

    @staticmethod
    def require_mapping_response(path: str, result: object) -> JsonObject:
        """Require one mapping response payload to be a JSON object."""
        return TransportCore.require_mapping_response(path, result)

    async def execute_mapping_request_with_rate_limit(
        self,
        *,
        path: str,
        retry_count: int,
        send_request: MappingRequestSender,
    ) -> tuple[int, JsonObject, str | None]:
        """Execute one mapping request with policy-owned 429 decisions."""
        return await self._transport_retry.execute_with_rate_limit_retry(
            path=path,
            retry_count=retry_count,
            send_request=send_request,
            require_mapping_response=self.require_mapping_response,
            handle_rate_limit=self._request_policy.handle_rate_limit,
        )

    def build_iot_headers(self, body: str) -> ResponseHeaders:
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


__all__ = ["RestTransportExecutor"]
