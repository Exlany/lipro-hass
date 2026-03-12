"""Unit tests for CommandRuntime component."""

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
from custom_components.lipro.core.coordinator.runtime.command import (
    CommandBuilder,
    CommandSender,
    ConfirmationManager,
    RetryStrategy,
)
from custom_components.lipro.core.coordinator.runtime.command_runtime import (
    CommandRuntime,
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
    connect_status_priority_ids: set[str] = set()

    track_background_task = Mock(side_effect=lambda coro: asyncio.create_task(coro))
    request_refresh = AsyncMock()
    mqtt_connected_provider = Mock(return_value=True)
    normalize_device_key = Mock(side_effect=lambda x: x.lower())
    force_connect_status_refresh_setter = Mock()
    trigger_reauth = AsyncMock()

    builder = CommandBuilder(debug_mode=True)
    sender = CommandSender(client=mock_client)
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
        "connect_status_priority_ids": connect_status_priority_ids,
        "normalize_device_key": normalize_device_key,
        "force_connect_status_refresh_setter": force_connect_status_refresh_setter,
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
        connect_status_priority_ids=runtime_deps["connect_status_priority_ids"],
        normalize_device_key=runtime_deps["normalize_device_key"],
        force_connect_status_refresh_setter=runtime_deps["force_connect_status_refresh_setter"],
        trigger_reauth=runtime_deps["trigger_reauth"],
        debug_mode=True,
    )


class TestCommandBuilder:
    """Test CommandBuilder component."""

    def test_build_trace(self, mock_device):
        """Test trace building."""
        builder = CommandBuilder()
        trace = builder.build_trace(device=mock_device, command="POWER_ON", properties=None)

        assert trace["device_serial"] == "test_serial_123"
        assert trace["device_name"] == "Test Device"
        assert trace["command"] == "POWER_ON"
        assert trace["success"] is False
        assert "start_time" in trace

    def test_should_skip_immediate_refresh_brightness(self):
        """Test skip immediate refresh for brightness."""
        builder = CommandBuilder()
        properties = [{"key": "brightness", "value": "50"}]

        assert builder.should_skip_immediate_refresh(command="CHANGE_STATE", properties=properties) is True

    def test_should_skip_immediate_refresh_power(self):
        """Test no skip for power command."""
        builder = CommandBuilder()
        properties = [{"key": "powerState", "value": "1"}]

        assert builder.should_skip_immediate_refresh(command="CHANGE_STATE", properties=properties) is False


class TestRetryStrategy:
    """Test RetryStrategy component."""

    def test_default_values(self):
        """Test default retry configuration."""
        retry = RetryStrategy()
        assert retry.max_attempts == 6

    def test_build_retry_delays(self):
        """Test retry delay generation."""
        retry = RetryStrategy(max_attempts=4, base_delay=0.5)
        delays = retry.build_retry_delays()

        assert len(delays) >= 1  # At least one delay
        assert all(d > 0 for d in delays)

    def test_should_retry(self):
        """Test retry decision logic."""
        retry = RetryStrategy(max_attempts=3)

        assert retry.should_retry(1) is True
        assert retry.should_retry(2) is True
        assert retry.should_retry(3) is False


class TestCommandSender:
    """Test CommandSender component."""

    @pytest.mark.asyncio
    async def test_send_command_success(self, mock_client, mock_device):
        """Test successful command send."""
        sender = CommandSender(client=mock_client)
        trace: dict[str, Any] = {}

        with patch("custom_components.lipro.core.coordinator.runtime.command.sender.execute_command_plan_with_trace") as mock_exec:
            mock_plan = Mock()
            mock_exec.return_value = (mock_plan, {"pushSuccess": True, "msgSn": "12345"}, "iot")

            result, route = await sender.send_command(
                device=mock_device, command="POWER_ON", properties=None, fallback_device_id=None, trace=trace
            )

            assert isinstance(result, dict)
            assert result["pushSuccess"] is True
            assert route == "iot"

    @pytest.mark.asyncio
    async def test_verify_command_delivery_timeout(self, mock_client, mock_device):
        """Test command delivery verification timeout."""
        sender = CommandSender(client=mock_client)
        trace: dict[str, Any] = {}

        # Mock to always return None (no result)
        async def mock_query_once(*args, **kwargs):
            return None

        with patch("custom_components.lipro.core.coordinator.runtime.command.sender.query_command_result_once", side_effect=mock_query_once):
            verified, classification = await sender.verify_command_delivery(
                msg_sn="12345", retry_delays=[0.001], trace=trace, device=mock_device
            )

            assert verified is False
            assert trace["verification_result"] == "timeout"
            assert classification is None

    @pytest.mark.asyncio
    async def test_verify_command_delivery_confirmed_result(self, mock_client, mock_device):
        """Test command delivery with confirmed classification."""
        sender = CommandSender(client=mock_client)
        trace: dict[str, Any] = {}

        async def mock_query_once(*args, **kwargs):
            return {"code": 0}

        with (
            patch(
                "custom_components.lipro.core.coordinator.runtime.command.sender.query_command_result_once",
                side_effect=mock_query_once,
            ),
            patch(
                "custom_components.lipro.core.coordinator.runtime.command.sender.classify_command_result_payload",
                return_value="confirmed",
            ),
        ):
            verified, classification = await sender.verify_command_delivery(
                msg_sn="12345", retry_delays=[0.001], trace=trace, device=mock_device
            )

            assert verified is True
            assert trace["verification_result"] == "confirmed"
            assert classification == "confirmed"

    @pytest.mark.asyncio
    async def test_verify_command_delivery_failed_result(self, mock_client, mock_device):
        """Test command delivery with failed classification."""
        sender = CommandSender(client=mock_client)
        trace: dict[str, Any] = {}

        async def mock_query_once(*args, **kwargs):
            return {"code": 1}

        with (
            patch(
                "custom_components.lipro.core.coordinator.runtime.command.sender.query_command_result_once",
                side_effect=mock_query_once,
            ),
            patch(
                "custom_components.lipro.core.coordinator.runtime.command.sender.classify_command_result_payload",
                return_value="failed",
            ),
        ):
            verified, classification = await sender.verify_command_delivery(
                msg_sn="12345", retry_delays=[0.001], trace=trace, device=mock_device
            )

            assert verified is False
            assert trace["verification_result"] == "failed"
            assert classification == "failed"

    @pytest.mark.asyncio
    async def test_verify_command_delivery_pending_classification(self, mock_client, mock_device):
        """Test command delivery with pending classification that times out."""
        sender = CommandSender(client=mock_client)
        trace: dict[str, Any] = {}

        async def mock_query_once(*args, **kwargs):
            return {"code": 100000}

        with (
            patch(
                "custom_components.lipro.core.coordinator.runtime.command.sender.query_command_result_once",
                side_effect=mock_query_once,
            ),
            patch(
                "custom_components.lipro.core.coordinator.runtime.command.sender.classify_command_result_payload",
                return_value="pending",
            ),
        ):
            verified, classification = await sender.verify_command_delivery(
                msg_sn="12345", retry_delays=[0.001], trace=trace, device=mock_device
            )

            assert verified is False
            assert trace["verification_result"] == "timeout"
            assert classification is None


class TestConfirmationManager:
    """Test ConfirmationManager component."""

    def test_track_command_expectation(self, confirmation_tracker):
        """Test command expectation tracking."""
        pending_expectations: dict[str, PendingCommandExpectation] = {}
        manager = ConfirmationManager(
            confirmation_tracker=confirmation_tracker,
            pending_expectations=pending_expectations,
            device_state_latency_seconds={},
            post_command_refresh_tasks={},
            track_background_task=Mock(),
            request_refresh=AsyncMock(),
            mqtt_connected_provider=Mock(return_value=True),
        )

        properties = [{"key": "powerState", "value": "1"}]
        manager.track_command_expectation(device_serial="test_123", command="CHANGE_STATE", properties=properties)

        assert "test_123" in pending_expectations
        assert pending_expectations["test_123"].expected == {"powerState": "1"}

    def test_get_adaptive_post_refresh_delay(self, confirmation_tracker):
        """Test adaptive delay retrieval."""
        device_state_latency_seconds = {"test_123": 2.5}
        manager = ConfirmationManager(
            confirmation_tracker=confirmation_tracker,
            pending_expectations={},
            device_state_latency_seconds=device_state_latency_seconds,
            post_command_refresh_tasks={},
            track_background_task=Mock(),
            request_refresh=AsyncMock(),
            mqtt_connected_provider=Mock(return_value=True),
        )

        delay = manager.get_adaptive_post_refresh_delay("test_123")
        assert isinstance(delay, float)
        assert delay > 0

    def test_filter_pending_command_mismatches_delegates_to_tracker(self):
        """Test stale-state filtering delegates to the shared confirmation tracker."""
        tracker = Mock()
        tracker.filter_pending_command_mismatches.return_value = ({"powerState": "1"}, {"brightness"})
        manager = ConfirmationManager(
            confirmation_tracker=tracker,
            pending_expectations={},
            device_state_latency_seconds={},
            post_command_refresh_tasks={},
            track_background_task=Mock(),
            request_refresh=AsyncMock(),
            mqtt_connected_provider=Mock(return_value=True),
        )

        filtered, blocked = manager.filter_pending_command_mismatches(
            device_serial="test_123",
            properties={"powerState": "1", "brightness": "5"},
        )

        assert filtered == {"powerState": "1"}
        assert blocked == {"brightness"}
        tracker.filter_pending_command_mismatches.assert_called_once()

    def test_observe_command_confirmation_delegates_to_tracker(self):
        """Test confirmation observation delegates to the shared tracker."""
        tracker = Mock()
        tracker.observe_command_confirmation.return_value = 0.42
        manager = ConfirmationManager(
            confirmation_tracker=tracker,
            pending_expectations={},
            device_state_latency_seconds={},
            post_command_refresh_tasks={},
            track_background_task=Mock(),
            request_refresh=AsyncMock(),
            mqtt_connected_provider=Mock(return_value=True),
        )

        latency = manager.observe_command_confirmation(
            device_serial="test_123",
            properties={"powerState": "1"},
        )

        assert latency == 0.42
        tracker.observe_command_confirmation.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_delayed_refresh(self, confirmation_tracker):
        """Test delayed refresh execution."""
        request_refresh = AsyncMock()
        manager = ConfirmationManager(
            confirmation_tracker=confirmation_tracker,
            pending_expectations={},
            device_state_latency_seconds={},
            post_command_refresh_tasks={},
            track_background_task=Mock(),
            request_refresh=request_refresh,
            mqtt_connected_provider=Mock(return_value=True),
        )

        await manager.run_delayed_refresh(0.001)
        request_refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_schedule_post_command_refresh(self, confirmation_tracker):
        """Test post command refresh scheduling."""
        request_refresh = AsyncMock()
        track_background_task_called = False

        def track_task(coro):
            nonlocal track_background_task_called
            track_background_task_called = True
            return asyncio.create_task(coro)

        manager = ConfirmationManager(
            confirmation_tracker=confirmation_tracker,
            pending_expectations={},
            device_state_latency_seconds={},
            post_command_refresh_tasks={},
            track_background_task=track_task,
            request_refresh=request_refresh,
            mqtt_connected_provider=Mock(return_value=True),
        )

        manager.schedule_post_command_refresh(skip_immediate=False, device_serial="test_123")
        assert track_background_task_called is True
        await asyncio.sleep(0.01)  # Let tasks complete


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


    @pytest.mark.asyncio
    async def test_send_device_command_push_failed(self, command_runtime, mock_device, runtime_deps):
        """Test send_device_command with push failure."""
        with patch.object(command_runtime._sender, "send_command") as mock_send:
            mock_send.return_value = ({"pushSuccess": False}, "iot")

            success, route = await command_runtime.send_device_command(
                device=mock_device, command="POWER_ON", properties=None, fallback_device_id=None
            )

            assert success is False
            assert route == "iot"
            assert command_runtime._last_failure is not None

    @pytest.mark.asyncio
    async def test_send_device_command_missing_msg_sn(self, command_runtime, mock_device):
        """Test send_device_command with missing msgSn."""
        with patch.object(command_runtime._sender, "send_command") as mock_send:
            mock_send.return_value = ({"pushSuccess": True}, "iot")

            success, _route = await command_runtime.send_device_command(
                device=mock_device, command="POWER_ON", properties=None, fallback_device_id=None
            )

            assert success is False
            assert command_runtime._last_failure is not None

    @pytest.mark.asyncio
    async def test_send_device_command_api_error(self, command_runtime, mock_device, runtime_deps):
        """Test send_device_command with API error."""
        with patch.object(command_runtime._sender, "send_command") as mock_send:
            mock_send.side_effect = LiproApiError("API Error")

            success, _route = await command_runtime.send_device_command(
                device=mock_device, command="POWER_ON", properties=None, fallback_device_id=None
            )

            assert success is False
            assert command_runtime._last_failure is not None

    @pytest.mark.asyncio
    async def test_send_device_command_auth_error_triggers_reauth(self, command_runtime, mock_device, runtime_deps):
        """Test send_device_command with auth error triggers reauth."""
        with patch.object(command_runtime._sender, "send_command") as mock_send:
            mock_send.side_effect = LiproAuthError("Auth failed")

            success, _route = await command_runtime.send_device_command(
                device=mock_device, command="POWER_ON", properties=None, fallback_device_id=None
            )

            assert success is False
            runtime_deps["trigger_reauth"].assert_called_once_with("auth_error")

    @pytest.mark.asyncio
    async def test_send_device_command_success_flow(self, command_runtime, mock_device, runtime_deps):
        """Test successful command send flow."""
        with patch.object(command_runtime._sender, "send_command") as mock_send:
            mock_send.return_value = ({"pushSuccess": True, "msgSn": "12345"}, "iot")

            with patch.object(command_runtime, "_verify_delivery") as mock_verify:
                mock_verify.return_value = True

                success, route = await command_runtime.send_device_command(
                    device=mock_device, command="POWER_ON", properties=None, fallback_device_id=None
                )

                assert success is True
                assert route == "iot"
                assert command_runtime._last_failure is None
                runtime_deps["force_connect_status_refresh_setter"].assert_called_with(True)

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
            connect_status_priority_ids=runtime_deps["connect_status_priority_ids"],
            normalize_device_key=runtime_deps["normalize_device_key"],
            force_connect_status_refresh_setter=runtime_deps["force_connect_status_refresh_setter"],
            trigger_reauth=runtime_deps["trigger_reauth"],
            debug_mode=False,
        )

        trace: dict[str, object] = {"test": "data"}
        runtime._record_trace(trace)

        assert len(runtime._traces) == 0
