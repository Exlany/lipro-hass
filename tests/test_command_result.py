"""Unit tests for command result helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.lipro.core.command.result import (
    classify_command_result_payload,
    extract_msg_sn,
    is_command_push_failed,
    resolve_polled_command_result,
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


def test_is_command_push_failed_accepts_bool_like_payloads() -> None:
    assert is_command_push_failed({"pushSuccess": "0"}) is True
    assert is_command_push_failed({"pushSuccess": "false"}) is True
    assert is_command_push_failed({"pushSuccess": 1}) is False


def test_classify_command_result_payload_coerces_success_and_pushsuccess() -> None:
    assert classify_command_result_payload({"success": "true"}) == "confirmed"
    assert classify_command_result_payload({"success": "0"}) == "failed"
    assert classify_command_result_payload({"pushSuccess": "FALSE"}) == "failed"
