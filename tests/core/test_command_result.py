"""Unit tests for command result helpers."""

from __future__ import annotations

from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro.core.command.result import (
    classify_command_result_payload,
    extract_msg_sn,
    is_command_push_failed,
    poll_command_result_state,
    query_command_result_once,
    resolve_polled_command_result,
    should_skip_immediate_post_refresh,
)


def test_resolve_polled_command_result_confirmed() -> None:
    """Confirmed state should mark verification success without failure payload."""
    trace: dict[str, object] = {}

    verified, failure = resolve_polled_command_result(
        state="confirmed",
        trace=trace,
        route="device_direct",
        msg_sn="abc",
        device_serial="03ab111111111111",
        attempt=1,
        attempt_limit=3,
        last_payload={"success": True},
        elapsed_seconds=0.1,
        logger=MagicMock(),
    )

    assert verified is True
    assert failure is None
    assert trace["command_result_verify"] == {
        "enabled": True,
        "verified": True,
        "attempts": 1,
        "msg_sn": "abc",
    }


def test_resolve_polled_command_result_failed() -> None:
    """Failed state should return rejected failure payload."""
    trace: dict[str, object] = {}

    verified, failure = resolve_polled_command_result(
        state="failed",
        trace=trace,
        route="group_direct",
        msg_sn="abc",
        device_serial="03ab111111111111",
        attempt=2,
        attempt_limit=3,
        last_payload={"success": False},
        elapsed_seconds=0.2,
        logger=MagicMock(),
    )

    assert verified is False
    assert failure == {
        "reason": "command_result_failed",
        "code": "command_result_failed",
        "route": "group_direct",
        "msg_sn": "abc",
        "device_id": "03ab111111111111",
    }
    assert trace["error"] == "CommandResultRejected"


def test_resolve_polled_command_result_unconfirmed_uses_last_state() -> None:
    """Unconfirmed state should include normalized last-state details."""
    trace: dict[str, object] = {}

    verified, failure = resolve_polled_command_result(
        state="unconfirmed",
        trace=trace,
        route="group_direct",
        msg_sn="abc",
        device_serial="03ab111111111111",
        attempt=3,
        attempt_limit=3,
        last_payload={"result": "pending"},
        elapsed_seconds=0.3,
        logger=MagicMock(),
    )

    assert verified is False
    assert failure == {
        "reason": "command_result_unconfirmed",
        "code": "command_result_unconfirmed",
        "route": "group_direct",
        "msg_sn": "abc",
        "device_id": "03ab111111111111",
    }
    assert trace["command_result_verify"] == {
        "enabled": True,
        "verified": False,
        "attempts": 3,
        "msg_sn": "abc",
        "last_state": "pending",
    }


def test_extract_msg_sn_coerces_int_float_and_str() -> None:
    assert extract_msg_sn({"msgSn": 123}) == "123"
    assert extract_msg_sn({"msgSn": 123.0}) == "123"
    assert extract_msg_sn({"msgSn": "  abc  "}) == "abc"


def test_extract_msg_sn_ignores_bool_and_blank_and_uses_fallback_keys() -> None:
    assert extract_msg_sn({"msgSn": True}) is None
    assert extract_msg_sn({"msgSn": "   ", "msg_sn": "x"}) == "x"


def test_extract_msg_sn_ignores_non_integral_float() -> None:
    assert extract_msg_sn({"msgSn": 123.4}) is None


def test_extract_msg_sn_returns_none_for_non_dict_payload() -> None:
    assert extract_msg_sn(None) is None
    assert extract_msg_sn("682550445474476112") is None


def test_is_command_push_failed_accepts_bool_like_payloads() -> None:
    assert is_command_push_failed({"pushSuccess": "0"}) is True
    assert is_command_push_failed({"pushSuccess": "false"}) is True
    assert is_command_push_failed({"pushSuccess": 1}) is False


def test_classify_command_result_payload_coerces_success_and_pushsuccess() -> None:
    assert classify_command_result_payload({"success": "true"}) == "confirmed"
    assert classify_command_result_payload({"success": "0"}) == "failed"
    assert classify_command_result_payload({"pushSuccess": "FALSE"}) == "failed"


def test_classify_command_result_payload_returns_unknown_when_no_match() -> None:
    assert classify_command_result_payload({"result": "in_progress"}) == "unknown"


def test_should_skip_immediate_post_refresh_returns_false_without_valid_key() -> None:
    assert (
        should_skip_immediate_post_refresh(
            command="CHANGE_STATE",
            properties=cast(
                list[dict[str, str]] | None,
                [{"value": "1"}, {"key": 1}, {}],
            ),
            slider_like_properties={"brightness"},
        )
        is False
    )


@pytest.mark.asyncio
async def test_query_command_result_once_returns_none_on_api_error() -> None:
    class DummyApiError(Exception):
        def __init__(self, code: int, message: str) -> None:
            super().__init__(message)
            self.code = code

    async def _raise_query(**_: object) -> dict[str, object]:
        raise DummyApiError(1001, "query failed")

    logger = MagicMock()
    result = await query_command_result_once(
        query_command_result=_raise_query,
        lipro_api_error=DummyApiError,
        device_name="Living Room Light",
        device_serial="03ab111111111111",
        device_type_hex="0x0133",
        msg_sn="682550445474476112",
        attempt=2,
        attempt_limit=3,
        logger=logger,
    )

    assert result is None
    logger.debug.assert_called_once()
    assert "query_command_result failed" in logger.debug.call_args.args[0]
    assert logger.debug.call_args.args[5] == 1001


@pytest.mark.asyncio
async def test_poll_command_result_state_retries_when_payload_is_none() -> None:
    query_once = AsyncMock(side_effect=[None, {"success": True}])
    on_attempt = MagicMock()
    sleep_mock = AsyncMock()

    with patch(
        "custom_components.lipro.core.command.result.asyncio.sleep", new=sleep_mock
    ):
        state, attempt, payload = await poll_command_result_state(
            query_once=query_once,
            classify_payload=classify_command_result_payload,
            attempt_limit=2,
            interval_seconds=0.25,
            on_attempt=on_attempt,
        )

    assert state == "confirmed"
    assert attempt == 2
    assert payload == {"success": True}
    sleep_mock.assert_awaited_once_with(0.25)
    on_attempt.assert_called_once_with(2, "confirmed")
