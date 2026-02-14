"""Tests for Lipro helper utilities."""

from __future__ import annotations

from custom_components.lipro.helpers.platform import create_platform_entities


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
