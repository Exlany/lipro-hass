"""HTTP transport and request pipeline for LiproClient."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import TYPE_CHECKING, Any

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
    IOT_SIGN_KEY,
    MERCHANT_CODE,
    SMART_HOME_API_URL,
    SMART_HOME_SIGN_KEY,
    USER_AGENT,
)
from ...const.base import APP_VERSION_CODE, APP_VERSION_NAME
from ...const.device_types import DEVICE_TYPE_MAP
from . import response_safety as _response_safety
from .client_auth_recovery import _ClientAuthRecoveryMixin
from .errors import LiproApiError, LiproAuthError, LiproConnectionError
from .request_codec import (
    build_smart_home_request_data,
    encode_iot_request_body,
    extract_smart_home_success_payload,
)
from .response_safety import (
    DEVICE_TYPE_HEX_PATTERN as _DEVICE_TYPE_HEX_PATTERN,
    INVALID_JSON_BODY_READ_MAX_BYTES as _INVALID_JSON_BODY_READ_MAX_BYTES,
    INVALID_JSON_LOG_PREVIEW_MAX_CHARS as _INVALID_JSON_LOG_PREVIEW_MAX_CHARS,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


# Use the same logger instance as custom_components.lipro.core.api.client._LOGGER
# so tests patching client._LOGGER.* still intercept logs here.
_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")


class _ClientTransportMixin(_ClientAuthRecoveryMixin):
    """Mixin implementing HTTP request transport and mapping pipelines."""

    def _init_transport(
        self,
        *,
        phone_id: str,
        session: aiohttp.ClientSession | None,
        request_timeout: int,
    ) -> None:
        """Initialize transport-specific runtime state.

        Keeping this initialization here clarifies ownership of the fields that
        back request signing and session management.
        """
        self._phone_id = phone_id
        self._session = session
        self._request_timeout = request_timeout

    @property
    def phone_id(self) -> str:
        """Return the phone ID used for API signing."""
        return self._phone_id

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get the aiohttp session.

        Raises:
            LiproConnectionError: If no session is available.

        """
        if self._session is None or self._session.closed:
            msg = "No aiohttp session available (must be injected via constructor)"
            raise LiproConnectionError(msg)
        return self._session

    async def close(self) -> None:
        """Close the client session (no-op: HA-injected session is managed by HA)."""
        self._session = None

    def _smart_home_sign(self) -> str:
        """Generate Smart Home API signature.

        Returns:
            MD5 signature string.

        """
        sign_data = f"{self._phone_id}{SMART_HOME_SIGN_KEY}"
        return hashlib.md5(sign_data.encode("utf-8"), usedforsecurity=False).hexdigest()

    def _iot_sign(self, nonce: int, body: str) -> str:
        """Generate IoT API signature.

        Args:
            nonce: Timestamp in milliseconds.
            body: Request body JSON string.

        Returns:
            MD5 signature string.

        Note:
            Per API docs, body should be trimmed before signing.
            json.dumps() output has no leading/trailing whitespace,
            but we call strip() explicitly for safety.

        """
        trimmed_body = body.strip() if body else ""
        sign_data = (
            f"{self._access_token}{nonce}{MERCHANT_CODE}{trimmed_body}{IOT_SIGN_KEY}"
        )
        return hashlib.md5(sign_data.encode("utf-8"), usedforsecurity=False).hexdigest()

    def _to_device_type_hex(self, device_type: int | str) -> str:
        """Convert device type to hex string format.

        Args:
            device_type: Device type as integer or hex string.

        Returns:
            Device type as hex string (e.g., "ff000001").

        """
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

    def _get_timestamp_ms(self) -> int:
        """Get current timestamp in milliseconds."""
        return int(time.time() * 1000)

    async def _execute_request(
        self,
        request_ctx: Any,
        path: str,
    ) -> tuple[int, dict[str, Any], dict[str, str]]:
        """Execute an HTTP request with common error handling.

        Args:
            request_ctx: The context manager from session.post().
            path: API path (for logging).

        Returns:
            Tuple of (HTTP status code, parsed JSON response body, response headers).

        Raises:
            LiproConnectionError: If connection fails or times out.

        """
        try:
            async with request_ctx as response:
                status = response.status
                headers = dict(response.headers)
                try:
                    try:
                        result = await response.json(content_type=None)
                    except TypeError:
                        result = await response.json()
                except (json.JSONDecodeError, aiohttp.ContentTypeError) as err:
                    body_length: int | None = response.content_length
                    preview_bytes: Any

                    body_bytes: bytes | None = getattr(response, "_body", None)
                    if isinstance(body_bytes, bytes):
                        body_length = len(body_bytes)
                        preview_bytes = body_bytes[:_INVALID_JSON_BODY_READ_MAX_BYTES]
                        truncated = len(body_bytes) > _INVALID_JSON_BODY_READ_MAX_BYTES
                    else:
                        preview_bytes = await response.content.read(
                            _INVALID_JSON_BODY_READ_MAX_BYTES + 1
                        )
                        truncated = (
                            len(preview_bytes) > _INVALID_JSON_BODY_READ_MAX_BYTES
                        )
                        if truncated:
                            preview_bytes = preview_bytes[
                                :_INVALID_JSON_BODY_READ_MAX_BYTES
                            ]

                    if not isinstance(preview_bytes, (bytes, bytearray)):
                        preview_bytes = b""
                    else:
                        preview_bytes = bytes(preview_bytes)

                    charset = response.charset or "utf-8"
                    try:
                        preview_text = preview_bytes.decode(
                            charset,
                            errors="replace",
                        )
                    except (LookupError, TypeError):
                        preview_text = preview_bytes.decode(
                            "utf-8",
                            errors="replace",
                        )
                    masked_preview = _response_safety.mask_sensitive_data(preview_text)
                    masked_preview = masked_preview[
                        :_INVALID_JSON_LOG_PREVIEW_MAX_CHARS
                    ]
                    _LOGGER.debug(
                        "Invalid JSON response preview from %s: %s",
                        path,
                        masked_preview,
                    )
                    if truncated:
                        _LOGGER.debug(
                            "Invalid JSON response from %s truncated at %d bytes",
                            path,
                            _INVALID_JSON_BODY_READ_MAX_BYTES,
                        )
                    msg = (
                        f"Invalid JSON response from {path} "
                        f"(status={status}, body_length={body_length})"
                    )
                    raise LiproApiError(msg) from err
        except aiohttp.ClientError as err:
            msg = f"Connection error: {err}"
            raise LiproConnectionError(msg) from err
        except TimeoutError as err:
            msg = "Request timeout"
            raise LiproConnectionError(msg) from err

        if _LOGGER.isEnabledFor(logging.DEBUG):
            summary: dict[str, Any] = {"type": type(result).__name__}
            if isinstance(result, dict):
                summary["keys_count"] = len(result)
                for key in ("code", "errorCode", "success"):
                    if key in result:
                        summary[key] = result.get(key)
            elif isinstance(result, list):
                summary["len"] = len(result)
            _LOGGER.debug(
                "API response from %s: %s",
                path,
                json.dumps(summary, ensure_ascii=False),
            )
        return status, result, headers

    @staticmethod
    def _require_mapping_response(path: str, result: Any) -> dict[str, Any]:
        """Validate that an API response payload is a JSON object."""
        if isinstance(result, dict):
            return result
        msg = (
            f"Invalid JSON response from {path}: "
            f"expected object, got {type(result).__name__}"
        )
        raise LiproApiError(msg)

    async def _execute_mapping_request_with_rate_limit(
        self,
        *,
        path: str,
        retry_count: int,
        send_request: Callable[
            [],
            Awaitable[tuple[int, Any, dict[str, str], str | None]],
        ],
    ) -> tuple[int, dict[str, Any], str | None]:
        """Execute mapping request with shared 429 retry and payload validation."""
        status, result, headers, request_token = await send_request()
        if status == 429:
            await self._handle_rate_limit(path, headers, retry_count)
            return await self._execute_mapping_request_with_rate_limit(
                path=path,
                retry_count=retry_count + 1,
                send_request=send_request,
            )
        return status, self._require_mapping_response(path, result), request_token

    async def _request_smart_home_mapping(
        self,
        path: str,
        data: dict[str, Any],
        require_auth: bool = True,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        """Execute one Smart Home HTTP request and return validated mapping payload.

        Handles the shared request pipeline for Smart Home endpoints:
        optional token precheck, form payload build, and 429 backoff retries.
        """
        url = f"{SMART_HOME_API_URL}{path}"

        async def _send_request() -> tuple[int, Any, dict[str, str], str | None]:
            request_token = self._access_token
            if require_auth and not request_token:
                msg = "No access token available"
                raise LiproAuthError(msg)

            request_data = build_smart_home_request_data(
                sign=self._smart_home_sign(),
                phone_id=self._phone_id,
                timestamp_ms=self._get_timestamp_ms(),
                app_version_name=APP_VERSION_NAME,
                app_version_code=APP_VERSION_CODE,
                data=data,
                access_token=request_token if require_auth else None,
            )

            session = await self._get_session()
            status, result, headers = await self._execute_request(
                session.post(
                    url,
                    data=request_data,
                    headers={
                        HEADER_CONTENT_TYPE: CONTENT_TYPE_FORM,
                        HEADER_USER_AGENT: USER_AGENT,
                    },
                    timeout=aiohttp.ClientTimeout(total=self._request_timeout),
                ),
                path,
            )
            return status, result, headers, request_token

        _, result, request_token = await self._execute_mapping_request_with_rate_limit(
            path=path,
            retry_count=retry_count,
            send_request=_send_request,
        )
        return result, request_token

    async def _smart_home_request(
        self,
        path: str,
        data: dict[str, Any],
        require_auth: bool = True,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        """Make a Smart Home API request with automatic 401/429 handling.

        Args:
            path: API path.
            data: Request data.
            require_auth: Whether authentication is required.
            is_retry: Internal flag to prevent infinite retry loops.
            retry_count: Internal counter for rate limit retries.

        Returns:
            Response data.

        Raises:
            LiproAuthError: If authentication fails.
            LiproConnectionError: If connection fails.
            LiproRateLimitError: If rate limited after max retries.
            LiproApiError: If API returns an error.

        """
        result, request_token = await self._request_smart_home_mapping(
            path,
            data,
            require_auth=require_auth,
            is_retry=is_retry,
            retry_count=retry_count,
        )
        return await self._finalize_mapping_result(
            path=path,
            result=result,
            request_token=request_token,
            is_retry=is_retry,
            retry_on_auth_error=require_auth,
            retry_request=(
                lambda: self._smart_home_request(
                    path,
                    data,
                    require_auth,
                    is_retry=True,
                )
            ),
            success_payload=extract_smart_home_success_payload,
        )

    def _build_iot_headers(self, body: str) -> dict[str, str]:
        """Build common IoT API request headers.

        Args:
            body: JSON-encoded request body (used for signature generation).

        Returns:
            Headers dict for the IoT API request.

        """
        nonce = self._get_timestamp_ms()
        sign = self._iot_sign(nonce, body)
        return {
            HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
            HEADER_CACHE_CONTROL: "no-cache",
            HEADER_USER_AGENT: USER_AGENT,
            HEADER_ACCESS_TOKEN: self._access_token or "",
            HEADER_MERCHANT_CODE: MERCHANT_CODE,
            HEADER_NONCE: str(nonce),
            HEADER_SIGN: sign,
        }

    async def _request_iot_mapping_raw(
        self,
        path: str,
        body: str,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        """Execute one IoT HTTP request with a pre-encoded body string."""
        url = f"{IOT_API_URL}{path}"

        async def _send_request() -> tuple[int, Any, dict[str, str], str | None]:
            request_token = self._access_token
            if not request_token:
                msg = "No access token available"
                raise LiproAuthError(msg)

            session = await self._get_session()
            req_headers = self._build_iot_headers(body)
            status, result, resp_headers = await self._execute_request(
                session.post(
                    url,
                    data=body,
                    headers=req_headers,
                    timeout=aiohttp.ClientTimeout(total=self._request_timeout),
                ),
                path,
            )
            return status, result, resp_headers, request_token

        (
            status,
            result,
            request_token,
        ) = await self._execute_mapping_request_with_rate_limit(
            path=path,
            retry_count=retry_count,
            send_request=_send_request,
        )

        if status == 401:
            if await self._handle_auth_error_and_retry(path, request_token, is_retry):
                return await self._request_iot_mapping_raw(
                    path,
                    body,
                    is_retry=True,
                )
            msg = "HTTP 401 Unauthorized"
            raise LiproAuthError(msg, 401)

        return result, request_token

    async def _request_iot_mapping(
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        """Execute one IoT HTTP request and return validated mapping payload.

        Handles the shared request pipeline for IoT endpoints:
        token precheck, signed headers, 429 backoff retries, and HTTP 401 retry.
        """
        body = encode_iot_request_body(body_data)
        return await self._request_iot_mapping_raw(
            path,
            body,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def _iot_request(
        self,
        path: str,
        body_data: dict[str, Any],
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        """Make an IoT API request with automatic 401/429 handling.

        Args:
            path: API path.
            body_data: Request body data.
            is_retry: Internal flag to prevent infinite retry loops.
            retry_count: Internal counter for rate limit retries.

        Returns:
            Response data.

        Raises:
            LiproAuthError: If authentication fails.
            LiproConnectionError: If connection fails.
            LiproRateLimitError: If rate limited after max retries.
            LiproApiError: If API returns an error.

        """
        result, request_token = await self._request_iot_mapping(
            path,
            body_data,
            is_retry=is_retry,
            retry_count=retry_count,
        )
        return await self._finalize_mapping_result(
            path=path,
            result=result,
            request_token=request_token,
            is_retry=is_retry,
            retry_on_auth_error=True,
            retry_request=lambda: self._iot_request(path, body_data, is_retry=True),
            success_payload=self._unwrap_iot_success_payload,
        )
