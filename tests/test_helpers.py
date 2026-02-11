"""Tests for Lipro helper utilities."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.helpers.debounce import Debouncer
from custom_components.lipro.helpers.platform import create_platform_entities


class TestDebouncer:
    """Tests for Debouncer class."""

    @pytest.mark.asyncio
    async def test_single_call_executes(self):
        """Test a single debounced call executes after delay."""
        func = AsyncMock()
        debouncer = Debouncer(delay=0.05)

        await debouncer.async_call(func, "arg1", key="val")
        # Wait for debounce delay + buffer
        await asyncio.sleep(0.1)

        func.assert_called_once_with("arg1", key="val")

    @pytest.mark.asyncio
    async def test_rapid_calls_only_last_executes(self):
        """Test rapid calls: only the last one executes."""
        func = AsyncMock()
        debouncer = Debouncer(delay=0.05)

        await debouncer.async_call(func, "first")
        await debouncer.async_call(func, "second")
        await debouncer.async_call(func, "third")
        await asyncio.sleep(0.1)

        func.assert_called_once_with("third")

    @pytest.mark.asyncio
    async def test_cancel_prevents_execution(self):
        """Test cancel prevents pending call from executing."""
        func = AsyncMock()
        debouncer = Debouncer(delay=0.05)

        await debouncer.async_call(func, "arg")
        debouncer.cancel()
        await asyncio.sleep(0.1)

        func.assert_not_called()

    @pytest.mark.asyncio
    async def test_cancel_when_no_pending(self):
        """Test cancel is safe when nothing is pending."""
        debouncer = Debouncer()
        debouncer.cancel()  # Should not raise

    @pytest.mark.asyncio
    async def test_error_in_func_does_not_propagate(self):
        """Test exception in debounced function is caught (logged, not raised)."""
        func = AsyncMock(side_effect=ValueError("boom"))
        debouncer = Debouncer(delay=0.05)

        await debouncer.async_call(func)
        await asyncio.sleep(0.1)

        func.assert_called_once()

    @pytest.mark.asyncio
    async def test_sequential_calls_after_delay(self):
        """Test two calls separated by more than delay both execute."""
        func = AsyncMock()
        debouncer = Debouncer(delay=0.05)

        await debouncer.async_call(func, "first")
        await asyncio.sleep(0.1)
        await debouncer.async_call(func, "second")
        await asyncio.sleep(0.1)

        assert func.call_count == 2
        func.assert_any_call("first")
        func.assert_any_call("second")


class TestCreatePlatformEntities:
    """Tests for create_platform_entities helper."""

    def test_filters_and_creates_entities(self, make_device, mock_coordinator):
        """Test entities are created only for matching devices."""
        light = make_device("light", serial="03ab5ccd7cxxxxxx")
        switch = make_device("switch", serial="03ab5ccd7cyyyyyy")
        mock_coordinator.devices = {
            light.serial: light,
            switch.serial: switch,
        }

        entities = create_platform_entities(
            mock_coordinator,
            device_filter=lambda d: d.is_light,
            entity_factory=lambda c, d: f"entity_{d.serial}",
        )

        assert entities == [f"entity_{light.serial}"]

    def test_empty_when_no_match(self, make_device, mock_coordinator):
        """Test empty list when no devices match filter."""
        switch = make_device("switch", serial="03ab5ccd7cyyyyyy")
        mock_coordinator.devices = {switch.serial: switch}

        entities = create_platform_entities(
            mock_coordinator,
            device_filter=lambda d: d.is_curtain,
            entity_factory=lambda c, d: f"entity_{d.serial}",
        )

        assert entities == []

    def test_empty_when_no_devices(self, mock_coordinator):
        """Test empty list when coordinator has no devices."""
        mock_coordinator.devices = {}

        entities = create_platform_entities(
            mock_coordinator,
            device_filter=lambda d: True,
            entity_factory=lambda c, d: f"entity_{d.serial}",
        )

        assert entities == []

    def test_all_devices_match(self, make_device, mock_coordinator):
        """Test all devices match when filter always returns True."""
        d1 = make_device("light", serial="03ab5ccd7cxxxxxx")
        d2 = make_device("switch", serial="03ab5ccd7cyyyyyy")
        mock_coordinator.devices = {d1.serial: d1, d2.serial: d2}

        entities = create_platform_entities(
            mock_coordinator,
            device_filter=lambda d: True,
            entity_factory=lambda c, d: d.serial,
        )

        assert len(entities) == 2
