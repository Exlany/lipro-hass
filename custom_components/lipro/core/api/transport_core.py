"""Core HTTP transport and request execution for LiproClient."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

import aiohttp

from . import response_safety as _response_safety
from .errors import LiproApiError, LiproConnectionError
from .response_safety import (
    INVALID_JSON_BODY_READ_MAX_BYTES as _INVALID_JSON_BODY_READ_MAX_BYTES,
    INVALID_JSON_LOG_PREVIEW_MAX_CHARS as _INVALID_JSON_LOG_PREVIEW_MAX_CHARS,
)

if TYPE_CHECKING:
    pass


_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")


class TransportCore:
    """Handles core HTTP request execution and response processing."""

    def __init__(self, session: aiohttp.ClientSession | None, request_timeout: int) -> None:
        """Initialize transport core.

        Args:
            session: aiohttp session for making requests.
            request_timeout: Request timeout in seconds.

        """
        self._session = session
        self._request_timeout = request_timeout

    async def get_session(self) -> aiohttp.ClientSession:
        """Get the aiohttp session.

        Returns:
            Active aiohttp session.

        Raises:
            LiproConnectionError: If no session is available.

        """
        if self._session is None or self._session.closed:
            msg = "No aiohttp session available (must be injected via constructor)"
            raise LiproConnectionError(msg)
        return self._session

    def close_session(self) -> None:
        """Close the client session (no-op: HA-injected session is managed by HA)."""
        self._session = None

    async def execute_request(
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
            LiproApiError: If response is not valid JSON.

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
    def require_mapping_response(path: str, result: Any) -> dict[str, Any]:
        """Validate that an API response payload is a JSON object.

        Args:
            path: API path (for error message).
            result: Response data to validate.

        Returns:
            Validated response dict.

        Raises:
            LiproApiError: If response is not a dict.

        """
        if isinstance(result, dict):
            return result
        msg = (
            f"Invalid JSON response from {path}: "
            f"expected object, got {type(result).__name__}"
        )
        raise LiproApiError(msg)
