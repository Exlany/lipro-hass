"""Lipro API client for Home Assistant integration."""

from __future__ import annotations

import asyncio
from datetime import datetime
from email.utils import parsedate_to_datetime
import hashlib
import json
import logging
import re
import time
from typing import TYPE_CHECKING, Any

import aiohttp

from ..const import APP_VERSION_CODE, APP_VERSION_NAME, DEVICE_TYPE_MAP
from ..const.config import (
    CONF_ACCESS_TOKEN,
    CONF_BIZ_ID,
    CONF_REFRESH_TOKEN,
    CONF_USER_ID,
)
from .anonymous_share import get_anonymous_share_manager
from .const import (
    CONTENT_TYPE_FORM,
    CONTENT_TYPE_JSON,
    ERROR_AUTH_CODES,
    ERROR_DEVICE_OFFLINE,
    ERROR_DEVICE_OFFLINE_STR,
    ERROR_NO_PERMISSION,
    ERROR_NO_PERMISSION_STR,
    HEADER_ACCESS_TOKEN,
    HEADER_CACHE_CONTROL,
    HEADER_CONTENT_TYPE,
    HEADER_MERCHANT_CODE,
    HEADER_NONCE,
    HEADER_SIGN,
    HEADER_USER_AGENT,
    IOT_API_URL,
    IOT_SIGN_KEY,
    MAX_DEVICES_PER_QUERY,
    MAX_RATE_LIMIT_RETRIES,
    MAX_RETRY_AFTER,
    MERCHANT_CODE,
    PATH_FETCH_DEVICES,
    PATH_GET_MQTT_CONFIG,
    PATH_GET_PRODUCT_CONFIGS,
    PATH_LOGIN,
    PATH_QUERY_CONNECT_STATUS,
    PATH_QUERY_DEVICE_STATUS,
    PATH_QUERY_MESH_GROUP_STATUS,
    PATH_QUERY_OUTLET_POWER,
    PATH_REFRESH_TOKEN,
    PATH_SCHEDULE_ADD,
    PATH_SCHEDULE_DELETE,
    PATH_SCHEDULE_GET,
    PATH_SEND_COMMAND,
    PATH_SEND_GROUP_COMMAND,
    REQUEST_TIMEOUT,
    RESPONSE_SUCCESS,
    RESPONSE_SUCCESS_CODES,
    SMART_HOME_API_URL,
    SMART_HOME_SIGN_KEY,
    USER_AGENT,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

_LOGGER = logging.getLogger(__name__)

# Patterns for sensitive data masking
_SENSITIVE_PATTERNS = (
    (re.compile(r'"access_token"\s*:\s*"[^"]*"'), '"access_token": "***"'),
    (re.compile(r'"refresh_token"\s*:\s*"[^"]*"'), '"refresh_token": "***"'),
    (re.compile(r'"accessToken"\s*:\s*"[^"]*"'), '"accessToken": "***"'),
    (re.compile(r'"refreshToken"\s*:\s*"[^"]*"'), '"refreshToken": "***"'),
    (re.compile(r'"password"\s*:\s*"[^"]*"'), '"password": "***"'),
    (re.compile(r'"phone"\s*:\s*"(\d{3})\d{4}(\d{4})"'), r'"phone": "\1****\2"'),
)


def _mask_sensitive_data(data: str) -> str:
    """Mask sensitive data in log output.

    Args:
        data: String that may contain sensitive data.

    Returns:
        String with sensitive data masked.

    """
    result = data
    for pattern, replacement in _SENSITIVE_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


class LiproApiError(Exception):
    """Base exception for Lipro API errors."""

    def __init__(self, message: str, code: int | str | None = None) -> None:
        """Initialize the exception."""
        super().__init__(message)
        self.code = code


class LiproAuthError(LiproApiError):
    """Authentication error (401 or token expired)."""


class LiproRefreshTokenExpiredError(LiproAuthError):
    """Refresh token expired error (20002, 1202)."""


class LiproConnectionError(LiproApiError):
    """Connection error."""


class LiproRateLimitError(LiproApiError):
    """Rate limit error (429 Too Many Requests)."""

    def __init__(
        self, message: str, retry_after: float | None = None, code: int | str = 429
    ) -> None:
        """Initialize the exception.

        Args:
            message: Error message.
            retry_after: Seconds to wait before retrying (from Retry-After header).
            code: Error code (default 429).

        """
        super().__init__(message, code)
        self.retry_after = retry_after


class LiproClient:
    """Lipro API client with automatic 401 handling and token refresh."""

    def __init__(
        self,
        phone_id: str,
        session: aiohttp.ClientSession | None = None,
        request_timeout: int = REQUEST_TIMEOUT,
    ) -> None:
        """Initialize the client.

        Args:
            phone_id: Device UUID for API signing.
            session: Optional aiohttp session to use.
            request_timeout: Request timeout in seconds.

        """
        self._phone_id = phone_id
        self._session = session
        self._request_timeout = request_timeout
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._user_id: int | None = None
        self._biz_id: str | None = None
        # Callback for token refresh (set by auth manager)
        self._on_token_refresh: Callable[[], Awaitable[None]] | None = None
        # Instance-level lock for preventing concurrent token refresh
        self._refresh_lock: asyncio.Lock = asyncio.Lock()

    @property
    def phone_id(self) -> str:
        """Return the phone ID."""
        return self._phone_id

    @property
    def access_token(self) -> str | None:
        """Return the access token."""
        return self._access_token

    @property
    def refresh_token(self) -> str | None:
        """Return the refresh token."""
        return self._refresh_token

    @property
    def user_id(self) -> int | None:
        """Return the user ID."""
        return self._user_id

    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        user_id: int | None = None,
        biz_id: str | None = None,
    ) -> None:
        """Set authentication tokens.

        Args:
            access_token: The access token.
            refresh_token: The refresh token.
            user_id: Optional user ID.
            biz_id: Optional business ID.

        """
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._user_id = user_id
        self._biz_id = biz_id

    def set_token_refresh_callback(
        self,
        callback: Callable[[], Awaitable[None]] | None,
    ) -> None:
        """Set callback to be called when token needs refresh.

        Args:
            callback: Async function to refresh token.

        """
        self._on_token_refresh = callback

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
        return device_type

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
                    result = await response.json()
                except (json.JSONDecodeError, aiohttp.ContentTypeError) as err:
                    body = await response.text()
                    msg = f"Invalid JSON response from {path} (status={status}): {body[:200]}"
                    raise LiproApiError(msg) from err
        except aiohttp.ClientError as err:
            msg = f"Connection error: {err}"
            raise LiproConnectionError(msg) from err
        except TimeoutError as err:
            msg = "Request timeout"
            raise LiproConnectionError(msg) from err

        _LOGGER.debug(
            "API response from %s: %s",
            path,
            _mask_sensitive_data(json.dumps(result, ensure_ascii=False)[:500]),
        )
        return status, result, headers

    async def _handle_rate_limit(
        self,
        path: str,
        headers: dict[str, str],
        retry_count: int,
    ) -> float:
        """Handle 429 rate limit with exponential backoff.

        Args:
            path: API path (for logging).
            headers: Response headers (may contain Retry-After).
            retry_count: Current retry attempt (0-based).

        Returns:
            Wait time in seconds.

        Raises:
            LiproRateLimitError: If max retries exceeded.

        """
        retry_after = self._parse_retry_after(headers)
        if retry_count >= MAX_RATE_LIMIT_RETRIES:
            _LOGGER.warning(
                "Rate limited on %s after %d retries (retry_after=%s)",
                path,
                MAX_RATE_LIMIT_RETRIES,
                retry_after,
            )
            msg = f"Rate limited after {MAX_RATE_LIMIT_RETRIES} retries"
            raise LiproRateLimitError(msg, retry_after)

        # Cap wait_time to prevent hanging on malicious Retry-After values
        wait_time = min(MAX_RETRY_AFTER, max(0.1, retry_after or (2**retry_count)))
        _LOGGER.debug(
            "Rate limited on %s, waiting %.1fs before retry %d/%d",
            path,
            wait_time,
            retry_count + 1,
            MAX_RATE_LIMIT_RETRIES,
        )
        await asyncio.sleep(wait_time)
        return wait_time

    async def _handle_auth_error_and_retry(
        self,
        path: str,
        old_token: str | None,
        is_retry: bool,
    ) -> bool:
        """Handle auth error by refreshing token.

        Args:
            path: API path (for logging).
            old_token: Token used in the failed request.
            is_retry: Whether this is already a retry attempt.

        Returns:
            True if token was refreshed and request should be retried.

        """
        if is_retry or not self._on_token_refresh:
            return False
        _LOGGER.info("Received auth error from %s, attempting token refresh", path)
        return await self._handle_401_with_refresh(old_token)

    async def _smart_home_request(
        self,
        path: str,
        data: dict[str, Any],
        require_auth: bool = True,
        _is_retry: bool = False,
        _retry_count: int = 0,
    ) -> dict[str, Any]:
        """Make a Smart Home API request with automatic 401/429 handling.

        Args:
            path: API path.
            data: Request data.
            require_auth: Whether authentication is required.
            _is_retry: Internal flag to prevent infinite retry loops.
            _retry_count: Internal counter for rate limit retries.

        Returns:
            Response data.

        Raises:
            LiproAuthError: If authentication fails.
            LiproConnectionError: If connection fails.
            LiproRateLimitError: If rate limited after max retries.
            LiproApiError: If API returns an error.

        """
        session = await self._get_session()
        old_token = self._access_token

        request_data = {
            "sign": self._smart_home_sign(),
            "optFrom": self._phone_id,
            "optAt": self._get_timestamp_ms(),
            "vn": APP_VERSION_NAME,
            "vc": APP_VERSION_CODE,
            **data,
        }

        if require_auth:
            if not self._access_token:
                msg = "No access token available"
                raise LiproAuthError(msg)
            request_data["accessToken"] = self._access_token

        url = f"{SMART_HOME_API_URL}{path}"

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

        # Handle 429 Rate Limit
        if status == 429:
            await self._handle_rate_limit(path, headers, _retry_count)
            return await self._smart_home_request(
                path, data, require_auth, _is_retry, _retry_count=_retry_count + 1
            )

        code = result.get("code")
        if code == RESPONSE_SUCCESS:
            return result.get("value") or result.get("typedValue") or {}

        error_code = result.get("errorCode")
        message = result.get("message", "Unknown error")

        # Check for 401 in response body (hilbert API style)
        # Per docs: some APIs return HTTP 200 with code:401 in body
        is_auth_error = code == 401 or error_code in ("401", "token_expired")

        if is_auth_error:
            if require_auth and await self._handle_auth_error_and_retry(
                path, old_token, _is_retry
            ):
                return await self._smart_home_request(
                    path, data, require_auth, _is_retry=True
                )
            raise LiproAuthError(message, code)

        # Record API error for anonymous share
        _record_api_error(path, code or error_code or 0, message, method="POST")
        raise LiproApiError(message, code)

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

    async def _iot_request(
        self,
        path: str,
        body_data: dict[str, Any],
        _is_retry: bool = False,
        _retry_count: int = 0,
    ) -> dict[str, Any]:
        """Make an IoT API request with automatic 401/429 handling.

        Args:
            path: API path.
            body_data: Request body data.
            _is_retry: Internal flag to prevent infinite retry loops.
            _retry_count: Internal counter for rate limit retries.

        Returns:
            Response data.

        Raises:
            LiproAuthError: If authentication fails.
            LiproConnectionError: If connection fails.
            LiproRateLimitError: If rate limited after max retries.
            LiproApiError: If API returns an error.

        """
        if not self._access_token:
            msg = "No access token available"
            raise LiproAuthError(msg)

        old_token = self._access_token
        session = await self._get_session()
        body = json.dumps(body_data, separators=(",", ":"), ensure_ascii=False)
        req_headers = self._build_iot_headers(body)

        url = f"{IOT_API_URL}{path}"

        status, result, resp_headers = await self._execute_request(
            session.post(
                url,
                data=body,
                headers=req_headers,
                timeout=aiohttp.ClientTimeout(total=self._request_timeout),
            ),
            path,
        )

        # Handle 429 Rate Limit
        if status == 429:
            await self._handle_rate_limit(path, resp_headers, _retry_count)
            return await self._iot_request(
                path, body_data, _is_retry, _retry_count=_retry_count + 1
            )

        # Check HTTP status code for 401 (IoT API style)
        if status == 401:
            if await self._handle_auth_error_and_retry(path, old_token, _is_retry):
                return await self._iot_request(path, body_data, _is_retry=True)
            msg = "HTTP 401 Unauthorized"
            raise LiproAuthError(msg, 401)

        code = result.get("code")
        if code in RESPONSE_SUCCESS_CODES:
            return result.get("data") or result

        message = result.get("message", "Unknown error")

        # Check for auth errors in response body
        if code in ERROR_AUTH_CODES:
            if await self._handle_auth_error_and_retry(path, old_token, _is_retry):
                return await self._iot_request(path, body_data, _is_retry=True)
            raise LiproAuthError(message, code)

        # Record API error for anonymous share
        _record_api_error(path, code or 0, message, method="POST")
        raise LiproApiError(message, code)

    @staticmethod
    def _parse_retry_after(headers: dict[str, str]) -> float | None:
        """Parse Retry-After header value.

        Supports both formats per RFC 7231:
        - Seconds: "Retry-After: 120"
        - HTTP-date: "Retry-After: Wed, 21 Oct 2015 07:28:00 GMT"

        Args:
            headers: Response headers dict.

        Returns:
            Seconds to wait, or None if header not present/invalid.

        """
        retry_after = headers.get("Retry-After") or headers.get("retry-after")
        if not retry_after:
            return None

        # Try parsing as seconds first (most common)
        try:
            return float(retry_after)
        except ValueError:
            pass

        # Try parsing as HTTP-date (RFC 7231)
        try:
            retry_dt = parsedate_to_datetime(retry_after)
            delta = (retry_dt - datetime.now(tz=retry_dt.tzinfo)).total_seconds()
            return max(0.0, delta)  # Don't return negative values
        except (ValueError, TypeError):
            return None

    async def _handle_401_with_refresh(self, old_token: str | None) -> bool:
        """Handle 401 error by refreshing token with concurrency control.

        This implements the same pattern as Android's TokenInterceptor:
        - Use lock to prevent multiple concurrent refresh attempts
        - Double-check if token was already refreshed by another request
        - Call refresh callback to get new token

        Args:
            old_token: The token that was used in the failed request.

        Returns:
            True if token was refreshed successfully, False otherwise.

        """
        if not self._on_token_refresh:
            return False

        async with self._refresh_lock:
            # Double-check: token might have been refreshed by another request
            if self._access_token != old_token and self._access_token is not None:
                _LOGGER.debug(
                    "Token already refreshed by another request, using new token",
                )
                return True

            # Perform the refresh
            try:
                _LOGGER.debug("Executing token refresh")
                await self._on_token_refresh()
                _LOGGER.info("Token refresh successful, retrying request")
                return True
            except LiproRefreshTokenExpiredError:
                _LOGGER.warning("Refresh token expired, re-authentication required")
                raise
            except LiproAuthError as err:
                _LOGGER.warning("Token refresh failed: %s", err)
                return False
            except LiproConnectionError as err:
                _LOGGER.warning("Connection error during token refresh: %s", err)
                return False

    async def login(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> dict[str, Any]:
        """Login with phone number and password.

        Args:
            phone: Phone number.
            password: Password (plain text or MD5 hash).
            password_is_hashed: If True, password is already MD5 hashed.

        Returns:
            Login result containing tokens and user info.

        Raises:
            LiproAuthError: If login fails.

        """
        if password_is_hashed:
            password_hash = password
        else:
            password_hash = hashlib.md5(
                password.encode("utf-8"), usedforsecurity=False
            ).hexdigest()

        result = await self._smart_home_request(
            PATH_LOGIN,
            {
                "phone": phone,
                "password": password_hash,
            },
            require_auth=False,
        )

        access_token = result.get("access_token")
        refresh_token = result.get("refresh_token")
        if not access_token or not refresh_token:
            msg = "Login response missing access_token or refresh_token"
            raise LiproAuthError(msg)

        self._access_token = access_token
        self._refresh_token = refresh_token
        self._user_id = result.get("userId")
        self._biz_id = result.get("bizId")

        _LOGGER.info("Login successful")

        return {
            CONF_ACCESS_TOKEN: self._access_token,
            CONF_REFRESH_TOKEN: self._refresh_token,
            CONF_USER_ID: self._user_id,
            CONF_BIZ_ID: self._biz_id,
            "phone": result.get("phone"),
            "user_name": result.get("userName"),
        }

    async def login_with_hash(self, phone: str, password_hash: str) -> dict[str, Any]:
        """Login with phone number and pre-hashed password.

        This is a convenience method for login with already hashed password.

        Args:
            phone: Phone number.
            password_hash: MD5 hash of the password.

        Returns:
            Login result containing tokens and user info.

        Raises:
            LiproAuthError: If login fails.

        """
        return await self.login(phone, password_hash, password_is_hashed=True)

    async def refresh_access_token(self) -> dict[str, Any]:
        """Refresh the access token.

        Returns:
            New tokens.

        Raises:
            LiproAuthError: If refresh fails.

        """
        if not self._refresh_token:
            msg = "No refresh token available"
            raise LiproAuthError(msg)

        result = await self._smart_home_request(
            PATH_REFRESH_TOKEN,
            {
                "refreshToken": self._refresh_token,
                "model": "HomeAssistant",
            },
            require_auth=False,
        )

        access_token = result.get("access_token")
        refresh_token = result.get("refresh_token")
        if not access_token or not refresh_token:
            msg = "Refresh response missing access_token or refresh_token"
            raise LiproAuthError(msg)

        self._access_token = access_token
        self._refresh_token = refresh_token
        self._user_id = result.get("userId")

        _LOGGER.info("Token refreshed successfully")

        return {
            CONF_ACCESS_TOKEN: self._access_token,
            CONF_REFRESH_TOKEN: self._refresh_token,
            CONF_USER_ID: self._user_id,
        }

    async def get_devices(self, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """Get all devices.

        Args:
            offset: Pagination offset.
            limit: Number of devices to fetch.

        Returns:
            Device list and order info.

        """
        return await self._smart_home_request(
            PATH_FETCH_DEVICES,
            {
                "offset": offset,
                "limit": limit,
            },
        )

    async def get_product_configs(self) -> list[dict[str, Any]]:
        """Get all product configurations.

        This is a public API that doesn't require authentication.
        Returns product specs including color temperature ranges.

        Returns:
            List of product configurations.

        """
        # _smart_home_request extracts the "value" field from the response.
        # For this endpoint, "value" is a JSON array, so the runtime type
        # is list despite the dict[str, Any] return annotation.
        result: Any = await self._smart_home_request(
            PATH_GET_PRODUCT_CONFIGS,
            {},
            require_auth=False,
        )
        if isinstance(result, list):
            return result
        return []

    @staticmethod
    def _is_retriable_device_error(err: LiproApiError) -> bool:
        """Check if the error is a retriable device error (offline/no permission).

        Args:
            err: The API error to check.

        Returns:
            True if the error should trigger fallback to individual queries.

        """
        return err.code in (
            ERROR_DEVICE_OFFLINE,
            ERROR_DEVICE_OFFLINE_STR,
            ERROR_NO_PERMISSION,
            ERROR_NO_PERMISSION_STR,
        )

    @staticmethod
    def _extract_data_list(result: Any) -> list[dict[str, Any]]:
        """Extract a list of data items from an API result.

        The API may return either a list directly or a dict with a "data" key.

        Args:
            result: API response data.

        Returns:
            List of data items.

        """
        if isinstance(result, list):
            return result
        if isinstance(result, dict) and "data" in result:
            return result["data"]  # type: ignore[no-any-return]
        return []

    async def _query_with_fallback(
        self,
        path: str,
        body_key: str,
        ids: list[str],
        item_name: str,
    ) -> list[dict[str, Any]]:
        """Query API with automatic fallback to individual queries on retriable errors.

        Args:
            path: API endpoint path.
            body_key: Request body key for the ID list (e.g., "deviceIdList").
            ids: List of IDs to query.
            item_name: Human-readable name for logging (e.g., "device", "group").

        Returns:
            List of status data items.

        """
        try:
            result = await self._iot_request(path, {body_key: ids})
            return self._extract_data_list(result)
        except LiproApiError as err:
            if not self._is_retriable_device_error(err):
                raise
            _LOGGER.warning(
                "Batch %s query failed (%s offline?): %s. "
                "Falling back to individual queries.",
                item_name,
                item_name,
                err,
            )
            all_results: list[dict[str, Any]] = []
            for item_id in ids:
                try:
                    single_result = await self._iot_request(path, {body_key: [item_id]})
                    all_results.extend(self._extract_data_list(single_result))
                except LiproApiError as single_err:
                    _LOGGER.debug(
                        "Failed to query %s %s: %s (code: %s)",
                        item_name,
                        item_id,
                        single_err,
                        single_err.code,
                    )
            return all_results

    async def query_device_status(self, device_ids: list[str]) -> list[dict[str, Any]]:
        """Query status of multiple devices.

        Args:
            device_ids: List of IoT device IDs (format: "03ab" + MAC).

        Returns:
            List of device status data.

        Note:
            If a device is offline, the API may return error 140003.
            In this case, we fall back to querying devices one by one.

        """
        if not device_ids:
            return []

        all_results: list[dict[str, Any]] = []
        for i in range(0, len(device_ids), MAX_DEVICES_PER_QUERY):
            batch = device_ids[i : i + MAX_DEVICES_PER_QUERY]
            all_results.extend(
                await self._query_with_fallback(
                    PATH_QUERY_DEVICE_STATUS, "deviceIdList", batch, "device"
                )
            )
        return all_results

    async def query_mesh_group_status(
        self,
        group_ids: list[str],
    ) -> list[dict[str, Any]]:
        """Query status of Mesh groups.

        Args:
            group_ids: List of Mesh group IDs.

        Returns:
            List of group status data.

        Note:
            If a group has offline devices, the API may return error 140003.
            In this case, we fall back to querying groups one by one.

        """
        if not group_ids:
            return []

        return await self._query_with_fallback(
            PATH_QUERY_MESH_GROUP_STATUS, "groupIdList", group_ids, "group"
        )

    async def query_connect_status(
        self,
        device_ids: list[str],
    ) -> dict[str, bool]:
        """Query real-time connection status for devices.

        This provides more accurate online/offline status than the cached
        connectState property from device status queries.

        Args:
            device_ids: List of device IoT IDs.

        Returns:
            Dict mapping device IoT ID to online status (True=online, False=offline).

        """
        if not device_ids:
            return {}

        try:
            # _iot_request returns dict[str, Any], but we use Any to allow
            # the defensive isinstance check below without type: ignore.
            result: Any = await self._iot_request(
                PATH_QUERY_CONNECT_STATUS,
                {"deviceIdList": device_ids},
            )

            # API returns Map<String, Boolean>
            if isinstance(result, dict):
                # Convert string "true"/"false" to bool if needed
                return {
                    k: v if isinstance(v, bool) else str(v).lower() == "true"
                    for k, v in result.items()
                }
            return {}
        except LiproApiError as err:
            _LOGGER.debug(
                "Failed to query connect status for %s: %s",
                device_ids,
                err,
            )
            return {}

    async def send_command(
        self,
        device_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> dict[str, Any]:
        """Send a command to a device.

        Args:
            device_id: Device ID.
            command: Command name (e.g., POWER_ON, CHANGE_STATE).
            device_type: Device type (integer or hex string).
            properties: Optional list of property key-value pairs.
            iot_name: Optional IoT name/model.

        Returns:
            Command result.

        """
        device_type_hex = self._to_device_type_hex(device_type)

        body = {
            "command": command,
            "deviceId": device_id,
            "deviceType": device_type_hex,
            "iotName": iot_name,
            "properties": properties or [],
            "skuId": "",
            "hasMacRule": False,
        }

        return await self._iot_request(PATH_SEND_COMMAND, body)

    async def send_group_command(
        self,
        group_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> dict[str, Any]:
        """Send a command to a Mesh group.

        Args:
            group_id: Mesh group ID.
            command: Command name.
            device_type: Device type of devices in the group.
            properties: Optional list of property key-value pairs.
            iot_name: Optional IoT name/model (e.g., "20X1").

        Returns:
            Command result.

        """
        device_type_hex = self._to_device_type_hex(device_type)

        body = {
            "command": command,
            "deviceId": group_id,
            "deviceType": device_type_hex,
            "groupId": group_id,
            "iotName": iot_name,
            "properties": properties or [],
            "skuId": "",
            "hasMacRule": False,
        }

        return await self._iot_request(PATH_SEND_GROUP_COMMAND, body)

    async def get_mqtt_config(
        self,
        _is_retry: bool = False,
        _retry_count: int = 0,
    ) -> dict[str, Any]:
        """Get MQTT configuration for real-time status updates.

        Args:
            _is_retry: Internal flag to prevent infinite retry loops.
            _retry_count: Internal counter for rate limit retries.

        Returns:
            Dict containing encrypted accessKey and secretKey.
            These need to be decrypted using the MQTT AES key.

        Raises:
            LiproAuthError: If authentication fails.
            LiproRateLimitError: If rate limited after max retries.
            LiproApiError: If API returns an error.

        Note:
            This endpoint returns a non-standard response format:
            ``{"accessKey": "...", "secretKey": "..."}``
            without the usual ``code``/``data`` wrapper, so we bypass
            ``_iot_request`` and issue the HTTP call directly.

        """
        if not self._access_token:
            msg = "No access token available"
            raise LiproAuthError(msg)

        old_token = self._access_token
        session = await self._get_session()
        body = json.dumps({}, separators=(",", ":"), ensure_ascii=False)
        req_headers = self._build_iot_headers(body)

        url = f"{IOT_API_URL}{PATH_GET_MQTT_CONFIG}"

        status, result, resp_headers = await self._execute_request(
            session.post(
                url,
                data=body,
                headers=req_headers,
                timeout=aiohttp.ClientTimeout(total=self._request_timeout),
            ),
            PATH_GET_MQTT_CONFIG,
        )

        # Handle 429 Rate Limit
        if status == 429:
            await self._handle_rate_limit(
                PATH_GET_MQTT_CONFIG, resp_headers, _retry_count
            )
            return await self.get_mqtt_config(_is_retry, _retry_count=_retry_count + 1)

        # Handle 401 with token refresh retry
        if status == 401:
            if await self._handle_auth_error_and_retry(
                PATH_GET_MQTT_CONFIG, old_token, _is_retry
            ):
                return await self.get_mqtt_config(_is_retry=True)
            msg = "HTTP 401 Unauthorized"
            raise LiproAuthError(msg, 401)

        # This endpoint returns {"accessKey": "...", "secretKey": "..."} directly
        if "accessKey" in result and "secretKey" in result:
            return result

        # Fallback: if the API ever wraps it in standard format
        code = result.get("code")
        if code in RESPONSE_SUCCESS_CODES:
            return result.get("data") or result

        message = result.get("message", "Unknown error")
        raise LiproApiError(message, code)

    async def fetch_outlet_power_info(
        self,
        device_ids: list[str],
    ) -> dict[str, Any]:
        """Fetch power information for outlet devices.

        Args:
            device_ids: List of outlet device IDs (IoT IDs).

        Returns:
            Dict containing:
                - nowPower: Current power in watts (W)
                - energyList: Array of daily energy records (max 90 days) with:
                    - t: Date string (YYYYMMDD format)
                    - v: Energy value in kWh

        Raises:
            LiproAuthError: If authentication fails.
            LiproApiError: If API returns an error.

        """
        return await self._iot_request(
            PATH_QUERY_OUTLET_POWER,
            {"deviceIds": device_ids},
        )

    # ==================== Timing Task APIs ====================

    async def get_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
    ) -> list[dict[str, Any]]:
        """Get timing schedules for a device.

        Args:
            device_id: Device IoT ID.
            device_type: Device type (integer or hex string).

        Returns:
            List of timing schedules, each containing:
                - id: Schedule ID
                - active: Whether schedule is active
                - schedule: Dict with days, time, evt arrays

        """
        device_type_hex = self._to_device_type_hex(device_type)

        result = await self._iot_request(
            PATH_SCHEDULE_GET,
            {
                "deviceId": device_id,
                "deviceType": device_type_hex,
            },
        )

        return result.get("timings", [])  # type: ignore[no-any-return]

    async def add_device_schedule(
        self,
        device_id: str,
        device_type: int | str,
        days: list[int],
        times: list[int],
        events: list[int],
        group_id: str = "",
    ) -> list[dict[str, Any]]:
        """Add or update a timing schedule for a device.

        Args:
            device_id: Device IoT ID.
            device_type: Device type (integer or hex string).
            days: List of weekdays (1=Monday, 7=Sunday).
            times: List of times in seconds from midnight.
            events: List of event codes (0=light on, 1=light off, etc.).
            group_id: Optional group ID for mesh devices.

        Returns:
            Updated list of timing schedules.

        Note:
            times and events arrays must have the same length.
            Each time[i] corresponds to events[i].

        Event codes:
            - 0: Light on
            - 1: Light off
            - 200: Outlet on
            - 201: Outlet off
            - 300/310: Switch left key on/off
            - 301/311: Switch middle key on/off
            - 302/312: Switch right key on/off
            - 400/401: Fan on/off

        """
        if len(times) != len(events):
            msg = "times and events arrays must have the same length"
            raise ValueError(msg)

        device_type_hex = self._to_device_type_hex(device_type)

        result = await self._iot_request(
            PATH_SCHEDULE_ADD,
            {
                "deviceId": device_id,
                "deviceType": device_type_hex,
                "scheduleInfo": {
                    "days": days,
                    "time": times,
                    "evt": events,
                },
                "groupId": group_id,
                "singleBle": False,
            },
        )

        return result.get("timings", [])  # type: ignore[no-any-return]

    async def delete_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        schedule_ids: list[int],
        group_id: str = "",
    ) -> list[dict[str, Any]]:
        """Delete timing schedules for a device.

        Args:
            device_id: Device IoT ID.
            device_type: Device type (integer or hex string).
            schedule_ids: List of schedule IDs to delete.
            group_id: Optional group ID for mesh devices.

        Returns:
            Remaining list of timing schedules.

        """
        device_type_hex = self._to_device_type_hex(device_type)

        result = await self._iot_request(
            PATH_SCHEDULE_DELETE,
            {
                "deviceId": device_id,
                "deviceType": device_type_hex,
                "idList": schedule_ids,
                "groupId": group_id,
                "singleBle": False,
            },
        )

        return result.get("timings", [])  # type: ignore[no-any-return]


def _record_api_error(
    endpoint: str, code: str | int, message: str, method: str = ""
) -> None:
    """Record API error for anonymous share.

    Args:
        endpoint: The API endpoint that failed.
        code: The error code.
        message: The error message.
        method: The HTTP method (e.g., "POST").

    """
    share_manager = get_anonymous_share_manager()
    share_manager.record_api_error(endpoint, code, message, method=method)
