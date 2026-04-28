"""Direct tests for CommandRuntime outcome support helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproRefreshTokenExpiredError,
)
from custom_components.lipro.core.coordinator.runtime.command_runtime_outcome_support import (
    _finalize_success,
    _handle_api_error,
    _handle_verify_delivery_result,
    _record_command_result_failure,
    _resolve_reauth_reason,
    _verify_delivery,
)
from custom_components.lipro.core.coordinator.runtime.command_runtime_support import (
    _CommandRequest,
)

from . import test_command_runtime_support as _support_fixtures


@pytest.fixture(name="mock_device")
def _mock_device_fixture():
    return _support_fixtures.mock_device.__wrapped__()


def test_record_command_result_failure_marks_trace_and_uses_runtime_callback(
    mock_device,
) -> None:
    trace: dict[str, object] = {}
    record_failure = MagicMock(return_value={"reason": "command_result_failed"})

    summary = _record_command_result_failure(
        trace=trace,
        route="iot",
        device_serial=mock_device.serial,
        reason="command_result_failed",
        error_type="CommandResultRejected",
        record_failure=record_failure,
    )

    assert summary == {"reason": "command_result_failed"}
    assert trace["route"] == "iot"
    assert trace["success"] is False
    assert trace["error"] == "CommandResultRejected"
    record_failure.assert_called_once()


@pytest.mark.asyncio
async def test_verify_delivery_returns_true_without_recording_failure(
    mock_device,
) -> None:
    sender = MagicMock()
    sender.verify_command_delivery = AsyncMock(return_value=(True, "confirmed"))
    retry = MagicMock()
    retry.build_retry_delays.return_value = [0.1, 0.2]
    record_failure = MagicMock()

    verified = await _verify_delivery(
        trace={},
        route="iot",
        msg_sn="12345",
        device=mock_device,
        sender=sender,
        retry=retry,
        record_failure=record_failure,
    )

    assert verified is True
    sender.verify_command_delivery.assert_awaited_once()
    record_failure.assert_not_called()


@pytest.mark.asyncio
async def test_verify_delivery_records_unconfirmed_failure(mock_device) -> None:
    sender = MagicMock()
    sender.verify_command_delivery = AsyncMock(return_value=(False, "pending"))
    retry = MagicMock()
    retry.build_retry_delays.return_value = [0.1]
    record_failure = MagicMock(return_value={"reason": "command_result_unconfirmed"})
    trace: dict[str, object] = {}

    verified = await _verify_delivery(
        trace=trace,
        route="iot",
        msg_sn="12345",
        device=mock_device,
        sender=sender,
        retry=retry,
        record_failure=record_failure,
    )

    assert verified is False
    assert trace["error"] == "CommandResultUnconfirmed"
    record_failure.assert_called_once()


def test_handle_verify_delivery_result_records_failed_summary(mock_device) -> None:
    trace: dict[str, object] = {}
    record_failure = MagicMock(return_value={"reason": "command_result_failed"})

    verified = _handle_verify_delivery_result(
        verified=False,
        command_result_state="failed",
        trace=trace,
        route="iot",
        device_serial=mock_device.serial,
        record_failure=record_failure,
    )

    assert verified is False
    assert trace["error"] == "CommandResultRejected"
    record_failure.assert_called_once_with(
        trace=trace,
        failure={
            "reason": "command_result_failed",
            "code": "command_result_failed",
            "route": "iot",
            "device_id": mock_device.serial,
        },
        error_type="CommandResultRejected",
    )


def test_handle_verify_delivery_result_returns_true_when_verified(mock_device) -> None:
    trace: dict[str, object] = {}
    record_failure = MagicMock()

    verified = _handle_verify_delivery_result(
        verified=True,
        command_result_state="pending",
        trace=trace,
        route="iot",
        device_serial=mock_device.serial,
        record_failure=record_failure,
    )

    assert verified is True
    assert trace == {}
    record_failure.assert_not_called()


def test_finalize_success_updates_confirmation_and_clears_failure(mock_device) -> None:
    builder = MagicMock()
    builder.should_skip_immediate_refresh.return_value = True
    confirmation = MagicMock()
    record_trace = MagicMock()
    clear_failure_state = MagicMock()
    trace: dict[str, object] = {}
    request = _CommandRequest(
        device=mock_device,
        command="POWER_ON",
        properties=None,
        fallback_device_id=None,
    )

    _finalize_success(
        request=request,
        route="iot",
        trace=trace,
        builder=builder,
        confirmation=confirmation,
        record_trace=record_trace,
        clear_failure_state=clear_failure_state,
    )

    confirmation.track_command_expectation.assert_called_once_with(
        device_serial=mock_device.serial,
        command="POWER_ON",
        properties=None,
    )
    record_trace.assert_called_once_with(trace)
    clear_failure_state.assert_called_once_with()
    assert trace["route"] == "iot"
    assert trace["success"] is True


def test_resolve_reauth_reason_matches_auth_errors() -> None:
    assert (
        _resolve_reauth_reason(LiproRefreshTokenExpiredError("expired"))
        == "auth_expired"
    )
    assert _resolve_reauth_reason(LiproAuthError("auth")) == "auth_error"
    assert _resolve_reauth_reason(LiproApiError("generic")) is None


@pytest.mark.asyncio
async def test_handle_api_error_records_failure_and_triggers_reauth(
    mock_device,
) -> None:
    trace: dict[str, object] = {}
    record_failure = MagicMock(return_value={"reason": "api_error"})
    trigger_reauth = AsyncMock()
    request = _CommandRequest(
        device=mock_device,
        command="POWER_ON",
        properties=None,
        fallback_device_id=None,
    )

    await _handle_api_error(
        request=request,
        trace=trace,
        route="device_direct",
        err=LiproAuthError("boom"),
        record_failure=record_failure,
        trigger_reauth=trigger_reauth,
    )

    record_failure.assert_called_once()
    trigger_reauth.assert_awaited_once_with("auth_error")
    assert trace["route"] == "device_direct"
    assert trace["success"] is False


@pytest.mark.asyncio
async def test_handle_api_error_skips_reauth_for_generic_api_error(mock_device) -> None:
    trace: dict[str, object] = {}
    record_failure = MagicMock(return_value={"reason": "api_error"})
    trigger_reauth = AsyncMock()
    request = _CommandRequest(
        device=mock_device,
        command="POWER_ON",
        properties=None,
        fallback_device_id=None,
    )

    await _handle_api_error(
        request=request,
        trace=trace,
        route="device_direct",
        err=LiproApiError("boom"),
        record_failure=record_failure,
        trigger_reauth=trigger_reauth,
    )

    record_failure.assert_called_once()
    trigger_reauth.assert_not_awaited()
