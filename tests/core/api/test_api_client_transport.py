"""Tests for REST transport executor edge paths."""

from __future__ import annotations

import json
import logging
from unittest.mock import MagicMock

import aiohttp
import pytest

from custom_components.lipro.core.api import LiproApiError
from custom_components.lipro.core.api.client_auth_recovery import AuthRecoveryCoordinator
from custom_components.lipro.core.api.client_base import ClientSessionState
from custom_components.lipro.core.api.client_transport import TransportExecutor
from custom_components.lipro.core.api.request_policy import RequestPolicy
from custom_components.lipro.core.api.response_safety import (
    INVALID_JSON_BODY_READ_MAX_BYTES,
)


class _DummyContent:
    def __init__(self, data: bytes) -> None:
        self._data = data

    async def read(self, n: int) -> bytes:
        return self._data[:n]


class _DummyResponse:
    def __init__(
        self,
        *,
        status: int,
        headers: dict[str, str] | None = None,
        json_data: object | None = None,
        json_exc: Exception | None = None,
        body: object | None = None,
        content_bytes: bytes = b"",
        charset: str | None = "utf-8",
        content_length: int | None = None,
    ) -> None:
        self.status = status
        self.headers = headers or {}
        self._json_data = json_data
        self._json_exc = json_exc
        self._body = body
        self.content = _DummyContent(content_bytes)
        self.charset = charset
        self.content_length = content_length

    async def json(self) -> object:
        if self._json_exc is not None:
            raise self._json_exc
        return self._json_data


class _DummyRequestCtx:
    def __init__(self, response: _DummyResponse) -> None:
        self._response = response

    async def __aenter__(self) -> _DummyResponse:
        return self._response

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False


def _build_executor() -> TransportExecutor:
    state = ClientSessionState(
        phone_id="test_phone_id",
        session=MagicMock(spec=aiohttp.ClientSession),
        request_timeout=30,
    )
    policy = RequestPolicy()
    auth_recovery = AuthRecoveryCoordinator(state)
    return TransportExecutor(state, auth_recovery, policy)


@pytest.mark.asyncio
async def test_execute_request_invalid_json_uses_cached_body_bytes() -> None:
    executor = _build_executor()

    body = b"x" * (INVALID_JSON_BODY_READ_MAX_BYTES + 10)
    response = _DummyResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        json_exc=json.JSONDecodeError("Expecting value", "doc", 0),
        body=body,
    )

    with pytest.raises(LiproApiError, match="Invalid JSON response from /v2/test"):
        await executor.execute_request(_DummyRequestCtx(response), "/v2/test")


@pytest.mark.asyncio
async def test_execute_request_invalid_json_reads_and_truncates_stream_body() -> None:
    executor = _build_executor()

    stream_body = b"y" * (INVALID_JSON_BODY_READ_MAX_BYTES + 10)
    response = _DummyResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        json_exc=json.JSONDecodeError("Expecting value", "doc", 0),
        body=None,
        content_bytes=stream_body,
    )

    with pytest.raises(LiproApiError, match="Invalid JSON response from /v2/test"):
        await executor.execute_request(_DummyRequestCtx(response), "/v2/test")


@pytest.mark.asyncio
async def test_execute_request_logs_response_when_debug_enabled(caplog) -> None:
    executor = _build_executor()

    caplog.set_level(logging.DEBUG, logger="custom_components.lipro.core.api.client")

    response = _DummyResponse(
        status=200,
        headers={"x-test": "1"},
        json_data={"ok": True},
    )
    status, result, headers = await executor.execute_request(
        _DummyRequestCtx(response), "/v2/test"
    )

    assert status == 200
    assert result == {"ok": True}
    assert headers == {"x-test": "1"}
    assert any(
        "API response from /v2/test" in rec.getMessage() for rec in caplog.records
    )
