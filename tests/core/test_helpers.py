"""Tests for Lipro helper utilities."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock

from custom_components.lipro.helpers.platform import (
    add_entry_entities,
    build_device_entities_from_rules,
    create_device_entities,
    create_platform_entities,
)
from homeassistant.helpers.entity import Entity


def _make_entity(tag: str) -> Entity:
    entity = MagicMock(spec=Entity)
    entity.tag = tag
    return cast(Entity, entity)


class TestAddEntryEntities:
    """Tests for the thin platform adapter shell helper."""

    def test_projects_runtime_data_once(self, mock_coordinator):
        """Entry shell should only pass runtime_data into the entity builder."""
        entry = MagicMock(runtime_data=mock_coordinator)
        async_add_entities = MagicMock()
        entities = [_make_entity('first'), _make_entity('second')]

        add_entry_entities(
            entry,
            async_add_entities,
            entity_builder=lambda coordinator: entities if coordinator is mock_coordinator else [],
        )

        async_add_entities.assert_called_once_with(entities)


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
            device_filter=lambda d: d.capabilities.is_light,
            entity_factory=lambda c, d: _make_entity(f"entity_{d.serial}"),
        )

        assert [cast(Any, entity).tag for entity in entities] == [
            f"entity_{light.serial}"
        ]

    def test_empty_when_no_match(self, make_device, mock_coordinator):
        """Test empty list when no devices match filter."""
        switch = make_device("switch", serial="03ab5ccd7cyyyyyy")
        mock_coordinator.devices = {switch.serial: switch}

        entities = create_platform_entities(
            mock_coordinator,
            device_filter=lambda d: d.capabilities.is_curtain,
            entity_factory=lambda c, d: _make_entity(f"entity_{d.serial}"),
        )

        assert entities == []

    def test_empty_when_no_devices(self, mock_coordinator):
        """Test empty list when coordinator has no devices."""
        mock_coordinator.devices = {}

        entities = create_platform_entities(
            mock_coordinator,
            device_filter=lambda d: True,
            entity_factory=lambda c, d: _make_entity(f"entity_{d.serial}"),
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
            entity_factory=lambda c, d: _make_entity(d.serial),
        )

        assert [cast(Any, entity).tag for entity in entities] == [d1.serial, d2.serial]


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
                [
                    _make_entity(f"{d.serial}_1"),
                    _make_entity(f"{d.serial}_2"),
                ]
                if d.capabilities.is_light
                else []
            ),
        )

        assert [cast(Any, entity).tag for entity in entities] == [
            f"{light.serial}_1",
            f"{light.serial}_2",
        ]

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
            return [_make_entity(d.serial)]

        entities = create_device_entities(
            mock_coordinator,
            entity_builder=_builder,
            device_filter=lambda d: d.capabilities.is_light,
        )

        assert built_for == [light.serial]
        assert [cast(Any, entity).tag for entity in entities] == [light.serial]


class TestBuildDeviceEntitiesFromRules:
    """Tests for build_device_entities_from_rules helper."""

    def test_includes_always_entities(self, make_device, mock_coordinator):
        """Always factories should be created regardless of rules."""
        device = make_device("light", serial="03ab5ccd7cxxxxxx")

        entities = build_device_entities_from_rules(
            mock_coordinator,
            device,
            always_factories=(lambda c, d: _make_entity(f"{d.serial}_always"),),
            rules=(),
        )

        assert [cast(Any, entity).tag for entity in entities] == [
            f"{device.serial}_always"
        ]

    def test_applies_matching_rules_in_order(self, make_device, mock_coordinator):
        """Matching rules should append entities in declaration order."""
        device = make_device("light", serial="03ab5ccd7cxxxxxx")

        entities = build_device_entities_from_rules(
            mock_coordinator,
            device,
            rules=(
                (
                    lambda d: d.capabilities.is_light,
                    (
                        lambda c, d: _make_entity("first"),
                        lambda c, d: _make_entity("second"),
                    ),
                ),
                (lambda d: d.capabilities.is_switch, (lambda c, d: _make_entity("third"),)),
            ),
        )

        assert [cast(Any, entity).tag for entity in entities] == ["first", "second"]
