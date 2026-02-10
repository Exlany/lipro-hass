"""Tests for debounce helper."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

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
