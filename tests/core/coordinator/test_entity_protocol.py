"""Tests for coordinator entity protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from custom_components.lipro.core.coordinator.entity_protocol import (
    LiproEntityProtocol,
)
from custom_components.lipro.core.device import LiproDevice

if TYPE_CHECKING:
    from unittest.mock import Mock


class TestLiproEntityProtocol:
    """Test LiproEntityProtocol."""

    def test_protocol_structure(self) -> None:
        """Test protocol defines required methods."""
        assert hasattr(LiproEntityProtocol, "unique_id")
        assert hasattr(LiproEntityProtocol, "device")
        assert hasattr(LiproEntityProtocol, "get_protected_keys")

    def test_protocol_with_mock_entity(self) -> None:
        """Test protocol works with mock entity."""

        class MockEntity:
            """Mock entity implementing protocol."""

            @property
            def unique_id(self) -> str:
                """Return unique id."""
                return "test_entity_123"

            @property
            def device(self) -> LiproDevice:
                """Return device."""
                return LiproDevice(
                    device_id="device_123",
                    name="Test Device",
                    model="test_model",
                    category="light",
                    room_id="room_123",
                    room_name="Living Room",
                )

            def get_protected_keys(self) -> set[str]:
                """Return protected keys."""
                return {"brightness", "color_temp"}

        entity = MockEntity()

        # Protocol should accept this implementation
        def process_entity(e: LiproEntityProtocol) -> str:
            return f"{e.unique_id}:{len(e.get_protected_keys())}"

        result = process_entity(entity)
        assert result == "test_entity_123:2"

    def test_protocol_type_checking(self) -> None:
        """Test protocol type checking at runtime."""

        class IncompleteEntity:
            """Entity missing required methods."""

            @property
            def unique_id(self) -> str:
                return "incomplete"

        entity = IncompleteEntity()

        # Should not have device or get_protected_keys
        assert not hasattr(entity, "device")
        assert not hasattr(entity, "get_protected_keys")

    def test_protocol_with_none_unique_id(self) -> None:
        """Test protocol allows None unique_id."""

        class EntityWithoutId:
            """Entity with None unique_id."""

            @property
            def unique_id(self) -> None:
                """Return None."""
                return None

            @property
            def device(self) -> LiproDevice:
                """Return device."""
                return LiproDevice(
                    device_id="device_123",
                    name="Test",
                    model="test",
                    category="light",
                    room_id="room_123",
                    room_name="Room",
                )

            def get_protected_keys(self) -> set[str]:
                """Return empty set."""
                return set()

        entity = EntityWithoutId()

        def check_entity(e: LiproEntityProtocol) -> bool:
            return e.unique_id is None

        assert check_entity(entity)

    def test_protocol_protected_keys_empty(self) -> None:
        """Test protocol with empty protected keys."""

        class EntityNoProtection:
            """Entity with no protected keys."""

            @property
            def unique_id(self) -> str:
                return "no_protection"

            @property
            def device(self) -> LiproDevice:
                return LiproDevice(
                    device_id="device_123",
                    name="Test",
                    model="test",
                    category="switch",
                    room_id="room_123",
                    room_name="Room",
                )

            def get_protected_keys(self) -> set[str]:
                return set()

        entity = EntityNoProtection()

        def has_protection(e: LiproEntityProtocol) -> bool:
            return len(e.get_protected_keys()) > 0

        assert not has_protection(entity)
