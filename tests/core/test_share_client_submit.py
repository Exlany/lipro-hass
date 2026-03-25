"""Topicized ShareWorkerClient submission and outcome tests."""
# ruff: noqa: F403, F405, I001

from __future__ import annotations

import typing

from .test_share_client_support import *

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
    refresh_install_token_with_outcome = AsyncMock(
        return_value=build_operation_outcome(
            kind="success",
            reason_code="refresh_success",
        )
    )

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
        patch.object(
            client,
            "refresh_install_token_with_outcome",
            new=refresh_install_token_with_outcome,
        ),
    ):
        result = await client.submit_share_payload(
            session,
            _make_report(),
            label="Anonymous share",
            ensure_loaded=AsyncMock(),
        )

    assert result is False
    refresh_install_token_with_outcome.assert_awaited_once_with(session)


@pytest.mark.parametrize(
    (
        "response",
        "expected_reason",
        "expected_http_status",
        "expected_retry_after",
        "expected_install_token",
        "expected_next_upload_attempt_at",
    ),
    [
        (
            _response(
                status=429,
                payload={"code": "RATE_LIMIT"},
                headers={"Retry-After": "120"},
            ),
            "rate_limited",
            429,
            120.0,
            "tok-old",
            260.0,
        ),
        (
            _response(status=401, payload={"code": "TOKEN_EXPIRED"}),
            "token_invalid",
            401,
            None,
            None,
            0.0,
        ),
    ],
)
@pytest.mark.asyncio
async def test_submit_share_payload_with_outcome_surfaces_refresh_failures_when_due(
    response: MagicMock,
    expected_reason: str,
    expected_http_status: int,
    expected_retry_after: float | None,
    expected_install_token: str | None,
    expected_next_upload_attempt_at: float,
) -> None:
    client = ShareWorkerClient()
    client.install_token = "tok-old"
    client.token_refresh_after = 150
    session = MagicMock()
    session.post = MagicMock(return_value=_response_context(response))

    with patch(
        "custom_components.lipro.core.anonymous_share.share_client.time.time",
        return_value=200.0,
    ):
        outcome = await client.submit_share_payload_with_outcome(
            session,
            _make_report(),
            label="Anonymous share",
            ensure_loaded=AsyncMock(),
        )

    assert outcome.kind == "failed"
    assert outcome.reason_code == expected_reason
    assert outcome.http_status == expected_http_status
    assert outcome.retry_after_seconds == expected_retry_after
    assert client.install_token == expected_install_token
    assert client.next_upload_attempt_at == expected_next_upload_attempt_at
    assert session.post.call_count == 1
    assert session.post.call_args is not None
    assert session.post.call_args.args[0] == SHARE_TOKEN_REFRESH_URL

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
async def test_submit_share_payload_with_outcome_exposes_token_rejected_reason() -> None:
    client = ShareWorkerClient()
    client.install_token = cast(str | None, "tok-old")
    session = MagicMock()
    session.post = MagicMock(
        side_effect=[
            _response_context(_response(status=401, payload={"code": "TOKEN_EXPIRED"})),
            _response_context(_response(status=401, payload={"code": "TOKEN_MISSING"})),
        ]
    )

    outcome = await client.submit_share_payload_with_outcome(
        session,
        _make_report(),
        label="Anonymous share",
        ensure_loaded=AsyncMock(),
    )

    assert outcome.kind == "failed"
    assert outcome.reason_code == "token_rejected"
    assert outcome.http_status == 401
    assert client.install_token is None
    assert session.post.call_count == 2
    assert all(call.args[0] == SHARE_REPORT_URL for call in session.post.call_args_list)

@pytest.mark.asyncio
async def test_submit_share_payload_with_outcome_keeps_413_fallback_terminal_reason() -> None:
    client = ShareWorkerClient()
    session = MagicMock()
    session.post = MagicMock(
        side_effect=[
            _response_context(_response(status=413, payload={"code": "TOO_LARGE"})),
            _response_context(_response(status=413, payload={"code": "TOO_LARGE"})),
        ]
    )

    outcome = await client.submit_share_payload_with_outcome(
        session,
        _make_report(),
        label="Anonymous share",
        ensure_loaded=AsyncMock(),
    )

    assert outcome.kind == "failed"
    assert outcome.reason_code == "payload_too_large"
    assert outcome.http_status == 413
    assert session.post.call_count == 2
    assert all(call.args[0] == SHARE_REPORT_URL for call in session.post.call_args_list)

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
@pytest.mark.asyncio
async def test_submit_share_payload_handles_exceptions(
    exc: Exception,
    expected: tuple[typing.Any, ...],
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
