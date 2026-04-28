"""Topicized CommandRuntime orchestration tests."""

from __future__ import annotations

from collections import deque
from unittest.mock import AsyncMock, patch

import pytest

from . import test_command_runtime_support as _support_fixtures
from .test_command_runtime_support import (
    COMMAND_RESULT_STATE_FAILED,
    COMMAND_RESULT_STATE_PENDING,
    CommandDispatchApiError,
    CommandRuntime,
    CommandSender,
    LiproApiError,
    LiproAuthError,
)


@pytest.fixture(name="mock_client")
def _mock_client_fixture():
    return _support_fixtures.mock_client.__wrapped__()


@pytest.fixture(name="mock_device")
def _mock_device_fixture():
    return _support_fixtures.mock_device.__wrapped__()


@pytest.fixture(name="confirmation_tracker")
def _confirmation_tracker_fixture():
    return _support_fixtures.confirmation_tracker.__wrapped__()


@pytest.fixture(name="runtime_deps")
def _runtime_deps_fixture(mock_client, confirmation_tracker):
    return _support_fixtures.runtime_deps.__wrapped__(mock_client, confirmation_tracker)


@pytest.fixture(name="command_runtime")
def _command_runtime_fixture(runtime_deps):
    return _support_fixtures.command_runtime.__wrapped__(runtime_deps)


class TestCommandRuntime:
    """Test CommandRuntime orchestrator."""

    def test_initialization(self, command_runtime):
        """Test runtime initialization."""
        assert command_runtime._debug_mode is True
        assert isinstance(command_runtime._traces, deque)
        assert command_runtime._last_failure is None

    def test_last_command_failure_none(self, command_runtime):
        """Test last_command_failure when no failure."""
        assert command_runtime.last_command_failure is None

    def test_last_command_failure_returns_copy(self, command_runtime):
        """Test last_command_failure returns copy."""
        command_runtime._last_failure = {"reason": "test"}
        failure = command_runtime.last_command_failure

        assert failure == {"reason": "test"}
        assert failure is not command_runtime._last_failure

    def test_last_command_failure_summary_returns_copy(self, command_runtime):
        """Test last_command_failure_summary returns copy."""
        command_runtime._last_failure_summary = {
            "reason": "api_error",
            "error_type": "LiproAuthError",
            "reauth_reason": "auth_error",
            "failure_category": "auth",
        }
        summary = command_runtime.last_command_failure_summary

        assert summary == {
            "reason": "api_error",
            "error_type": "LiproAuthError",
            "reauth_reason": "auth_error",
            "failure_category": "auth",
        }
        assert summary is not command_runtime._last_failure_summary

    @pytest.mark.asyncio
    async def test_send_device_command_push_failed(
        self, command_runtime, mock_device, runtime_deps
    ):
        """Test send_device_command with push failure."""
        with patch.object(command_runtime._sender, "send_command") as mock_send:
            mock_send.return_value = ({"pushSuccess": False}, "iot")

            success, route = await command_runtime.send_device_command(
                device=mock_device,
                command="POWER_ON",
                properties=None,
                fallback_device_id=None,
            )

            assert success is False
            assert route == "iot"
            assert command_runtime._last_failure is not None
            assert command_runtime.last_command_failure_summary == {
                "reason": "push_failed",
                "code": "push_failed",
                "route": "iot",
                "device_id": mock_device.serial,
                "error_type": "PushFailed",
                "failure_category": "protocol",
            }

    @pytest.mark.asyncio
    async def test_send_device_command_missing_msg_sn(
        self, command_runtime, mock_device
    ):
        """Test send_device_command with missing msgSn."""
        with patch.object(command_runtime._sender, "send_command") as mock_send:
            mock_send.return_value = ({"pushSuccess": True}, "iot")

            success, _route = await command_runtime.send_device_command(
                device=mock_device,
                command="POWER_ON",
                properties=None,
                fallback_device_id=None,
            )

            assert success is False
            assert _route == "iot"
            assert command_runtime._last_failure is not None
            assert command_runtime.last_command_failure_summary == {
                "reason": "command_result_unconfirmed",
                "code": "command_result_missing_msgsn",
                "route": "iot",
                "device_id": mock_device.serial,
                "error_type": "CommandResultMissingMsgSn",
                "failure_category": "protocol",
            }

    @pytest.mark.asyncio
    async def test_send_device_command_api_error(
        self, command_runtime, mock_device, runtime_deps
    ):
        """Test send_device_command with API error."""
        with patch.object(command_runtime._sender, "send_command") as mock_send:
            mock_send.side_effect = CommandDispatchApiError(
                route="device_direct",
                error=LiproApiError("API Error"),
            )

            success, route = await command_runtime.send_device_command(
                device=mock_device,
                command="POWER_ON",
                properties=None,
                fallback_device_id=None,
            )

            assert success is False
            assert route == "device_direct"
            assert command_runtime._last_failure is not None

    @pytest.mark.asyncio
    async def test_send_device_command_preserves_planned_route_on_api_error(
        self, command_runtime, mock_device
    ):
        """Route-aware sender failures should keep the planned route in failure summary."""
        with patch.object(command_runtime._sender, "send_command") as mock_send:
            mock_send.side_effect = CommandDispatchApiError(
                route="group_direct",
                error=LiproApiError("routeful boom"),
            )

            success, route = await command_runtime.send_device_command(
                device=mock_device,
                command="POWER_ON",
                properties=None,
                fallback_device_id=None,
            )

            assert success is False
            assert route == "group_direct"
            assert command_runtime.last_command_failure_summary == {
                "reason": "api_error",
                "route": "group_direct",
                "device_id": mock_device.serial,
                "message": "routeful boom",
                "error_type": "LiproApiError",
                "failure_category": "protocol",
            }

    @pytest.mark.asyncio
    async def test_send_device_command_auth_error_triggers_reauth(
        self, command_runtime, mock_device, runtime_deps
    ):
        """Test send_device_command with auth error triggers reauth."""
        with patch.object(command_runtime._sender, "send_command") as mock_send:
            mock_send.side_effect = CommandDispatchApiError(
                route="device_direct",
                error=LiproAuthError("Auth failed"),
            )

            success, route = await command_runtime.send_device_command(
                device=mock_device,
                command="POWER_ON",
                properties=None,
                fallback_device_id=None,
            )

            assert success is False
            assert route == "device_direct"
            assert command_runtime.last_command_failure_summary == {
                "reason": "api_error",
                "route": "device_direct",
                "device_id": mock_device.serial,
                "message": "Auth failed",
                "error_type": "LiproAuthError",
                "failure_category": "auth",
                "reauth_reason": "auth_error",
            }
            runtime_deps["trigger_reauth"].assert_called_once_with("auth_error")

    @pytest.mark.asyncio
    async def test_send_device_command_command_result_failure_sets_summary(
        self, command_runtime, mock_device
    ):
        """Failed command-result verification should publish a normalized summary."""
        with (
            patch.object(command_runtime._sender, "send_command") as mock_send,
            patch.object(
                command_runtime._sender,
                "verify_command_delivery",
                new=AsyncMock(return_value=(False, COMMAND_RESULT_STATE_FAILED)),
            ),
        ):
            mock_send.return_value = ({"pushSuccess": True, "msgSn": "12345"}, "iot")

            success, route = await command_runtime.send_device_command(
                device=mock_device,
                command="POWER_ON",
                properties=None,
                fallback_device_id=None,
            )

            assert success is False
            assert route == "iot"
            assert command_runtime.last_command_failure_summary == {
                "reason": "command_result_failed",
                "code": "command_result_failed",
                "route": "iot",
                "device_id": mock_device.serial,
                "error_type": "CommandResultRejected",
                "failure_category": "protocol",
            }

    @pytest.mark.asyncio
    async def test_send_device_command_command_result_unconfirmed_sets_summary(
        self, command_runtime, mock_device
    ):
        """Unconfirmed verification should publish the canonical timeout-ish summary."""
        with (
            patch.object(command_runtime._sender, "send_command") as mock_send,
            patch.object(
                command_runtime._sender,
                "verify_command_delivery",
                new=AsyncMock(return_value=(False, COMMAND_RESULT_STATE_PENDING)),
            ),
        ):
            mock_send.return_value = ({"pushSuccess": True, "msgSn": "12345"}, "iot")

            success, route = await command_runtime.send_device_command(
                device=mock_device,
                command="POWER_ON",
                properties=None,
                fallback_device_id=None,
            )

            assert success is False
            assert route == "iot"
            assert command_runtime.last_command_failure_summary == {
                "reason": "command_result_unconfirmed",
                "code": "command_result_unconfirmed",
                "route": "iot",
                "device_id": mock_device.serial,
                "error_type": "CommandResultUnconfirmed",
                "failure_category": "protocol",
            }

    @pytest.mark.asyncio
    async def test_send_device_command_success_flow(
        self, command_runtime, mock_device, runtime_deps
    ):
        """Test successful command send flow."""
        with patch.object(command_runtime._sender, "send_command") as mock_send:
            mock_send.return_value = ({"pushSuccess": True, "msgSn": "12345"}, "iot")

            with patch.object(command_runtime, "_verify_delivery") as mock_verify:
                mock_verify.return_value = True

                success, route = await command_runtime.send_device_command(
                    device=mock_device,
                    command="POWER_ON",
                    properties=None,
                    fallback_device_id=None,
                )

                assert success is True
                assert route == "iot"
                assert command_runtime._last_failure is None

    def test_record_trace_when_debug_enabled(self, command_runtime):
        """Test trace recording in debug mode."""
        trace: dict[str, object] = {"test": "data"}
        command_runtime._record_trace(trace)

        assert len(command_runtime._traces) == 1
        assert command_runtime._traces[0] == trace

    def test_record_trace_when_debug_disabled(self, runtime_deps):
        """Test trace not recorded when debug disabled."""
        runtime = CommandRuntime(
            builder=runtime_deps["builder"],
            sender=runtime_deps["sender"],
            retry=runtime_deps["retry"],
            confirmation=runtime_deps["confirmation"],
            trigger_reauth=runtime_deps["trigger_reauth"],
            debug_mode=False,
        )

        trace: dict[str, object] = {"test": "data"}
        runtime._record_trace(trace)

        assert len(runtime._traces) == 0

    def test_get_runtime_metrics_uses_confirmation_contract(
        self, command_runtime
    ) -> None:
        """CommandRuntime should read confirmation metrics through the formal contract."""
        command_runtime._confirmation.get_runtime_metrics = lambda: {"pending": 2}

        assert command_runtime.get_runtime_metrics() == {
            "debug_enabled": True,
            "trace_count": 0,
            "last_failure": None,
            "confirmation": {"pending": 2},
        }

    @pytest.mark.asyncio
    async def test_send_device_command_trace_uses_injected_redactor(
        self, mock_device, runtime_deps
    ) -> None:
        """Command trace should honor the injected identifier redactor."""
        runtime = CommandRuntime(
            builder=runtime_deps["builder"],
            sender=runtime_deps["sender"],
            retry=runtime_deps["retry"],
            confirmation=runtime_deps["confirmation"],
            trigger_reauth=runtime_deps["trigger_reauth"],
            redact_identifier=lambda value: f"redacted:{value}" if value else None,
            debug_mode=True,
        )

        with patch.object(runtime._sender, "send_command") as mock_send:
            mock_send.return_value = ({"pushSuccess": True, "msgSn": "12345"}, "iot")

            with patch.object(runtime, "_verify_delivery") as mock_verify:
                mock_verify.return_value = True

                success, route = await runtime.send_device_command(
                    device=mock_device,
                    command="POWER_ON",
                    properties=None,
                    fallback_device_id="fallback-1",
                )

        assert success is True
        assert route == "iot"
        assert (
            runtime.get_recent_traces()[0]["device_id"]
            == f"redacted:{mock_device.serial}"
        )
        assert (
            runtime.get_recent_traces()[0]["requested_fallback_device_id"]
            == "redacted:fallback-1"
        )


@pytest.mark.asyncio
async def test_verify_command_delivery_auth_errors_bubble(mock_client, mock_device):
    sender = CommandSender(protocol=mock_client)
    trace: dict[str, object] = {}

    with (
        patch(
            "custom_components.lipro.core.coordinator.runtime.command.sender.query_command_result_once",
            side_effect=LiproAuthError("auth boom"),
        ),
        pytest.raises(LiproAuthError, match="auth boom"),
    ):
        await sender.verify_command_delivery(
            msg_sn="12345",
            retry_delays=[0.001],
            trace=trace,
            device=mock_device,
        )
