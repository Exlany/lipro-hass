"""Topicized CommandRuntime confirmation-manager tests."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from .test_command_runtime_support import ConfirmationManager, PendingCommandExpectation

pytest_plugins = ("tests.core.coordinator.runtime.test_command_runtime_support",)


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
        manager.track_command_expectation(
            device_serial="test_123", command="CHANGE_STATE", properties=properties
        )

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
        tracker.filter_pending_command_mismatches.return_value = (
            {"powerState": "1"},
            {"brightness"},
        )
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

        manager.schedule_post_command_refresh(
            skip_immediate=False, device_serial="test_123"
        )
        assert track_background_task_called is True
        await asyncio.sleep(0.01)  # Let tasks complete
