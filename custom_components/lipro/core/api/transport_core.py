"""Core HTTP transport and request execution for the formal REST facade."""

from __future__ import annotations

from contextlib import AbstractAsyncContextManager
import json
import logging
from typing import cast

import aiohttp

from . import response_safety as _response_safety
from .errors import LiproApiError, LiproConnectionError
from .response_safety import (
    INVALID_JSON_BODY_READ_MAX_BYTES as _INVALID_JSON_BODY_READ_MAX_BYTES,
    INVALID_JSON_LOG_PREVIEW_MAX_CHARS as _INVALID_JSON_LOG_PREVIEW_MAX_CHARS,
)
from .types import JsonObject, ResponseHeaders

_LOGGER = logging.getLogger("custom_components.lipro.core.api")


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

    def set_session(self, session: aiohttp.ClientSession | None) -> None:
        """Replace the injected aiohttp session reference."""
        self._session = session

    def close_session(self) -> None:
        """Close the client session (no-op: HA-injected session is managed by HA)."""
        self._session = None

    async def _parse_json_response(self, response: aiohttp.ClientResponse) -> object:
        """Parse one JSON response while tolerating aiohttp version differences."""
        try:
            return await response.json(content_type=None)
        except TypeError:
            return await response.json()

    @staticmethod
    def _read_cached_body_bytes(response: aiohttp.ClientResponse) -> bytes | None:
        """Return cached response body bytes when aiohttp already buffered them."""
        body_bytes: bytes | None = getattr(response, "_body", None)
        return body_bytes if isinstance(body_bytes, bytes) else None

    async def _read_invalid_json_preview(
        self,
        response: aiohttp.ClientResponse,
    ) -> tuple[int | None, bytes, bool]:
        """Read a bounded preview for invalid-JSON diagnostics."""
        body_bytes = self._read_cached_body_bytes(response)
        if body_bytes is not None:
            body_length = len(body_bytes)
            preview_bytes = body_bytes[:_INVALID_JSON_BODY_READ_MAX_BYTES]
            truncated = len(body_bytes) > _INVALID_JSON_BODY_READ_MAX_BYTES
            return body_length, preview_bytes, truncated

        preview_bytes = await response.content.read(_INVALID_JSON_BODY_READ_MAX_BYTES + 1)
        truncated = len(preview_bytes) > _INVALID_JSON_BODY_READ_MAX_BYTES
        if truncated:
            preview_bytes = preview_bytes[:_INVALID_JSON_BODY_READ_MAX_BYTES]
        return response.content_length, preview_bytes, truncated

    @staticmethod
    def _decode_preview_text(
        response: aiohttp.ClientResponse,
        preview_bytes: bytes,
    ) -> str:
        """Decode one invalid-JSON preview using response charset when possible."""
        charset = response.charset or "utf-8"
        try:
            return preview_bytes.decode(charset, errors="replace")
        except (LookupError, TypeError):
            return preview_bytes.decode("utf-8", errors="replace")

    async def _raise_invalid_json_response(
        self,
        *,
        path: str,
        status: int,
        response: aiohttp.ClientResponse,
        err: Exception,
    ) -> None:
        """Log one invalid-JSON preview and raise the canonical API error."""
        body_length, preview_bytes, truncated = await self._read_invalid_json_preview(
            response,
        )
        preview_text = self._decode_preview_text(response, preview_bytes)
        masked_preview = _response_safety.mask_sensitive_data(preview_text)[
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

    @staticmethod
    def _log_response_summary(path: str, result: object) -> None:
        """Emit one sanitized response summary when debug logging is enabled."""
        if not _LOGGER.isEnabledFor(logging.DEBUG):
            return

        summary: dict[str, object] = {"type": type(result).__name__}
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

    async def execute_request(
        self,
        request_ctx: object,
        path: str,
    ) -> tuple[int, JsonObject, ResponseHeaders]:
        """Execute an HTTP request with common error handling.

        Args:
            request_ctx: The context manager from session.post().
            path: API path (for logging).

        Returns:
            Tuple of (HTTP status code, parsed JSON response body, response headers).

        Raises:
            LiproConnectionError: If connection fails or times out.
            LiproApiError: If response is not valid JSON or not a JSON object.

        """
        try:
            async with cast(
                AbstractAsyncContextManager[aiohttp.ClientResponse],
                request_ctx,
            ) as response:
                status = response.status
                headers = dict(response.headers)
                try:
                    result = await self._parse_json_response(response)
                except (json.JSONDecodeError, aiohttp.ContentTypeError) as err:
                    await self._raise_invalid_json_response(
                        path=path,
                        status=status,
                        response=response,
                        err=err,
                    )
        except aiohttp.ClientError as err:
            msg = f"Connection error: {type(err).__name__}: {err}"
            _LOGGER.debug("Network error on %s: %s", path, msg)
            raise LiproConnectionError(msg) from err
        except TimeoutError as err:
            msg = f"Request timeout: {type(err).__name__}"
            _LOGGER.debug("Timeout on %s: %s", path, msg)
            raise LiproConnectionError(msg) from err

        mapping_result = self.require_mapping_response(path, result)
        self._log_response_summary(path, mapping_result)
        return status, mapping_result, headers

    @staticmethod
    def require_mapping_response(path: str, result: object) -> JsonObject:
        """Validate that an API response payload is a JSON object.

        Args:
            path: API path (for error message).
            result: Response data to validate.

        Returns:
            Validated response dict.

        Raises:
            LiproApiError: If response is not a string-keyed dict.

        """
        if isinstance(result, dict) and all(isinstance(key, str) for key in result):
            return cast(JsonObject, result)
        msg = (
            f"Invalid JSON response from {path}: "
            f"expected object, got {type(result).__name__}"
        )
        raise LiproApiError(msg)
