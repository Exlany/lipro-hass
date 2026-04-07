"""Topicized CommandRuntime builder and retry tests."""

from __future__ import annotations

from .test_command_runtime_support import CommandBuilder, RetryStrategy

pytest_plugins = ("tests.core.coordinator.runtime.test_command_runtime_support",)

class TestCommandBuilder:
    """Test CommandBuilder component."""

    def test_build_trace(self, mock_device):
        """Test trace building."""
        builder = CommandBuilder()
        trace = builder.build_trace(
            device=mock_device, command="POWER_ON", properties=None
        )

        assert trace["device_serial"] == "test_serial_123"
        assert trace["device_name"] == "Test Device"
        assert trace["command"] == "POWER_ON"
        assert trace["success"] is False
        assert "start_time" in trace

    def test_should_skip_immediate_refresh_brightness(self):
        """Test skip immediate refresh for brightness."""
        builder = CommandBuilder()
        properties = [{"key": "brightness", "value": "50"}]

        assert (
            builder.should_skip_immediate_refresh(
                command="CHANGE_STATE", properties=properties
            )
            is True
        )

    def test_should_skip_immediate_refresh_power(self):
        """Test no skip for power command."""
        builder = CommandBuilder()
        properties = [{"key": "powerState", "value": "1"}]

        assert (
            builder.should_skip_immediate_refresh(
                command="CHANGE_STATE", properties=properties
            )
            is False
        )

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
