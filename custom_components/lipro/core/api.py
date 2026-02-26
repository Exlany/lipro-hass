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
from typing import TYPE_CHECKING, Any, TypeVar

import aiohttp

from ..const import (
    APP_VERSION_CODE,
    APP_VERSION_NAME,
    DEVICE_TYPE_MAP,
    IOT_DEVICE_ID_PREFIX,
)
from ..const.api import (
    CONTENT_TYPE_FORM,
    CONTENT_TYPE_JSON,
    ERROR_AUTH_CODES,
    ERROR_DEVICE_BUSY,
    ERROR_DEVICE_BUSY_STR,
    ERROR_DEVICE_NOT_CONNECTED,
    ERROR_DEVICE_NOT_CONNECTED_STR,
    ERROR_DEVICE_OFFLINE,
    ERROR_DEVICE_OFFLINE_STR,
    ERROR_INVALID_PARAM,
    ERROR_INVALID_PARAM_STR,
    ERROR_NO_PERMISSION,
    ERROR_NO_PERMISSION_STR,
    ERROR_REFRESH_TOKEN_EXPIRED,
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
    PATH_BLE_SCHEDULE_ADD,
    PATH_BLE_SCHEDULE_DELETE,
    PATH_BLE_SCHEDULE_GET,
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
    RESPONSE_SUCCESS_CODES,
    SMART_HOME_API_URL,
    SMART_HOME_SIGN_KEY,
    USER_AGENT,
)
from ..const.config import (
    CONF_ACCESS_TOKEN,
    CONF_BIZ_ID,
    CONF_REFRESH_TOKEN,
    CONF_USER_ID,
)
from .anonymous_share import get_anonymous_share_manager
from .request_codec import (
    build_smart_home_request_data,
    encode_iot_request_body,
    extract_smart_home_success_payload,
)
from .schedule_codec import (
    coerce_int_list as _coerce_schedule_int_list,
    normalize_mesh_timing_rows as _normalize_mesh_schedule_rows,
    parse_mesh_schedule_json as _parse_mesh_schedule_payload,
)
from .schedule_endpoint import (
    build_mesh_schedule_add_body,
    build_mesh_schedule_delete_body,
    build_mesh_schedule_get_body,
    build_schedule_add_body,
    build_schedule_delete_body,
    build_schedule_get_body,
    encode_mesh_schedule_json,
    is_mesh_group_id,
    resolve_mesh_schedule_candidate_ids,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

_LOGGER = logging.getLogger(__name__)

# Retry settings for transient command-busy responses from device cloud.
_COMMAND_BUSY_RETRY_MAX_ATTEMPTS = 3
_COMMAND_BUSY_RETRY_BASE_DELAY_SECONDS = 0.25
# Minimum interval between CHANGE_STATE sends to the same target.
_CHANGE_STATE_MIN_INTERVAL_SECONDS = 0.2
# Adaptive pacing tuning for CHANGE_STATE per target.
_CHANGE_STATE_MAX_INTERVAL_SECONDS = 1.2
_CHANGE_STATE_BUSY_MULTIPLIER = 1.6
_CHANGE_STATE_RECOVERY_MULTIPLIER = 0.8
# Max tracked targets for command pacing cache.
_COMMAND_PACING_CACHE_MAX_SIZE = 256
_INVALID_JSON_MASK_INPUT_MAX_CHARS = 2048
_INVALID_JSON_LOG_PREVIEW_MAX_CHARS = 200

# Patterns for sensitive data masking
_SENSITIVE_PATTERNS = (
    (re.compile(r'"access_token"\s*:\s*"[^"]*"'), '"access_token": "***"'),
    (re.compile(r'"refresh_token"\s*:\s*"[^"]*"'), '"refresh_token": "***"'),
    (re.compile(r'"accessToken"\s*:\s*"[^"]*"'), '"accessToken": "***"'),
    (re.compile(r'"refreshToken"\s*:\s*"[^"]*"'), '"refreshToken": "***"'),
    (re.compile(r'"accessKey"\s*:\s*"[^"]*"'), '"accessKey": "***"'),
    (re.compile(r'"secretKey"\s*:\s*"[^"]*"'), '"secretKey": "***"'),
    (re.compile(r'"password"\s*:\s*"[^"]*"'), '"password": "***"'),
    (re.compile(r'"phone"\s*:\s*"(\d{3})\d{4}(\d{4})"'), r'"phone": "\1****\2"'),
)

_IOT_DEVICE_ID_PATTERN = re.compile(
    rf"^{re.escape(IOT_DEVICE_ID_PREFIX)}[0-9a-f]{{12}}$",
    re.IGNORECASE,
)
_DEVICE_TYPE_HEX_PATTERN = re.compile(r"^[0-9a-f]{8}$", re.IGNORECASE)

_MappingPayloadT = TypeVar("_MappingPayloadT")


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


def _coerce_connect_status(value: Any) -> bool:
    """Normalize backend connection-state variants to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off", ""}:
            return False
        _LOGGER.debug("Unexpected connect-status string value: %r", value)
        return False
    if value is None:
        return False
    _LOGGER.debug(
        "Unexpected connect-status value type: %s (%r)",
        type(value).__name__,
        value,
    )
    return False


def _normalize_iot_device_id(device_id: Any) -> str | None:
    """Normalize and validate IoT device IDs.

    Returns canonical lowercase ID if valid, otherwise ``None``.
    """
    if not isinstance(device_id, str):
        return None
    normalized = device_id.strip().lower()
    if not normalized:
        return None
    if not _IOT_DEVICE_ID_PATTERN.fullmatch(normalized):
        return None
    return normalized


def _normalize_response_code(code: Any) -> int | str | None:
    """Normalize API response codes for robust comparisons.

    Handles backend differences such as:
    - int codes (200, 401, 140003)
    - numeric strings ("0000", "200", "2001")
    - strings with accidental spaces (" 0000 ")
    - symbolic string codes ("token_expired")
    """
    if code is None:
        return None
    if isinstance(code, bool):
        return int(code)
    if isinstance(code, int):
        return code
    if isinstance(code, float):
        if code.is_integer():
            return int(code)
        return str(code).strip()
    if isinstance(code, str):
        normalized = code.strip()
        if not normalized:
            return None
        if normalized.lstrip("+-").isdigit():
            try:
                return int(normalized, 10)
            except ValueError:
                return normalized
        return normalized
    return str(code).strip()


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
        # Per-target pacing state for high-frequency CHANGE_STATE commands.
        self._command_pacing_lock: asyncio.Lock = asyncio.Lock()
        self._last_change_state_at: dict[str, float] = {}
        self._change_state_min_interval: dict[str, float] = {}
        self._change_state_busy_count: dict[str, int] = {}

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
                    result = await response.json()
                except (json.JSONDecodeError, aiohttp.ContentTypeError) as err:
                    body = await response.text()
                    masked_preview = _mask_sensitive_data(
                        body[:_INVALID_JSON_MASK_INPUT_MAX_CHARS]
                    )[:_INVALID_JSON_LOG_PREVIEW_MAX_CHARS]
                    _LOGGER.debug(
                        "Invalid JSON response preview from %s: %s",
                        path,
                        masked_preview,
                    )
                    msg = (
                        f"Invalid JSON response from {path} "
                        f"(status={status}, body_length={len(body)})"
                    )
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

    @staticmethod
    def _is_auth_error_code(code: Any) -> bool:
        """Check whether an API code represents an authentication failure."""
        normalized = _normalize_response_code(code)
        if isinstance(normalized, str) and normalized.lower() == "token_expired":
            return True
        return (
            normalized in ERROR_AUTH_CODES or normalized in ERROR_REFRESH_TOKEN_EXPIRED
        )

    @staticmethod
    def _is_success_code(code: Any) -> bool:
        """Check whether an API code represents success."""
        normalized = _normalize_response_code(code)
        return normalized in RESPONSE_SUCCESS_CODES

    @classmethod
    def _resolve_auth_error_code(
        cls,
        code: Any,
        error_code: Any,
    ) -> int | str | None:
        """Pick the most relevant auth code from response code/errorCode fields."""
        if cls._is_auth_error_code(code):
            normalized = _normalize_response_code(code)
            if isinstance(normalized, str) and normalized.lower() == "token_expired":
                return "token_expired"
            return normalized
        if cls._is_auth_error_code(error_code):
            normalized = _normalize_response_code(error_code)
            if isinstance(normalized, str) and normalized.lower() == "token_expired":
                return "token_expired"
            return normalized
        return None

    @staticmethod
    def _resolve_error_code(code: Any, error_code: Any) -> int | str | None:
        """Pick the most specific error code from code/errorCode fields."""
        normalized_error_code = _normalize_response_code(error_code)
        if normalized_error_code not in (None, "", 0):
            return normalized_error_code
        normalized_code = _normalize_response_code(code)
        if normalized_code not in (None, "", 0):
            return normalized_code
        return None

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
    ) -> _MappingPayloadT:
        """Finalize shared Smart Home/IoT mapping response handling.

        This keeps success extraction plus auth/API error mapping behavior aligned
        across request pipelines while preserving endpoint-specific retry policy.
        """
        code = result.get("code")
        if self._is_success_code(code):
            return success_payload(result)

        error_code = result.get("errorCode")
        message = result.get("message", "Unknown error")

        auth_error_code = self._resolve_auth_error_code(code, error_code)
        if auth_error_code is not None:
            if (
                retry_on_auth_error
                and retry_request is not None
                and await self._handle_auth_error_and_retry(
                    path, request_token, is_retry
                )
            ):
                return await retry_request()
            raise LiproAuthError(message, auth_error_code)

        effective_code = self._resolve_error_code(code, error_code)
        # Record API error for anonymous share
        _record_api_error(path, effective_code or 0, message, method="POST")
        raise LiproApiError(message, effective_code)

    @staticmethod
    def _is_invalid_param_error_code(code: Any) -> bool:
        """Check whether error code represents invalid request payload/params."""
        normalized = _normalize_response_code(code)
        return normalized in (ERROR_INVALID_PARAM, ERROR_INVALID_PARAM_STR)

    @staticmethod
    def _is_command_busy_error(err: LiproApiError) -> bool:
        """Check whether an API error is a transient command-busy response."""
        normalized = _normalize_response_code(err.code)
        if normalized in (ERROR_DEVICE_BUSY, ERROR_DEVICE_BUSY_STR):
            return True

        message = str(err)
        if not message:
            return False
        lowered = message.lower()
        return "设备繁忙" in message or "device busy" in lowered

    @staticmethod
    def _is_change_state_command(command: str) -> bool:
        """Return True when command is CHANGE_STATE."""
        return command.upper() == "CHANGE_STATE"

    @staticmethod
    def _normalize_pacing_target(target_id: str) -> str:
        """Normalize command target ID for per-target pacing caches."""
        return target_id.strip().lower()

    def _enforce_command_pacing_cache_limit(self) -> None:
        """Keep per-target pacing caches bounded."""
        tracked_targets = set(self._last_change_state_at) | set(
            self._change_state_min_interval
        )
        while len(tracked_targets) > _COMMAND_PACING_CACHE_MAX_SIZE:
            if self._last_change_state_at:
                oldest_target = min(
                    self._last_change_state_at.items(),
                    key=lambda item: item[1],
                )[0]
            else:
                oldest_target = next(iter(tracked_targets))

            self._last_change_state_at.pop(oldest_target, None)
            self._change_state_min_interval.pop(oldest_target, None)
            self._change_state_busy_count.pop(oldest_target, None)
            tracked_targets.discard(oldest_target)

    async def _record_change_state_busy(
        self,
        target_id: str,
        command: str,
    ) -> tuple[float, int]:
        """Increase adaptive pacing interval when CHANGE_STATE hits busy error."""
        if not self._is_change_state_command(command):
            return _CHANGE_STATE_MIN_INTERVAL_SECONDS, 0

        normalized_target = self._normalize_pacing_target(target_id)
        if not normalized_target:
            return _CHANGE_STATE_MIN_INTERVAL_SECONDS, 0

        async with self._command_pacing_lock:
            current_interval = max(
                _CHANGE_STATE_MIN_INTERVAL_SECONDS,
                self._change_state_min_interval.get(
                    normalized_target,
                    _CHANGE_STATE_MIN_INTERVAL_SECONDS,
                ),
            )
            next_interval = min(
                _CHANGE_STATE_MAX_INTERVAL_SECONDS,
                current_interval * _CHANGE_STATE_BUSY_MULTIPLIER,
            )
            busy_count = self._change_state_busy_count.get(normalized_target, 0) + 1

            self._change_state_min_interval[normalized_target] = next_interval
            self._change_state_busy_count[normalized_target] = busy_count
            self._enforce_command_pacing_cache_limit()
            return next_interval, busy_count

    async def _record_change_state_success(self, target_id: str, command: str) -> None:
        """Recover adaptive pacing interval after successful CHANGE_STATE command."""
        if not self._is_change_state_command(command):
            return

        normalized_target = self._normalize_pacing_target(target_id)
        if not normalized_target:
            return

        async with self._command_pacing_lock:
            current_interval = max(
                _CHANGE_STATE_MIN_INTERVAL_SECONDS,
                self._change_state_min_interval.get(
                    normalized_target,
                    _CHANGE_STATE_MIN_INTERVAL_SECONDS,
                ),
            )
            recovered_interval = max(
                _CHANGE_STATE_MIN_INTERVAL_SECONDS,
                current_interval * _CHANGE_STATE_RECOVERY_MULTIPLIER,
            )
            self._change_state_min_interval[normalized_target] = recovered_interval
            self._change_state_busy_count.pop(normalized_target, None)
            self._enforce_command_pacing_cache_limit()

    async def _iot_request_with_busy_retry(
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        target_id: str,
        command: str,
    ) -> dict[str, Any]:
        """Send IoT command request with retry for transient busy errors."""
        for attempt in range(_COMMAND_BUSY_RETRY_MAX_ATTEMPTS + 1):
            await self._throttle_change_state(target_id, command)
            try:
                result = await self._iot_request(path, body_data)
                await self._record_change_state_success(target_id, command)
                if isinstance(result, dict):
                    return result
                return {}
            except LiproApiError as err:
                if not self._is_command_busy_error(err):
                    raise

                adaptive_interval, busy_count = await self._record_change_state_busy(
                    target_id,
                    command,
                )
                if attempt >= _COMMAND_BUSY_RETRY_MAX_ATTEMPTS:
                    raise

                wait_time = _COMMAND_BUSY_RETRY_BASE_DELAY_SECONDS * (2**attempt)
                _LOGGER.debug(
                    (
                        "Command %s to %s busy (code=%s), retrying in %.2fs "
                        "(%d/%d), adaptive_interval=%.2fs busy_count=%d"
                    ),
                    command,
                    target_id,
                    err.code,
                    wait_time,
                    attempt + 1,
                    _COMMAND_BUSY_RETRY_MAX_ATTEMPTS,
                    adaptive_interval,
                    busy_count,
                )
                await asyncio.sleep(wait_time)

        # Defensive fallback, loop should return or raise earlier.
        return {}

    async def _throttle_change_state(self, target_id: str, command: str) -> None:
        """Pace high-frequency CHANGE_STATE sends for the same target."""
        if not self._is_change_state_command(command):
            return

        normalized_target = self._normalize_pacing_target(target_id)
        if not normalized_target:
            return

        async with self._command_pacing_lock:
            now = time.monotonic()
            last = self._last_change_state_at.get(normalized_target)
            min_interval = max(
                _CHANGE_STATE_MIN_INTERVAL_SECONDS,
                self._change_state_min_interval.get(
                    normalized_target,
                    _CHANGE_STATE_MIN_INTERVAL_SECONDS,
                ),
            )
            if last is not None:
                wait_time = min_interval - (now - last)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    now = time.monotonic()

            self._last_change_state_at[normalized_target] = now
            self._enforce_command_pacing_cache_limit()

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
        _is_retry: bool = False,
        _retry_count: int = 0,
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
            retry_count=_retry_count,
            send_request=_send_request,
        )
        return result, request_token

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
        result, request_token = await self._request_smart_home_mapping(
            path,
            data,
            require_auth=require_auth,
            _is_retry=_is_retry,
            _retry_count=_retry_count,
        )
        return await self._finalize_mapping_result(
            path=path,
            result=result,
            request_token=request_token,
            is_retry=_is_retry,
            retry_on_auth_error=require_auth,
            retry_request=(
                lambda: self._smart_home_request(
                    path,
                    data,
                    require_auth,
                    _is_retry=True,
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

    async def _request_iot_mapping(
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        _is_retry: bool = False,
        _retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        """Execute one IoT HTTP request and return validated mapping payload.

        Handles the shared request pipeline for IoT endpoints:
        token precheck, signed headers, 429 backoff retries, and HTTP 401 retry.
        """
        url = f"{IOT_API_URL}{path}"

        async def _send_request() -> tuple[int, Any, dict[str, str], str | None]:
            request_token = self._access_token
            if not request_token:
                msg = "No access token available"
                raise LiproAuthError(msg)

            session = await self._get_session()
            body = encode_iot_request_body(body_data)
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
            retry_count=_retry_count,
            send_request=_send_request,
        )

        if status == 401:
            if await self._handle_auth_error_and_retry(path, request_token, _is_retry):
                return await self._request_iot_mapping(
                    path,
                    body_data,
                    _is_retry=True,
                )
            msg = "HTTP 401 Unauthorized"
            raise LiproAuthError(msg, 401)

        return result, request_token

    async def _iot_request(
        self,
        path: str,
        body_data: dict[str, Any],
        _is_retry: bool = False,
        _retry_count: int = 0,
    ) -> Any:
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
        result, request_token = await self._request_iot_mapping(
            path,
            body_data,
            _is_retry=_is_retry,
            _retry_count=_retry_count,
        )
        return await self._finalize_mapping_result(
            path=path,
            result=result,
            request_token=request_token,
            is_retry=_is_retry,
            retry_on_auth_error=True,
            retry_request=lambda: self._iot_request(path, body_data, _is_retry=True),
            success_payload=self._unwrap_iot_success_payload,
        )

    @staticmethod
    def _unwrap_iot_success_payload(result: dict[str, Any]) -> Any:
        """Unwrap successful IoT API payload.

        Most endpoints use ``{"code":"0000","data":...}``, but a few may return
        direct payload objects. Keep empty ``data`` containers (for example `{}`)
        and only coerce ``None`` to empty dict for call-site compatibility.
        """
        if "data" in result:
            data = result["data"]
            return {} if data is None else data
        return result

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

        Raises:
            LiproConnectionError: If refresh fails due to transient network issues.

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
                raise

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
        """Check if the error is a retriable device error.

        Args:
            err: The API error to check.

        Returns:
            True if the error should trigger fallback to individual queries.
            Includes offline/no-permission/not-connected variants observed
            in real API traffic.

        """
        normalized = _normalize_response_code(err.code)
        return normalized in (
            ERROR_DEVICE_OFFLINE,
            ERROR_DEVICE_OFFLINE_STR,
            ERROR_DEVICE_NOT_CONNECTED,
            ERROR_DEVICE_NOT_CONNECTED_STR,
            ERROR_NO_PERMISSION,
            ERROR_NO_PERMISSION_STR,
        )

    @staticmethod
    def _extract_list_payload(
        result: Any,
        *keys: str,
    ) -> list[dict[str, Any]]:
        """Extract list payload from direct or wrapped API responses.

        Args:
            result: API response data.
            keys: Wrapper keys that may contain the list payload.

        Returns:
            Parsed list payload, or empty list when unavailable/invalid.

        """
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            for key in keys:
                value = result.get(key)
                if isinstance(value, list):
                    return value
        return []

    @staticmethod
    def _extract_data_list(result: Any) -> list[dict[str, Any]]:
        """Extract list payload from ``data`` responses."""
        return LiproClient._extract_list_payload(result, "data")

    @staticmethod
    def _extract_timings_list(result: Any) -> list[dict[str, Any]]:
        """Extract timing-task rows from API response variants.

        Real API responses are not fully consistent. Some endpoints return
        a list directly, while others may wrap rows under ``timings`` or
        ``data`` keys.
        """
        return LiproClient._extract_list_payload(result, "timings", "data")

    @staticmethod
    def _sanitize_iot_device_ids(
        device_ids: list[str],
        *,
        endpoint: str,
    ) -> list[str]:
        """Keep only valid IoT device IDs for endpoint requests.

        IDs are normalized to lowercase and de-duplicated while preserving order.
        Invalid/group IDs are skipped to prevent business-level API errors.
        """
        valid_ids: list[str] = []
        seen: set[str] = set()
        skipped = 0
        for raw_id in device_ids:
            normalized = _normalize_iot_device_id(raw_id)
            if normalized is None:
                skipped += 1
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            valid_ids.append(normalized)

        if skipped:
            _LOGGER.debug(
                "Skipped %d non-IoT IDs for %s",
                skipped,
                endpoint,
            )
        return valid_ids

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
            If a device is offline/unreachable, the API may return
            140003 or 140004.
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
            If a group has offline/unreachable devices, the API may return
            140003 or 140004.
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

        sanitized_ids = self._sanitize_iot_device_ids(
            device_ids,
            endpoint=PATH_QUERY_CONNECT_STATUS,
        )
        if not sanitized_ids:
            return {}

        try:
            # _iot_request returns dict[str, Any], but we use Any to allow
            # the defensive isinstance check below without type: ignore.
            result: Any = await self._iot_request(
                PATH_QUERY_CONNECT_STATUS,
                {"deviceIdList": sanitized_ids},
            )

            # API returns Map<String, Boolean>
            if isinstance(result, dict):
                # Defensive fallback for accidental wrapped payloads.
                if "code" in result and "data" in result:
                    wrapped_data = result.get("data")
                    if isinstance(wrapped_data, dict):
                        result = wrapped_data
                    else:
                        return {}
                # Defensive conversion for backend variants:
                # bool, int(1/0), and string("true"/"false"/"1"/"0").
                return {k: _coerce_connect_status(v) for k, v in result.items()}
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
        body = self._build_command_request_body(
            target_id=device_id,
            command=command,
            device_type=device_type,
            properties=properties,
            iot_name=iot_name,
        )

        return await self._iot_request_with_busy_retry(
            PATH_SEND_COMMAND,
            body,
            target_id=device_id,
            command=command,
        )

    def _build_command_request_body(
        self,
        *,
        target_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None,
        iot_name: str,
        group_id: str = "",
    ) -> dict[str, Any]:
        """Build a command request payload shared by device/group endpoints."""
        body: dict[str, Any] = {
            "command": command,
            "deviceId": target_id,
            "deviceType": self._to_device_type_hex(device_type),
            "iotName": iot_name,
            "properties": properties or [],
            "skuId": "",
            "hasMacRule": False,
        }
        if group_id:
            body["groupId"] = group_id
        return body

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
        body = self._build_command_request_body(
            target_id=group_id,
            command=command,
            device_type=device_type,
            properties=properties,
            iot_name=iot_name,
            group_id=group_id,
        )

        return await self._iot_request_with_busy_retry(
            PATH_SEND_GROUP_COMMAND,
            body,
            target_id=group_id,
            command=command,
        )

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
            without the usual ``code``/``data`` wrapper, so it uses
            dedicated success payload parsing.

        """
        result, _ = await self._request_iot_mapping(
            PATH_GET_MQTT_CONFIG,
            {},
            _is_retry=_is_retry,
            _retry_count=_retry_count,
        )

        # This endpoint returns {"accessKey": "...", "secretKey": "..."} directly
        if "accessKey" in result and "secretKey" in result:
            return result

        # Fallback: if the API ever wraps it in standard format
        code = result.get("code")
        if self._is_success_code(code):
            payload = self._unwrap_iot_success_payload(result)
            return self._require_mapping_response(PATH_GET_MQTT_CONFIG, payload)

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
        sanitized_ids = self._sanitize_iot_device_ids(
            device_ids,
            endpoint=PATH_QUERY_OUTLET_POWER,
        )
        if not sanitized_ids:
            return {}

        try:
            result = await self._iot_request(
                PATH_QUERY_OUTLET_POWER,
                {"deviceIds": sanitized_ids},
            )
            return self._require_mapping_response(PATH_QUERY_OUTLET_POWER, result)
        except LiproApiError as err:
            # Real-world API may return 100000 when device IDs are valid format
            # but unsupported by this endpoint. Degrade to empty power payload.
            if self._is_invalid_param_error_code(err.code):
                _LOGGER.debug(
                    "Power-info endpoint rejected device IDs %s (code=%s), treating as empty",
                    sanitized_ids,
                    err.code,
                )
                return {}
            raise

    # ==================== Timing Task APIs ====================

    @staticmethod
    def _is_mesh_group_id(device_id: str) -> bool:
        """Check whether the identifier is a mesh-group ID."""
        return is_mesh_group_id(device_id)

    @classmethod
    def _resolve_mesh_schedule_candidate_ids(
        cls,
        device_id: str,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[str]:
        """Resolve candidate IoT device IDs for mesh schedule APIs.

        The mesh schedule endpoints use real device IoT IDs in practice,
        not mesh-group IDs. Prefer gateway ID, then group members.
        """
        return resolve_mesh_schedule_candidate_ids(
            device_id,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
            normalize_iot_device_id=_normalize_iot_device_id,
        )

    def _resolve_mesh_schedule_candidates_for_group(
        self,
        device_id: str,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[str] | None:
        """Resolve mesh schedule candidate IDs only when target is a mesh group."""
        if not self._is_mesh_group_id(device_id):
            return None

        candidate_ids = self._resolve_mesh_schedule_candidate_ids(
            device_id,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )
        return candidate_ids or None

    def _resolve_schedule_request_context(
        self,
        *,
        device_id: str,
        device_type: int | str,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> tuple[list[str] | None, str]:
        """Resolve mesh candidate IDs and normalized device type for schedule APIs."""
        candidate_ids = self._resolve_mesh_schedule_candidates_for_group(
            device_id,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )
        device_type_hex = self._to_device_type_hex(device_type)
        return candidate_ids, device_type_hex

    async def _request_schedule_timings(
        self,
        path: str,
        body: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Request schedule endpoint and normalize timings-list payload variants."""
        result = await self._iot_request(path, body)
        return self._extract_timings_list(result)

    @staticmethod
    def _coerce_int_list(value: Any) -> list[int]:
        """Convert mixed list payloads into a clean integer list."""
        return _coerce_schedule_int_list(value)

    @classmethod
    def _parse_mesh_schedule_json(cls, schedule_json: Any) -> dict[str, list[int]]:
        """Parse mesh ``scheduleJson`` into ``days/time/evt`` arrays."""
        return _parse_mesh_schedule_payload(
            schedule_json,
            coerce_connect_status=_coerce_connect_status,
            mask_sensitive_data=_mask_sensitive_data,
        )

    @classmethod
    def _normalize_mesh_timing_rows(
        cls,
        rows: list[Any],
        *,
        fallback_device_id: str = "",
    ) -> list[dict[str, Any]]:
        """Normalize mesh timing rows to include ``schedule`` dict payload."""
        return _normalize_mesh_schedule_rows(
            rows,
            fallback_device_id=fallback_device_id,
            parse_schedule_json=cls._parse_mesh_schedule_json,
            coerce_connect_status=_coerce_connect_status,
        )

    async def _execute_mesh_schedule_candidate_request(
        self,
        *,
        candidate_id: str,
        operation: str,
        request: Callable[[str], Awaitable[Any]],
    ) -> tuple[bool, Any, LiproApiError | None]:
        """Execute one mesh schedule candidate request with shared error handling."""
        try:
            return True, await request(candidate_id), None
        except LiproAuthError:
            raise
        except LiproApiError as err:
            _LOGGER.debug(
                "Mesh schedule %s failed for %s: %s (code=%s)",
                operation,
                candidate_id,
                err,
                err.code,
            )
            return False, None, err

    async def _get_mesh_schedules_by_candidates(
        self,
        candidate_device_ids: list[str],
        *,
        raise_on_total_failure: bool = True,
    ) -> list[dict[str, Any]]:
        """Query mesh schedule list from candidate device IDs."""
        if not candidate_device_ids:
            return []

        last_error: LiproApiError | None = None
        has_successful_call = False

        for candidate_id in candidate_device_ids:
            ok, result, err = await self._execute_mesh_schedule_candidate_request(
                candidate_id=candidate_id,
                operation="GET",
                request=lambda candidate: self._iot_request(
                    PATH_BLE_SCHEDULE_GET,
                    build_mesh_schedule_get_body(candidate),
                ),
            )
            if not ok:
                if err is not None:
                    last_error = err
                continue

            has_successful_call = True
            rows = self._extract_timings_list(result)
            normalized_rows = self._normalize_mesh_timing_rows(
                rows,
                fallback_device_id=candidate_id,
            )
            if normalized_rows:
                return normalized_rows

        if has_successful_call:
            return []

        if raise_on_total_failure and last_error is not None:
            raise last_error

        return []

    async def _add_mesh_schedule_by_candidates(
        self,
        candidate_device_ids: list[str],
        *,
        days: list[int],
        times: list[int],
        events: list[int],
    ) -> list[dict[str, Any]]:
        """Try mesh schedule add across candidates and return refreshed schedule rows."""
        schedule_json = encode_mesh_schedule_json(days, times, events)
        last_error: LiproApiError | None = None

        for candidate_id in candidate_device_ids:
            ok, _, err = await self._execute_mesh_schedule_candidate_request(
                candidate_id=candidate_id,
                operation="ADD",
                request=lambda candidate: self._iot_request(
                    PATH_BLE_SCHEDULE_ADD,
                    build_mesh_schedule_add_body(
                        candidate,
                        schedule_json=schedule_json,
                    ),
                ),
            )
            if ok:
                return await self._get_mesh_schedules_by_candidates(
                    candidate_device_ids,
                    raise_on_total_failure=False,
                )
            if err is not None:
                last_error = err

        if last_error is not None:
            raise last_error
        return []

    async def _delete_mesh_schedules_by_candidates(
        self,
        candidate_device_ids: list[str],
        *,
        schedule_ids: list[int],
    ) -> list[dict[str, Any]]:
        """Try mesh schedule delete across candidates and return refreshed rows."""
        deleted = False
        last_error: LiproApiError | None = None

        for candidate_id in candidate_device_ids:
            ok, _, err = await self._execute_mesh_schedule_candidate_request(
                candidate_id=candidate_id,
                operation="DELETE",
                request=lambda candidate: self._iot_request(
                    PATH_BLE_SCHEDULE_DELETE,
                    build_mesh_schedule_delete_body(
                        candidate,
                        schedule_ids=schedule_ids,
                    ),
                ),
            )
            if ok:
                deleted = True
                continue
            if err is not None:
                last_error = err

        if deleted:
            return await self._get_mesh_schedules_by_candidates(
                candidate_device_ids,
                raise_on_total_failure=False,
            )
        if last_error is not None:
            raise last_error
        return []

    async def get_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Get timing schedules for a device.

        Args:
            device_id: Device IoT ID.
            device_type: Device type (integer or hex string).
            mesh_gateway_id: Optional mesh gateway IoT ID.
            mesh_member_ids: Optional mesh member IoT IDs.

        Returns:
            List of timing schedules, each containing:
                - id: Schedule ID
                - active: Whether schedule is active
                - schedule: Dict with days, time, evt arrays

        """
        candidate_ids, device_type_hex = self._resolve_schedule_request_context(
            device_id=device_id,
            device_type=device_type,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )
        if candidate_ids:
            return await self._get_mesh_schedules_by_candidates(candidate_ids)

        return await self._request_schedule_timings(
            PATH_SCHEDULE_GET,
            build_schedule_get_body(device_id, device_type_hex=device_type_hex),
        )

    async def add_device_schedule(
        self,
        device_id: str,
        device_type: int | str,
        days: list[int],
        times: list[int],
        events: list[int],
        group_id: str = "",
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Add or update a timing schedule for a device.

        Args:
            device_id: Device IoT ID.
            device_type: Device type (integer or hex string).
            days: List of weekdays (1=Monday, 7=Sunday).
            times: List of times in seconds from midnight.
            events: List of event codes (0=light on, 1=light off, etc.).
            group_id: Optional group ID for mesh devices.
            mesh_gateway_id: Optional mesh gateway IoT ID.
            mesh_member_ids: Optional mesh member IoT IDs.

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

        candidate_ids, device_type_hex = self._resolve_schedule_request_context(
            device_id=device_id,
            device_type=device_type,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )
        if candidate_ids:
            return await self._add_mesh_schedule_by_candidates(
                candidate_ids,
                days=days,
                times=times,
                events=events,
            )

        return await self._request_schedule_timings(
            PATH_SCHEDULE_ADD,
            build_schedule_add_body(
                device_id,
                device_type_hex=device_type_hex,
                days=days,
                times=times,
                events=events,
                group_id=group_id,
            ),
        )

    async def delete_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        schedule_ids: list[int],
        group_id: str = "",
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Delete timing schedules for a device.

        Args:
            device_id: Device IoT ID.
            device_type: Device type (integer or hex string).
            schedule_ids: List of schedule IDs to delete.
            group_id: Optional group ID for mesh devices.
            mesh_gateway_id: Optional mesh gateway IoT ID.
            mesh_member_ids: Optional mesh member IoT IDs.

        Returns:
            Remaining list of timing schedules.

        """
        candidate_ids, device_type_hex = self._resolve_schedule_request_context(
            device_id=device_id,
            device_type=device_type,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )
        if candidate_ids:
            return await self._delete_mesh_schedules_by_candidates(
                candidate_ids,
                schedule_ids=schedule_ids,
            )

        return await self._request_schedule_timings(
            PATH_SCHEDULE_DELETE,
            build_schedule_delete_body(
                device_id,
                device_type_hex=device_type_hex,
                schedule_ids=schedule_ids,
                group_id=group_id,
            ),
        )


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
