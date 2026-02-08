"""Tests for debounce helper."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.helpers.debounce import (
    DEFAULT_DEBOUNCE_DELAY,
    Debouncer,
    DebouncerManager,
)


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


class TestDebouncerManager:
    """Tests for DebouncerManager class."""

    def test_get_debouncer_creates_new(self):
        """Test get_debouncer creates new debouncer."""
        manager = DebouncerManager()

        debouncer = manager.get_debouncer("entity1_brightness")

        assert debouncer is not None
        assert isinstance(debouncer, Debouncer)

    def test_get_debouncer_returns_same(self):
        """Test get_debouncer returns same instance for same key."""
        manager = DebouncerManager()

        debouncer1 = manager.get_debouncer("entity1_brightness")
        debouncer2 = manager.get_debouncer("entity1_brightness")

        assert debouncer1 is debouncer2

    def test_get_debouncer_different_keys(self):
        """Test get_debouncer returns different instances for different keys."""
        manager = DebouncerManager()

        debouncer1 = manager.get_debouncer("entity1_brightness")
        debouncer2 = manager.get_debouncer("entity2_brightness")

        assert debouncer1 is not debouncer2

    def test_manager_custom_delay(self):
        """Test manager passes custom delay to debouncers."""
        manager = DebouncerManager(delay=2.0)

        debouncer = manager.get_debouncer("test")

        assert debouncer._delay == 2.0

    @pytest.mark.asyncio
    async def test_cancel_all(self):
        """Test cancel_all cancels all pending calls."""
        manager = DebouncerManager(delay=0.1)
        mock_func1 = AsyncMock()
        mock_func2 = AsyncMock()

        debouncer1 = manager.get_debouncer("key1")
        debouncer2 = manager.get_debouncer("key2")

        await debouncer1.async_call(mock_func1)
        await debouncer2.async_call(mock_func2)

        manager.cancel_all()

        # Wait for what would have been the delay
        await asyncio.sleep(0.15)

        # Neither should be called
        mock_func1.assert_not_called()
        mock_func2.assert_not_called()

        # Debouncers should be cleared
        assert len(manager._debouncers) == 0

    def test_cancel_all_empty(self):
        """Test cancel_all with no debouncers."""
        manager = DebouncerManager()
        # Should not raise
        manager.cancel_all()


class TestDefaultDebounceDelay:
    """Tests for default debounce delay constant."""

    def test_default_delay_value(self):
        """Test default delay is 0.5 seconds."""
        assert DEFAULT_DEBOUNCE_DELAY == 0.5
