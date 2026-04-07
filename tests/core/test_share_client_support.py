"""Shared helpers for topicized ShareWorkerClient suites."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.lipro.core.anonymous_share.const import (
    SHARE_REPORT_URL,
    SHARE_TOKEN_REFRESH_URL,
)
from custom_components.lipro.core.anonymous_share.share_client import ShareWorkerClient
from custom_components.lipro.core.telemetry.models import build_operation_outcome


def _response_context(response: MagicMock) -> AsyncMock:
    context = AsyncMock()
    context.__aenter__ = AsyncMock(return_value=response)
    context.__aexit__ = AsyncMock(return_value=False)
    return context


def _response(
    *,
    status: int,
    payload: Any = None,
    headers: dict[str, str] | None = None,
    json_side_effect: Exception | None = None,
    async_json: bool = True,
) -> MagicMock:
    response = MagicMock()
    response.status = status
    response.headers = headers or {}
    if json_side_effect is not None:
        response.json = MagicMock(side_effect=json_side_effect)
    elif async_json:
        response.json = AsyncMock(return_value=payload)
    else:
        response.json = MagicMock(return_value=payload)
    return response


def _make_report() -> dict[str, Any]:
    return {
        "installation_id": "install-001",
        "devices": [{"type": "light"}],
        "errors": [],
    }


__all__ = [
    "ANY",
    "SHARE_REPORT_URL",
    "SHARE_TOKEN_REFRESH_URL",
    "AsyncMock",
    "MagicMock",
    "ShareWorkerClient",
    "_make_report",
    "_response",
    "_response_context",
    "aiohttp",
    "build_operation_outcome",
    "cast",
    "patch",
    "pytest",
]
