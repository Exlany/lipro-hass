"""Internal token-refresh and submit-flow helpers for the share worker client."""

from __future__ import annotations

from collections.abc import Awaitable
import json

import aiohttp

from .share_client_ports import ShareWorkerClientLike
from .share_client_refresh import refresh_install_token_with_outcome
from .share_client_submit import submit_share_payload_with_outcome
from .share_client_support import JsonReadableResponse, WorkerResponsePayload


async def safe_read_json(
    response: JsonReadableResponse,
) -> WorkerResponsePayload | None:
    """Best-effort JSON parsing for Worker responses."""
    try:
        json_reader = getattr(response, "json", None)
        if not callable(json_reader):
            return None
        result = response.json(content_type=None)
        if isinstance(result, Awaitable):
            data = await result
        else:
            data = result
    except (
        AttributeError,
        aiohttp.ContentTypeError,
        json.JSONDecodeError,
        ValueError,
    ):
        return None
    return data if isinstance(data, dict) else None


__all__ = [
    "ShareWorkerClientLike",
    "refresh_install_token_with_outcome",
    "safe_read_json",
    "submit_share_payload_with_outcome",
]
