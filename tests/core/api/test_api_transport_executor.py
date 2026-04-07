"""Tests for REST transport executor edge paths."""

from __future__ import annotations

import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.lipro.const.api import (
    HEADER_ACCESS_TOKEN,
    HEADER_NONCE,
    HEADER_SIGN,
)
from custom_components.lipro.core.api import LiproApiError
from custom_components.lipro.core.api.auth_recovery import RestAuthRecoveryCoordinator
from custom_components.lipro.core.api.request_policy import RequestPolicy
from custom_components.lipro.core.api.response_safety import (
    INVALID_JSON_BODY_READ_MAX_BYTES,
)
from custom_components.lipro.core.api.session_state import RestSessionState
from custom_components.lipro.core.api.transport_executor import RestTransportExecutor


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


def _build_executor(policy: RequestPolicy | None = None) -> RestTransportExecutor:
    state = RestSessionState(
        phone_id="test_phone_id",
        session=MagicMock(spec=aiohttp.ClientSession),
        request_timeout=30,
    )
    auth_recovery = RestAuthRecoveryCoordinator(state)
    return RestTransportExecutor(state, auth_recovery, policy or RequestPolicy())


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

    caplog.set_level(logging.DEBUG, logger="custom_components.lipro.core.api")

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


@pytest.mark.asyncio
async def test_execute_request_rejects_non_mapping_json_payload() -> None:
    executor = _build_executor()

    response = _DummyResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        json_data=[{"ok": True}],
    )

    with pytest.raises(
        LiproApiError,
        match="Invalid JSON response from /v2/test: expected object, got list",
    ):
        await executor.execute_request(_DummyRequestCtx(response), "/v2/test")


@pytest.mark.asyncio
async def test_execute_mapping_request_with_rate_limit_uses_request_policy_home() -> None:
    policy = RequestPolicy()
    executor = _build_executor(policy)
    send_request = AsyncMock(
        side_effect=[
            (429, {"retry": True}, {"Retry-After": "1"}, "token-1"),
            (200, {"ok": True}, {}, "token-1"),
        ]
    )

    with patch.object(
        policy,
        "handle_rate_limit",
        new=AsyncMock(return_value=1.0),
    ) as handle_rate_limit:
        status, result, request_token = await executor.execute_mapping_request_with_rate_limit(
            path="/v2/test",
            retry_count=0,
            send_request=send_request,
        )

    assert status == 200
    assert result == {"ok": True}
    assert request_token == "token-1"
    handle_rate_limit.assert_awaited_once_with("/v2/test", {"Retry-After": "1"}, 0)


def test_to_device_type_hex_accepts_decimal_strings_and_rejects_invalid_format() -> None:
    executor = _build_executor()

    assert executor.to_device_type_hex("1") == "ff000001"

    with pytest.raises(ValueError, match="Invalid deviceType format"):
        executor.to_device_type_hex("bad-type")


def test_sync_session_updates_state_and_transport_core() -> None:
    executor = _build_executor()
    new_session = MagicMock(spec=aiohttp.ClientSession)

    with patch.object(executor._transport_core, "set_session") as set_session:
        executor.sync_session(new_session)

    assert executor._state.session is new_session
    set_session.assert_called_once_with(new_session)


def test_close_clears_state_and_transport_core_session() -> None:
    executor = _build_executor()

    with patch.object(executor._transport_core, "close_session") as close_session:
        executor.close()

    assert executor._state.session is None
    close_session.assert_called_once_with()


def test_build_iot_headers_uses_current_token_nonce_and_signature() -> None:
    executor = _build_executor()
    executor._state.access_token = "access-token"

    with (
        patch.object(executor, "get_timestamp_ms", return_value=1234567890),
        patch.object(executor, "iot_sign", return_value="signed-payload") as iot_sign,
    ):
        headers = executor.build_iot_headers('{"hello":"world"}')

    assert headers[HEADER_ACCESS_TOKEN] == "access-token"
    assert headers[HEADER_NONCE] == "1234567890"
    assert headers[HEADER_SIGN] == "signed-payload"
    iot_sign.assert_called_once_with(1234567890, '{"hello":"world"}')
