"""Shared fixtures and imports for topicized CommandRuntime suites."""
# ruff: noqa: F401


from __future__ import annotations

import asyncio
from collections import deque
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.lipro.core.api import LiproApiError, LiproAuthError
from custom_components.lipro.core.command.confirmation_tracker import (
    CommandConfirmationTracker,
)
from custom_components.lipro.core.command.expectation import PendingCommandExpectation
from custom_components.lipro.core.command.result import (
    COMMAND_FAILURE_CODE_MISSING_MSGSN,
    COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED,
    COMMAND_FAILURE_REASON_PUSH_FAILED,
    COMMAND_RESULT_STATE_CONFIRMED,
    COMMAND_RESULT_STATE_FAILED,
    COMMAND_RESULT_STATE_PENDING,
    COMMAND_VERIFICATION_RESULT_TIMEOUT,
)
from custom_components.lipro.core.coordinator.runtime.command import (
    CommandBuilder,
    CommandDispatchApiError,
    CommandSender,
    ConfirmationManager,
    RetryStrategy,
)
from custom_components.lipro.core.coordinator.runtime.command_runtime import (
    CommandRuntime,
)
from custom_components.lipro.core.coordinator.runtime.command_runtime_support import (
    _build_failure_summary,
    _build_request_trace,
    _build_runtime_metrics,
    _CommandRequest,
    _handle_command_dispatch_result,
)
from custom_components.lipro.core.device import LiproDevice


@pytest.fixture
def mock_client():
    """Create mock API client."""
    client = Mock()
    client.query_command_result = AsyncMock()
    return client


@pytest.fixture
def mock_device():
    """Create mock device."""
    device = Mock(spec=LiproDevice)
    device.serial = "test_serial_123"
    device.name = "Test Device"
    device.device_type = "light"
    device.iot_name = "iot-name"
    device.physical_model = "model-x"
    device.is_group = False
    return device


@pytest.fixture
def confirmation_tracker():
    """Create confirmation tracker."""
    return CommandConfirmationTracker(
        default_post_command_refresh_delay_seconds=3.0,
        min_post_command_refresh_delay_seconds=1.5,
        max_post_command_refresh_delay_seconds=8.0,
        state_latency_margin_seconds=0.6,
        state_latency_ewma_alpha=0.35,
        state_confirm_timeout_seconds=20.0,
    )


@pytest.fixture
def runtime_deps(mock_client, confirmation_tracker):
    """Create runtime dependencies."""
    pending_expectations: dict[str, PendingCommandExpectation] = {}
    device_state_latency_seconds: dict[str, float] = {}
    post_command_refresh_tasks: dict[str, asyncio.Task[Any]] = {}
    track_background_task = Mock(side_effect=lambda coro: asyncio.create_task(coro))
    request_refresh = AsyncMock()
    mqtt_connected_provider = Mock(return_value=True)
    trigger_reauth = AsyncMock()

    builder = CommandBuilder(debug_mode=True)
    sender = CommandSender(protocol=mock_client)
    retry = RetryStrategy()
    confirmation = ConfirmationManager(
        confirmation_tracker=confirmation_tracker,
        pending_expectations=pending_expectations,
        device_state_latency_seconds=device_state_latency_seconds,
        post_command_refresh_tasks=post_command_refresh_tasks,
        track_background_task=track_background_task,
        request_refresh=request_refresh,
        mqtt_connected_provider=mqtt_connected_provider,
    )

    return {
        "builder": builder,
        "sender": sender,
        "retry": retry,
        "confirmation": confirmation,
        "trigger_reauth": trigger_reauth,
        "track_background_task": track_background_task,
        "request_refresh": request_refresh,
    }


@pytest.fixture
def command_runtime(runtime_deps):
    """Create CommandRuntime instance."""
    return CommandRuntime(
        builder=runtime_deps["builder"],
        sender=runtime_deps["sender"],
        retry=runtime_deps["retry"],
        confirmation=runtime_deps["confirmation"],
        trigger_reauth=runtime_deps["trigger_reauth"],
        debug_mode=True,
    )


def test_build_request_trace_uses_shared_trace_fields(mock_device) -> None:
    request = _CommandRequest(
        device=mock_device,
        command="POWER_ON",
        properties=[{"key": "powerState", "value": "1"}],
        fallback_device_id="fallback-1",
    )

    trace = _build_request_trace(
        request=request,
        redact_identifier=lambda value: f"redacted:{value}" if value else None,
    )

    assert trace["device_id"] == "redacted:test_serial_123"
    assert trace["requested_fallback_device_id"] == "redacted:fallback-1"
    assert trace["requested_command"] == "POWER_ON"
    assert trace["requested_property_keys"] == ["powerState"]


def test_handle_command_dispatch_result_returns_msg_sn_without_failure(mock_device) -> None:
    record_failure = Mock()
    request = _CommandRequest(
        device=mock_device,
        command="POWER_ON",
        properties=None,
        fallback_device_id=None,
    )

    msg_sn = _handle_command_dispatch_result(
        request=request,
        result={"pushSuccess": True, "msgSn": "12345"},
        trace={},
        route="iot",
        logger=Mock(),
        record_failure=record_failure,
    )

    assert msg_sn == "12345"
    record_failure.assert_not_called()


def test_handle_command_dispatch_result_records_push_failure(mock_device) -> None:
    record_failure = Mock(return_value={"reason": "push_failed"})
    request = _CommandRequest(
        device=mock_device,
        command="POWER_ON",
        properties=None,
        fallback_device_id=None,
    )
    trace: dict[str, object] = {}

    msg_sn = _handle_command_dispatch_result(
        request=request,
        result={"pushSuccess": False, "message": "boom"},
        trace=trace,
        route="iot",
        logger=Mock(),
        record_failure=record_failure,
    )

    assert msg_sn is None
    record_failure.assert_called_once_with(
        trace=trace,
        failure={
            "reason": COMMAND_FAILURE_REASON_PUSH_FAILED,
            "code": COMMAND_FAILURE_REASON_PUSH_FAILED,
            "route": "iot",
            "device_id": mock_device.serial,
            "command": "POWER_ON",
        },
        error_type="PushFailed",
    )
    assert trace == {
        "route": "iot",
        "success": False,
        "error": "PushFailed",
        "error_message": "pushSuccess=false",
    }


def test_handle_command_dispatch_result_records_missing_msg_sn(mock_device) -> None:
    record_failure = Mock(return_value={"reason": "missing_msg_sn"})
    request = _CommandRequest(
        device=mock_device,
        command="POWER_ON",
        properties=None,
        fallback_device_id=None,
    )
    trace: dict[str, object] = {}

    msg_sn = _handle_command_dispatch_result(
        request=request,
        result={"pushSuccess": True},
        trace=trace,
        route="device_direct",
        logger=Mock(),
        record_failure=record_failure,
    )

    assert msg_sn is None
    record_failure.assert_called_once_with(
        trace=trace,
        failure={
            "reason": COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED,
            "code": COMMAND_FAILURE_CODE_MISSING_MSGSN,
            "route": "device_direct",
            "device_id": mock_device.serial,
            "command": "POWER_ON",
        },
        error_type="CommandResultMissingMsgSn",
    )
    assert trace == {
        "route": "device_direct",
        "success": False,
        "error": "CommandResultMissingMsgSn",
        "error_message": COMMAND_FAILURE_CODE_MISSING_MSGSN,
        "command_result_verify": {"enabled": True, "verified": False, "attempts": 0},
    }


def test_build_failure_summary_marks_auth_failures() -> None:
    summary = _build_failure_summary(
        failure={"reason": "api_error", "route": "iot", "device_id": "abc"},
        error_type="LiproAuthError",
        reauth_reason="auth_error",
    )

    assert summary == {
        "reason": "api_error",
        "route": "iot",
        "device_id": "abc",
        "error_type": "LiproAuthError",
        "reauth_reason": "auth_error",
        "failure_category": "auth",
    }


def test_build_runtime_metrics_shapes_failure_and_confirmation() -> None:
    last_failure = {"reason": "push_failed"}
    confirmation_metrics = {"pending": 2}

    metrics = _build_runtime_metrics(
        debug_enabled=True,
        trace_count=3,
        last_failure=last_failure,
        confirmation_metrics=confirmation_metrics,
    )

    assert metrics == {
        "debug_enabled": True,
        "trace_count": 3,
        "last_failure": {"reason": "push_failed"},
        "confirmation": {"pending": 2},
    }
    assert metrics["last_failure"] is not last_failure
    assert metrics["confirmation"] is not confirmation_metrics



__all__ = [
    "COMMAND_RESULT_STATE_CONFIRMED",
    "COMMAND_RESULT_STATE_FAILED",
    "COMMAND_RESULT_STATE_PENDING",
    "COMMAND_VERIFICATION_RESULT_TIMEOUT",
    "CommandBuilder",
    "CommandDispatchApiError",
    "CommandRuntime",
    "CommandSender",
    "ConfirmationManager",
    "LiproApiError",
    "LiproAuthError",
    "PendingCommandExpectation",
    "RetryStrategy",
    "command_runtime",
    "confirmation_tracker",
    "mock_client",
    "mock_device",
    "runtime_deps",
]
