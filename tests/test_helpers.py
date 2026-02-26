"""Tests for Lipro helper utilities."""

from __future__ import annotations

from custom_components.lipro.helpers.platform import (
    create_device_entities,
    create_platform_entities,
)


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


class TestCreateDeviceEntities:
    """Tests for create_device_entities helper."""

    def test_builds_multiple_entities_per_device(self, make_device, mock_coordinator):
        """Builder can return multiple entities and they are flattened."""
        light = make_device("light", serial="03ab5ccd7cxxxxxx")
        switch = make_device("switch", serial="03ab5ccd7cyyyyyy")
        mock_coordinator.devices = {
            light.serial: light,
            switch.serial: switch,
        }

        entities = create_device_entities(
            mock_coordinator,
            entity_builder=lambda c, d: (
                [f"{d.serial}_1", f"{d.serial}_2"] if d.is_light else []
            ),
        )

        assert entities == [f"{light.serial}_1", f"{light.serial}_2"]

    def test_applies_optional_device_filter(self, make_device, mock_coordinator):
        """Filter should be applied before invoking builder."""
        light = make_device("light", serial="03ab5ccd7cxxxxxx")
        switch = make_device("switch", serial="03ab5ccd7cyyyyyy")
        mock_coordinator.devices = {
            light.serial: light,
            switch.serial: switch,
        }
        built_for: list[str] = []

        def _builder(c, d):
            built_for.append(d.serial)
            return [d.serial]

        entities = create_device_entities(
            mock_coordinator,
            entity_builder=_builder,
            device_filter=lambda d: d.is_light,
        )

        assert built_for == [light.serial]
        assert entities == [light.serial]
