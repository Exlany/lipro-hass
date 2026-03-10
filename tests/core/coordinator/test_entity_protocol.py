"""Behavior-focused tests for the coordinator entity protocol."""

from __future__ import annotations

from custom_components.lipro.core.coordinator.entity_protocol import LiproEntityProtocol
from custom_components.lipro.core.device import LiproDevice


class _MockEntity:
    """Simple runtime implementation of ``LiproEntityProtocol``."""

    def __init__(self, *, unique_id: str | None, protected_keys: set[str]) -> None:
        self._unique_id = unique_id
        self._protected_keys = protected_keys
        self._device = LiproDevice(
            device_number=123,
            serial="03ab5ccd7caaaaaa",
            name="Desk Light",
            device_type=1,
            iot_name="lipro_led",
            physical_model="light",
        )

    @property
    def unique_id(self) -> str | None:
        return self._unique_id

    @property
    def device(self) -> LiproDevice:
        return self._device

    def get_protected_keys(self) -> set[str]:
        return self._protected_keys


def _collect_entity_snapshot(entity: LiproEntityProtocol) -> dict[str, object]:
    """Consume the public protocol surface used by coordinator flows."""
    return {
        "unique_id": entity.unique_id,
        "serial": entity.device.serial,
        "protected_keys": entity.get_protected_keys(),
    }


def test_entity_protocol_supports_debounce_protection_behavior() -> None:
    """Coordinator consumers should read ids, devices, and protected keys uniformly."""
    entity = _MockEntity(
        unique_id="entity_123",
        protected_keys={"brightness", "color_temp"},
    )

    assert _collect_entity_snapshot(entity) == {
        "unique_id": "entity_123",
        "serial": "03ab5ccd7caaaaaa",
        "protected_keys": {"brightness", "color_temp"},
    }


def test_entity_protocol_tolerates_optional_ids_and_empty_protection() -> None:
    """Public protocol consumers should handle optional ids and no protected keys."""
    entity = _MockEntity(unique_id=None, protected_keys=set())

    assert _collect_entity_snapshot(entity) == {
        "unique_id": None,
        "serial": "03ab5ccd7caaaaaa",
        "protected_keys": set(),
    }
