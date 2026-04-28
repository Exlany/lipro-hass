"""Topicized ShareWorkerClient primitive and token-shape tests."""
# ruff: noqa: F403, F405

from __future__ import annotations

from .test_share_client_support import *


def test_build_upload_headers_and_parse_retry_after() -> None:
    headers = ShareWorkerClient.build_upload_headers()
    assert headers["X-API-Key"]
    assert "Authorization" not in headers

    with_token = ShareWorkerClient.build_upload_headers(install_token="abc")
    assert with_token["Authorization"] == "Bearer abc"

    assert ShareWorkerClient.parse_retry_after({"Retry-After": "15"}) == 15.0
    assert ShareWorkerClient.parse_retry_after({"retry-after": "0"}) == 0.1
    assert ShareWorkerClient.parse_retry_after({"Retry-After": "-2"}) == 0.1
    assert ShareWorkerClient.parse_retry_after({"Retry-After": "bad"}) is None
    assert ShareWorkerClient.parse_retry_after(object()) is None


def test_parse_retry_after_supports_http_date() -> None:
    from datetime import UTC, datetime, timedelta

    future = datetime.now(UTC) + timedelta(seconds=60)
    http_date = future.strftime("%a, %d %b %Y %H:%M:%S GMT")

    result = ShareWorkerClient.parse_retry_after({"Retry-After": http_date})

    assert result is not None
    assert 55 <= result <= 65


def test_apply_token_payload_and_clear_install_token() -> None:
    client = ShareWorkerClient()

    assert client.apply_token_payload({}) is False
    assert client.install_token is None

    assert (
        client.apply_token_payload(
            {
                "install_token": "tok-2",
                "token_expires_at": 456,
                "token_refresh_after": 123,
            }
        )
        is True
    )
    assert client.install_token == "tok-2"
    assert client.token_expires_at == 456
    assert client.token_refresh_after == 123

    client.clear_install_token()
    assert client.install_token is None
    assert client.token_expires_at == 0
    assert client.token_refresh_after == 0


def test_apply_token_payload_coerces_invalid_timestamps_safely() -> None:
    client = ShareWorkerClient()

    assert (
        client.apply_token_payload(
            {
                "install_token": "tok-3",
                "token_expires_at": "bad",
                "token_refresh_after": True,
            }
        )
        is True
    )
    assert client.install_token == "tok-3"
    assert client.token_expires_at == 0
    assert client.token_refresh_after == 0


async def test_safe_read_json_handles_missing_reader_and_reader_errors() -> None:
    client = ShareWorkerClient()

    assert await client.safe_read_json(cast(aiohttp.ClientResponse, object())) is None

    bad_response = _response(status=200, json_side_effect=ValueError("bad-json"))
    assert await client.safe_read_json(bad_response) is None

    list_response = _response(status=200, payload=[1, 2, 3], async_json=False)
    assert await client.safe_read_json(list_response) is None
