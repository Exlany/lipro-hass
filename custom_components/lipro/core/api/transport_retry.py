"""429 replay loop for HTTP transport mapping requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class TransportRetry:
    """Replay mapping requests after policy-owned rate-limit decisions."""

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
        handle_rate_limit: Callable[[str, dict[str, str], int], Awaitable[float]],
    ) -> tuple[int, dict[str, Any], str | None]:
        """Execute one mapping request with externalized 429 policy handling."""
        status, result, headers, request_token = await send_request()
        if status == 429:
            await handle_rate_limit(path, headers, retry_count)
            return await TransportRetry.execute_with_rate_limit_retry(
                path=path,
                retry_count=retry_count + 1,
                send_request=send_request,
                require_mapping_response=require_mapping_response,
                handle_rate_limit=handle_rate_limit,
            )
        return status, require_mapping_response(path, result), request_token
