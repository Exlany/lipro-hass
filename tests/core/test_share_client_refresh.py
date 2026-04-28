"""Topicized ShareWorkerClient token-refresh tests."""
# ruff: noqa: F403, F405

from __future__ import annotations

from .test_share_client_support import *


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


@pytest.mark.parametrize(
    "exc",
    [
        TimeoutError(),
        aiohttp.ClientError("network"),
        OSError("io"),
        ValueError("bad"),
    ],
)
@pytest.mark.asyncio
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
async def test_refresh_install_token_with_outcome_reports_invalid_refresh_payload() -> (
    None
):
    client = ShareWorkerClient()
    client.install_token = "tok-old"
    session = MagicMock()
    session.post = MagicMock(
        return_value=_response_context(
            _response(status=200, payload=["bad-payload"], async_json=False)
        )
    )

    outcome = await client.refresh_install_token_with_outcome(session)

    assert outcome.kind == "failed"
    assert outcome.reason_code == "invalid_refresh_payload"
    assert outcome.http_status == 200
    assert client.install_token == "tok-old"
    assert session.post.call_args is not None
    assert session.post.call_args.args[0] == SHARE_TOKEN_REFRESH_URL
