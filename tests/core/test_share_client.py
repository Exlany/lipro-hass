"""Tests for ShareWorkerClient."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.lipro.core.anonymous_share.share_client import ShareWorkerClient


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


@pytest.mark.asyncio
async def test_safe_read_json_handles_missing_reader_and_reader_errors() -> None:
    client = ShareWorkerClient()

    assert await client.safe_read_json(cast(aiohttp.ClientResponse, object())) is None

    bad_response = _response(status=200, json_side_effect=ValueError("bad-json"))
    assert await client.safe_read_json(bad_response) is None

    list_response = _response(status=200, payload=[1, 2, 3], async_json=False)
    assert await client.safe_read_json(list_response) is None
    assert await client._safe_read_json(list_response) is None


@pytest.mark.asyncio
async def test_refresh_install_token_short_circuits_for_missing_token_or_backoff() -> (
    None
):
    client = ShareWorkerClient()
    session = MagicMock()

    assert await client.refresh_install_token(session) is False
    session.post.assert_not_called()

    client.install_token = "tok-old"
    client.next_upload_attempt_at = 200.0
    with patch(
        "custom_components.lipro.core.anonymous_share.share_client.time.time",
        return_value=100.0,
    ):
        assert await client.refresh_install_token(session) is False
    session.post.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_install_token_success_updates_state() -> None:
    client = ShareWorkerClient()
    client.install_token = "tok-old"
    session = MagicMock()
    session.post = MagicMock(
        return_value=_response_context(
            _response(
                status=200,
                payload={
                    "install_token": "tok-new",
                    "token_expires_at": 999,
                    "token_refresh_after": 888,
                },
            )
        )
    )

    assert await client.refresh_install_token(session) is True
    assert client.install_token == "tok-new"
    assert client.token_expires_at == 999
    assert client.token_refresh_after == 888


@pytest.mark.asyncio
async def test_refresh_install_token_handles_401_and_429() -> None:
    client = ShareWorkerClient()
    client.install_token = cast(str | None, "tok-old")
    client.token_expires_at = 100
    client.token_refresh_after = 90

    session_401 = MagicMock()
    session_401.post = MagicMock(
        return_value=_response_context(
            _response(status=401, payload={"code": "TOKEN_EXPIRED"})
        )
    )
    assert await client.refresh_install_token(session_401) is False
    assert client.install_token is None
    assert client.token_expires_at == 0
    assert client.token_refresh_after == 0

    client.install_token = "tok-again"
    session_429 = MagicMock()
    session_429.post = MagicMock(
        return_value=_response_context(
            _response(
                status=429,
                payload={"code": "RATE_LIMIT"},
                headers={"Retry-After": "120"},
            )
        )
    )
    with patch(
        "custom_components.lipro.core.anonymous_share.share_client.time.time",
        return_value=100.0,
    ):
        assert await client.refresh_install_token(session_429) is False
    assert client.next_upload_attempt_at == 160.0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exc",
    [
        TimeoutError(),
        aiohttp.ClientError("network"),
        OSError("io"),
        ValueError("bad"),
    ],
)
async def test_refresh_install_token_handles_transport_exceptions(
    exc: Exception,
) -> None:
    client = ShareWorkerClient()
    client.install_token = "tok-old"
    session = MagicMock()
    session.post = MagicMock(side_effect=exc)
    assert await client.refresh_install_token(session) is False


@pytest.mark.asyncio
async def test_refresh_install_token_with_outcome_exposes_reason_codes() -> None:
    client = ShareWorkerClient()

    missing_token = await client.refresh_install_token_with_outcome(MagicMock())
    assert missing_token.kind == "skipped"
    assert missing_token.reason_code == "missing_install_token"

    client.install_token = "tok-old"
    session = MagicMock()
    session.post = MagicMock(
        return_value=_response_context(
            _response(status=401, payload={"code": "TOKEN_EXPIRED"})
        )
    )

    invalid_token = await client.refresh_install_token_with_outcome(session)

    assert invalid_token.kind == "failed"
    assert invalid_token.reason_code == "token_invalid"
    assert invalid_token.http_status == 401
    assert invalid_token.failure_summary["failure_category"] == "auth"


@pytest.mark.asyncio
async def test_submit_share_payload_backoff_and_missing_installation_id() -> None:
    client = ShareWorkerClient()
    session = MagicMock()
    ensure_loaded = AsyncMock()

    client.next_upload_attempt_at = 200.0
    with patch(
        "custom_components.lipro.core.anonymous_share.share_client.time.time",
        return_value=100.0,
    ):
        assert (
            await client.submit_share_payload(
                session,
                _make_report(),
                label="Anonymous share",
                ensure_loaded=ensure_loaded,
            )
            is False
        )
    ensure_loaded.assert_awaited_once()
    session.post.assert_not_called()

    ensure_loaded = AsyncMock()
    client.next_upload_attempt_at = 0.0
    assert (
        await client.submit_share_payload(
            session,
            {"errors": []},
            label="Anonymous share",
            ensure_loaded=ensure_loaded,
        )
        is False
    )
    ensure_loaded.assert_awaited_once()
    session.post.assert_not_called()

    missing_installation_id = await client.submit_share_payload_with_outcome(
        session,
        {"errors": []},
        label="Anonymous share",
        ensure_loaded=AsyncMock(),
    )
    assert missing_installation_id.kind == "failed"
    assert missing_installation_id.reason_code == "missing_installation_id"


@pytest.mark.asyncio
async def test_submit_share_payload_refreshes_token_before_upload() -> None:
    client = ShareWorkerClient()
    client.install_token = "tok-old"
    client.token_refresh_after = 150
    refresh_install_token = AsyncMock(return_value=False)

    session = MagicMock()
    session.post = MagicMock(
        return_value=_response_context(
            _response(status=400, payload={"code": "INVALID_SCHEMA"})
        )
    )

    with (
        patch(
            "custom_components.lipro.core.anonymous_share.share_client.time.time",
            return_value=200.0,
        ),
        patch.object(client, "refresh_install_token", new=refresh_install_token),
    ):
        result = await client.submit_share_payload(
            session,
            _make_report(),
            label="Anonymous share",
            ensure_loaded=AsyncMock(),
        )

    assert result is False
    refresh_install_token.assert_awaited_once_with(session)


@pytest.mark.asyncio
async def test_submit_share_payload_retries_with_lite_variant_after_413() -> None:
    client = ShareWorkerClient()
    session = MagicMock()
    full_report = _make_report()
    lite_report = {"installation_id": "install-001", "lite": True}

    session.post = MagicMock(
        side_effect=[
            _response_context(_response(status=413, payload={"code": "TOO_LARGE"})),
            _response_context(_response(status=200, payload=None)),
        ]
    )

    with patch(
        "custom_components.lipro.core.anonymous_share.share_client.build_lite_report",
        return_value=lite_report,
    ) as build_lite:
        assert (
            await client.submit_share_payload(
                session,
                full_report,
                label="Anonymous share",
                ensure_loaded=AsyncMock(),
            )
            is True
        )

    assert session.post.call_count == 2
    assert session.post.call_args_list[0].kwargs["json"] == full_report
    assert session.post.call_args_list[1].kwargs["json"] == lite_report
    build_lite.assert_called_once_with(full_report)


@pytest.mark.asyncio
async def test_submit_share_payload_handles_401_token_fallback_and_no_token_reject() -> (
    None
):
    client = ShareWorkerClient()
    client.install_token = cast(str | None, "tok-old")
    session = MagicMock()
    session.post = MagicMock(
        side_effect=[
            _response_context(_response(status=401, payload={"code": "TOKEN_EXPIRED"})),
            _response_context(_response(status=200, payload=None)),
        ]
    )

    assert (
        await client.submit_share_payload(
            session,
            _make_report(),
            label="Anonymous share",
            ensure_loaded=AsyncMock(),
        )
        is True
    )
    assert client.install_token is None
    first_headers = session.post.call_args_list[0].kwargs["headers"]
    second_headers = session.post.call_args_list[1].kwargs["headers"]
    assert first_headers["Authorization"] == "Bearer tok-old"
    assert "Authorization" not in second_headers

    client = ShareWorkerClient()
    session = MagicMock()
    session.post = MagicMock(
        return_value=_response_context(
            _response(status=401, payload={"code": "TOKEN_MISSING"})
        )
    )
    assert (
        await client.submit_share_payload(
            session,
            _make_report(),
            label="Anonymous share",
            ensure_loaded=AsyncMock(),
        )
        is False
    )


@pytest.mark.asyncio
async def test_submit_share_payload_handles_429_and_invalid_schema() -> None:
    client = ShareWorkerClient()
    session_429 = MagicMock()
    session_429.post = MagicMock(
        return_value=_response_context(
            _response(
                status=429,
                payload={"code": "RATE_LIMIT"},
                headers={"Retry-After": "120"},
            )
        )
    )
    with patch(
        "custom_components.lipro.core.anonymous_share.share_client.time.time",
        return_value=10.0,
    ):
        assert (
            await client.submit_share_payload(
                session_429,
                _make_report(),
                label="Anonymous share",
                ensure_loaded=AsyncMock(),
            )
            is False
        )
    assert client.next_upload_attempt_at == 70.0

    session_400 = MagicMock()
    session_400.post = MagicMock(
        return_value=_response_context(
            _response(status=400, payload={"code": "INVALID_SCHEMA"})
        )
    )
    assert (
        await client.submit_share_payload(
            session_400,
            _make_report(),
            label="Anonymous share",
            ensure_loaded=AsyncMock(),
        )
        is False
    )


@pytest.mark.asyncio
async def test_submit_share_payload_with_outcome_exposes_lite_variant_reason() -> None:
    client = ShareWorkerClient()
    session = MagicMock()
    full_report = _make_report()
    lite_report = {"installation_id": "install-001", "lite": True}

    session.post = MagicMock(
        side_effect=[
            _response_context(_response(status=413, payload={"code": "TOO_LARGE"})),
            _response_context(_response(status=200, payload=None)),
        ]
    )

    with patch(
        "custom_components.lipro.core.anonymous_share.share_client.build_lite_report",
        return_value=lite_report,
    ):
        outcome = await client.submit_share_payload_with_outcome(
            session,
            full_report,
            label="Anonymous share",
            ensure_loaded=AsyncMock(),
        )

    assert outcome.kind == "success"
    assert outcome.reason_code == "submitted_lite_payload"


@pytest.mark.asyncio
async def test_submit_share_payload_with_outcome_exposes_rate_limit_reason() -> None:
    client = ShareWorkerClient()
    session = MagicMock()
    session.post = MagicMock(
        return_value=_response_context(
            _response(
                status=429,
                payload={"code": "RATE_LIMIT"},
                headers={"Retry-After": "120"},
            )
        )
    )

    with patch(
        "custom_components.lipro.core.anonymous_share.share_client.time.time",
        return_value=10.0,
    ):
        outcome = await client.submit_share_payload_with_outcome(
            session,
            _make_report(),
            label="Anonymous share",
            ensure_loaded=AsyncMock(),
        )

    assert outcome.kind == "failed"
    assert outcome.reason_code == "rate_limited"
    assert outcome.retry_after_seconds == 120.0


@pytest.mark.asyncio
async def test_submit_share_payload_logs_failure_when_no_variant_succeeds() -> None:
    client = ShareWorkerClient()
    session = MagicMock()
    session.post = MagicMock(
        side_effect=[
            _response_context(_response(status=500, payload={"code": "E1"})),
            _response_context(_response(status=500, payload={"code": "E2"})),
        ]
    )

    with patch(
        "custom_components.lipro.core.anonymous_share.share_client._LOGGER.warning"
    ) as warning:
        assert (
            await client.submit_share_payload(
                session,
                _make_report(),
                label="Anonymous share",
                ensure_loaded=AsyncMock(),
            )
            is False
        )

    assert session.post.call_count == 2
    warning.assert_any_call("%s upload failed with status %s", "Anonymous share", 500)
    assert warning.call_args_list[-1].args == (
        "%s upload failed with status %s",
        "Anonymous share",
        500,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("exc", "expected"),
    [
        (TimeoutError(), ("%s upload timed out", "Anonymous share")),
        (
            aiohttp.ClientError("network"),
            ("%s upload failed: %s", "Anonymous share", ANY),
        ),
        (OSError("io"), ("Unexpected error during %s upload", "anonymous share")),
        (ValueError("bad"), ("Unexpected error during %s upload", "anonymous share")),
    ],
)
async def test_submit_share_payload_handles_exceptions(
    exc: Exception,
    expected: tuple[Any, ...],
) -> None:
    client = ShareWorkerClient()
    session = MagicMock()
    session.post = MagicMock(side_effect=exc)
    ensure_loaded = AsyncMock()

    with (
        patch(
            "custom_components.lipro.core.anonymous_share.share_client._LOGGER.warning"
        ) as warning,
        patch(
            "custom_components.lipro.core.anonymous_share.share_client._LOGGER.exception"
        ) as exception,
    ):
        assert (
            await client.submit_share_payload(
                session,
                _make_report(),
                label="Anonymous share",
                ensure_loaded=ensure_loaded,
            )
            is False
        )

    ensure_loaded.assert_awaited_once()
    if isinstance(exc, (TimeoutError, aiohttp.ClientError)):
        warning.assert_called()
        assert len(warning.call_args.args) == len(expected)
        for actual, expected_part in zip(
            warning.call_args.args, expected, strict=False
        ):
            if expected_part is ANY:
                continue
            assert actual == expected_part
    else:
        exception.assert_called_once_with(*expected)


def test_build_lite_report_matches_external_boundary_fixture() -> None:
    from custom_components.lipro.core.anonymous_share.report_builder import (
        build_lite_report,
        canonicalize_generated_payload,
    )
    from tests.helpers.external_boundary_fixtures import load_external_boundary_fixture

    report = {
        "report_version": "1.1",
        "integration_version": load_external_boundary_fixture(
            "share_worker",
            "lite_report.canonical.json",
        )["integration_version"],
        "ha_version": "2026.3.0",
        "generated_at": "2026-03-12T00:00:00+00:00",
        "installation_id": "install-001",
        "device_count": 2,
        "error_count": 1,
        "devices": [
            {
                "physical_model": "light",
                "iot_name": "lipro_led",
                "device_type": 1,
                "product_id": 100,
                "is_group": False,
                "category": "light",
                "firmware_version": "1.0.0",
                "capabilities": ["on", "brightness"],
                "has_gear_presets": False,
                "gear_count": 0,
                "min_color_temp_kelvin": 2700,
                "max_color_temp_kelvin": 6500,
            }
        ],
        "errors": [
            {
                "type": "api_error",
                "message": "timeout",
                "endpoint": "/device/list",
                "iot_name": "lipro_led",
                "device_type": "ff000001",
                "timestamp": "2026-03-12T00:00:00+00:00",
            }
        ],
    }

    assert canonicalize_generated_payload(build_lite_report(report)) == (
        load_external_boundary_fixture("share_worker", "lite_report.canonical.json")
    )
