"""Unit tests for command result helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.lipro.core.command_result import resolve_polled_command_result


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
