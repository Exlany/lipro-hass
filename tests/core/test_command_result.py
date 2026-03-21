"""Unit tests for command result helpers."""

from __future__ import annotations

import asyncio
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import custom_components.lipro.core.command.result as command_result
from custom_components.lipro.core.command.result import (
    build_progressive_retry_delays,
    classify_command_result_payload,
    extract_msg_sn,
    is_command_push_failed,
    poll_command_result_state,
    query_command_result_once,
    resolve_delayed_refresh_delay,
    resolve_polled_command_result,
    run_delayed_refresh,
    should_schedule_delayed_refresh,
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
        last_payload={"code": "100000", "success": False},
        elapsed_seconds=0.3,
        logger=MagicMock(),
    )

    assert verified is False
    assert failure == {
        "reason": "command_result_unconfirmed",
        "code": "100000",
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
        "last_code": "100000",
    }


def test_resolve_polled_command_result_unconfirmed_preserves_last_code_and_message() -> None:
    """Unconfirmed state should retain the last backend code/message."""
    trace: dict[str, object] = {}

    verified, failure = resolve_polled_command_result(
        state="unconfirmed",
        trace=trace,
        route="group_direct",
        msg_sn="abc",
        device_serial="03ab111111111111",
        attempt=3,
        attempt_limit=3,
        last_payload={"code": "140006", "message": "设备未响应", "success": False},
        elapsed_seconds=0.3,
        logger=MagicMock(),
    )

    assert verified is False
    assert failure == {
        "reason": "command_result_unconfirmed",
        "code": "140006",
        "message": "设备未响应",
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
        "last_code": "140006",
        "last_message": "设备未响应",
    }



def test_resolve_polled_command_result_failed_preserves_code_and_message() -> None:
    """Failed state should retain backend rejection details when available."""
    trace: dict[str, object] = {}

    verified, failure = resolve_polled_command_result(
        state="failed",
        trace=trace,
        route="group_direct",
        msg_sn="abc",
        device_serial="03ab111111111111",
        attempt=2,
        attempt_limit=3,
        last_payload={"code": "140005", "message": "参数错误", "success": False},
        elapsed_seconds=0.2,
        logger=MagicMock(),
    )

    assert verified is False
    assert failure == {
        "reason": "command_result_failed",
        "code": "140005",
        "message": "参数错误",
        "route": "group_direct",
        "msg_sn": "abc",
        "device_id": "03ab111111111111",
    }
    assert trace["command_result_verify"] == {
        "enabled": True,
        "verified": False,
        "attempts": 2,
        "msg_sn": "abc",
        "state": "failed",
        "code": "140005",
        "message": "参数错误",
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


def test_classify_command_result_payload_uses_verified_success_contract() -> None:
    assert classify_command_result_payload({"success": "true"}) == "confirmed"
    assert classify_command_result_payload({"success": "0"}) == "failed"
    assert classify_command_result_payload({"code": "0000"}) == "confirmed"
    assert classify_command_result_payload({"code": "140004", "success": False}) == "failed"


def test_classify_command_result_payload_returns_unknown_when_no_match() -> None:
    assert classify_command_result_payload({"message": "waiting"}) == "unknown"


def test_classify_command_result_payload_treats_retryable_codes_as_pending() -> None:
    assert classify_command_result_payload({"code": "100000", "success": False}) == "pending"
    assert classify_command_result_payload({"code": "140006", "success": False}) == "pending"


def test_build_progressive_retry_delays_clips_exponential_backoff_to_budget() -> None:
    assert build_progressive_retry_delays(
        base_delay_seconds=0.35,
        time_budget_seconds=3.0,
        max_attempts=6,
    ) == pytest.approx((0.35, 0.7, 1.4, 0.55))


def test_build_progressive_retry_delays_returns_empty_sequence_when_budget_is_zero() -> None:
    assert build_progressive_retry_delays(
        base_delay_seconds=0.35,
        time_budget_seconds=0.0,
        max_attempts=6,
    ) == ()


def test_build_progressive_retry_delays_stops_when_policy_returns_zero_wait() -> None:
    with patch(
        "custom_components.lipro.core.command.result_policy.compute_exponential_retry_wait_time",
        return_value=0.0,
    ):
        assert (
            build_progressive_retry_delays(
                base_delay_seconds=0.35,
                time_budget_seconds=3.0,
                max_attempts=6,
            )
            == ()
        )


def test_extract_command_result_code_and_message_return_none_for_non_mapping() -> None:
    assert cast(Any, command_result)._extract_command_result_code(None) is None
    assert cast(Any, command_result)._extract_command_result_message(None) is None


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


def test_should_skip_immediate_post_refresh_accepts_slider_only_payloads() -> None:
    assert (
        should_skip_immediate_post_refresh(
            command="CHANGE_STATE",
            properties=[{"key": "brightness", "value": "50"}],
            slider_like_properties={"brightness", "colorTemp"},
        )
        is True
    )


def test_should_skip_immediate_post_refresh_returns_false_for_non_change_state() -> None:
    assert (
        should_skip_immediate_post_refresh(
            command="POWER_ON",
            properties=[{"key": "brightness", "value": "50"}],
            slider_like_properties={"brightness"},
        )
        is False
    )


def test_classify_command_result_payload_treats_other_codes_as_failed() -> None:
    assert classify_command_result_payload({"code": "140005"}) == "failed"


def test_should_schedule_and_resolve_delayed_refresh_cover_mqtt_and_pending_rules() -> (
    None
):
    assert (
        should_schedule_delayed_refresh(
            mqtt_connected=False,
            device_serial="device-1",
            pending_expectations={},
        )
        is True
    )
    assert (
        resolve_delayed_refresh_delay(
            mqtt_connected=True,
            device_serial="device-1",
            pending_expectations={"device-1": object()},
            get_adaptive_post_refresh_delay=lambda serial: 2.5 if serial else 0.0,
        )
        == 2.5
    )


@pytest.mark.asyncio
async def test_run_delayed_refresh_swallows_task_cancellation() -> None:
    request_refresh = AsyncMock()

    with patch(
        "custom_components.lipro.core.command.result_policy.asyncio.sleep",
        new=AsyncMock(side_effect=asyncio.CancelledError()),
    ):
        await run_delayed_refresh(
            delay_seconds=1.0,
            request_refresh=request_refresh,
        )

    request_refresh.assert_not_called()


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
        "custom_components.lipro.core.command.result_policy.asyncio.sleep", new=sleep_mock
    ):
        state, attempt, payload = await poll_command_result_state(
            query_once=query_once,
            classify_payload=classify_command_result_payload,
            retry_delays_seconds=(0.25,),
            on_attempt=on_attempt,
        )

    assert state == "confirmed"
    assert attempt == 2
    assert payload == {"success": True}
    sleep_mock.assert_awaited_once_with(0.25)
    on_attempt.assert_called_once_with(2, "confirmed")


@pytest.mark.asyncio
async def test_poll_command_result_state_returns_unconfirmed_after_pending_budget() -> (
    None
):
    query_once = AsyncMock(side_effect=[{"message": "waiting"}, {"message": "still waiting"}])
    sleep_mock = AsyncMock()

    with patch(
        "custom_components.lipro.core.command.result_policy.asyncio.sleep", new=sleep_mock
    ):
        state, attempt, payload = await poll_command_result_state(
            query_once=query_once,
            classify_payload=classify_command_result_payload,
            retry_delays_seconds=(0.1,),
        )

    assert state == "unconfirmed"
    assert attempt == 2
    assert payload == {"message": "still waiting"}


@pytest.mark.asyncio
async def test_query_command_result_once_reraises_when_predicate_matches() -> None:
    class DummyApiError(Exception):
        def __init__(self, code: int, message: str) -> None:
            super().__init__(message)
            self.code = code

    async def _raise_query(**_: object) -> dict[str, object]:
        raise DummyApiError(401, "auth failed")

    with pytest.raises(DummyApiError, match="auth failed"):
        await query_command_result_once(
            query_command_result=_raise_query,
            lipro_api_error=DummyApiError,
            device_name="Living Room Light",
            device_serial="03ab111111111111",
            device_type_hex="0x0133",
            msg_sn="682550445474476112",
            attempt=1,
            attempt_limit=1,
            logger=MagicMock(),
            should_reraise=lambda err: getattr(err, "code", None) == 401,
        )
