"""Retry and rate limit handling for HTTP transport."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from ...const.api import MAX_RATE_LIMIT_RETRIES, MAX_RETRY_AFTER
from .errors import LiproRateLimitError
from .request_policy import compute_rate_limit_wait_time

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


_LOGGER = logging.getLogger("custom_components.lipro.core.api")


class TransportRetry:
    """Handles retry logic and rate limit backoff for API requests."""

    @staticmethod
    async def handle_rate_limit(
        path: str,
        headers: dict[str, str],
        retry_count: int,
        parse_retry_after: Callable[[dict[str, str]], float | None],
    ) -> float:
        """Handle 429 rate limit with exponential backoff.

        Args:
            path: API path (for logging).
            headers: Response headers (may contain Retry-After).
            retry_count: Current retry attempt (0-based).
            parse_retry_after: Function to parse Retry-After header.

        Returns:
            Wait time in seconds.

        Raises:
            LiproRateLimitError: If max retries exceeded.

        """
        retry_after = parse_retry_after(headers)
        if retry_count >= MAX_RATE_LIMIT_RETRIES:
            _LOGGER.warning(
                "Rate limited on %s after %d retries (retry_after=%s)",
                path,
                MAX_RATE_LIMIT_RETRIES,
                retry_after,
            )
            msg = f"Rate limited after {MAX_RATE_LIMIT_RETRIES} retries"
            raise LiproRateLimitError(msg, retry_after)

        wait_time = compute_rate_limit_wait_time(
            retry_count=retry_count,
            retry_after=retry_after,
            max_retry_after=MAX_RETRY_AFTER,
        )
        _LOGGER.info(
            "Rate limited on %s (retry %d/%d), waiting %.1fs",
            path,
            retry_count + 1,
            MAX_RATE_LIMIT_RETRIES,
            wait_time,
        )

        await asyncio.sleep(wait_time)
        return wait_time

    @staticmethod
    async def execute_with_rate_limit_retry(
        *,
        path: str,
        retry_count: int,
        send_request: Callable[
            [],
            Awaitable[tuple[int, Any, dict[str, str], str | None]],
        ],
        require_mapping_response: Callable[[str, Any], dict[str, Any]],
        parse_retry_after: Callable[[dict[str, str]], float | None],
    ) -> tuple[int, dict[str, Any], str | None]:
        """Execute mapping request with shared 429 retry and payload validation.

        Args:
            path: API path.
            retry_count: Current retry count.
            send_request: Async function that sends the request.
            require_mapping_response: Function to validate response is a dict.
            parse_retry_after: Function to parse Retry-After header.

        Returns:
            Tuple of (status code, validated response dict, request token).

        """
        status, result, headers, request_token = await send_request()
        if status == 429:
            await TransportRetry.handle_rate_limit(
                path, headers, retry_count, parse_retry_after
            )
            return await TransportRetry.execute_with_rate_limit_retry(
                path=path,
                retry_count=retry_count + 1,
                send_request=send_request,
                require_mapping_response=require_mapping_response,
                parse_retry_after=parse_retry_after,
            )
        return status, require_mapping_response(path, result), request_token
