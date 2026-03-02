"""Tests for debounce helper."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.lipro.helpers.debounce import DEFAULT_DEBOUNCE_DELAY, Debouncer


class TestDebouncer:
    """Tests for Debouncer class."""

    @pytest.mark.asyncio
    async def test_debounce_single_call(self):
        """Test single debounced call executes after delay."""
        mock_func = AsyncMock()
        debouncer = Debouncer(delay=0.05)

        await debouncer.async_call(mock_func, "arg1", key="value")

        # Should not be called immediately
        mock_func.assert_not_called()

        # Wait for debounce delay
        await asyncio.sleep(0.1)

        mock_func.assert_called_once_with("arg1", key="value")

    @pytest.mark.asyncio
    async def test_debounce_multiple_calls(self):
        """Test multiple rapid calls only execute once."""
        mock_func = AsyncMock()
        debouncer = Debouncer(delay=0.05)

        # Make multiple rapid calls
        await debouncer.async_call(mock_func, "call1")
        await debouncer.async_call(mock_func, "call2")
        await debouncer.async_call(mock_func, "call3")

        # Wait for debounce delay
        await asyncio.sleep(0.1)

        # Only the last call should execute
        mock_func.assert_called_once_with("call3")

    @pytest.mark.asyncio
    async def test_debounce_cancel(self):
        """Test cancelling pending debounced call."""
        mock_func = AsyncMock()
        debouncer = Debouncer(delay=0.1)

        await debouncer.async_call(mock_func, "arg")
        debouncer.cancel()

        # Wait for what would have been the delay
        await asyncio.sleep(0.15)

        # Should not be called
        mock_func.assert_not_called()

    @pytest.mark.asyncio
    async def test_debounce_cancel_no_pending(self):
        """Test cancel when no pending call."""
        debouncer = Debouncer(delay=0.1)
        # Should not raise
        debouncer.cancel()

    @pytest.mark.asyncio
    async def test_debounce_exception_handling(self):
        """Test exception in debounced function is handled."""
        mock_func = AsyncMock(side_effect=ValueError("Test error"))
        debouncer = Debouncer(delay=0.05)

        await debouncer.async_call(mock_func)

        # Wait for execution
        await asyncio.sleep(0.1)

        # Should have been called (exception logged but not raised)
        mock_func.assert_called_once()
        assert isinstance(debouncer.last_error, ValueError)
        assert str(debouncer.last_error) == "Test error"

    @pytest.mark.asyncio
    async def test_debounce_error_callback_invoked(self):
        """Debouncer should surface failures via optional error callback."""
        err_callback = Mock()
        mock_func = AsyncMock(side_effect=RuntimeError("boom"))
        debouncer = Debouncer(delay=0.05, on_error=err_callback)

        await debouncer.async_call(mock_func)
        await asyncio.sleep(0.1)

        err_callback.assert_called_once()
        callback_err = err_callback.call_args[0][0]
        assert isinstance(callback_err, RuntimeError)
        assert str(callback_err) == "boom"

    @pytest.mark.asyncio
    async def test_debounce_clears_last_error_after_success(self):
        """A successful execution should clear previously stored error."""
        err_callback = Mock()
        failing = AsyncMock(side_effect=ValueError("first"))
        success = AsyncMock()
        debouncer = Debouncer(delay=0.05, on_error=err_callback)

        await debouncer.async_call(failing)
        await asyncio.sleep(0.1)
        assert isinstance(debouncer.last_error, ValueError)

        await debouncer.async_call(success)
        await asyncio.sleep(0.1)

        assert debouncer.last_error is None

    @pytest.mark.asyncio
    async def test_debounce_error_callback_failure_is_suppressed(self):
        """Error callback exceptions should not leak as task failures."""
        callback = Mock(side_effect=RuntimeError("callback boom"))
        mock_func = AsyncMock(side_effect=ValueError("func boom"))
        debouncer = Debouncer(delay=0.05, on_error=callback)

        await debouncer.async_call(mock_func)
        await asyncio.sleep(0.1)

        callback.assert_called_once()
        assert isinstance(debouncer.last_error, ValueError)
        assert str(debouncer.last_error) == "func boom"

    @pytest.mark.asyncio
    async def test_debounce_default_delay(self):
        """Test default delay value."""
        debouncer = Debouncer()
        assert debouncer._delay == DEFAULT_DEBOUNCE_DELAY

    @pytest.mark.asyncio
    async def test_debounce_custom_delay(self):
        """Test custom delay value."""
        debouncer = Debouncer(delay=1.5)
        assert debouncer._delay == 1.5


class TestDefaultDebounceDelay:
    """Tests for default debounce delay constant."""

    def test_default_delay_value(self):
        """Test default delay is 0.5 seconds."""
        assert DEFAULT_DEBOUNCE_DELAY == 0.5
