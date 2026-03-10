"""Tests for the coordinator entity protocol."""

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


def _entity_signature(entity: LiproEntityProtocol) -> tuple[str | None, str, int]:
    """Consume the protocol exactly how coordinator helpers do."""
    return (entity.unique_id, entity.device.serial, len(entity.get_protected_keys()))


def test_lipro_entity_protocol_exposes_required_members() -> None:
    """Protocol class should define the minimal debounce-protection surface."""
    assert hasattr(LiproEntityProtocol, "unique_id")
    assert hasattr(LiproEntityProtocol, "device")
    assert hasattr(LiproEntityProtocol, "get_protected_keys")


def test_lipro_entity_protocol_accepts_structural_implementations() -> None:
    """Any object with the required members should work as a protocol entity."""
    entity = _MockEntity(unique_id="entity_123", protected_keys={"brightness", "color_temp"})

    assert _entity_signature(entity) == (
        "entity_123",
        "03ab5ccd7caaaaaa",
        2,
    )


def test_lipro_entity_protocol_allows_none_unique_id_and_empty_keys() -> None:
    """Coordinator protocol should tolerate optional ids and no protected keys."""
    entity = _MockEntity(unique_id=None, protected_keys=set())

    assert _entity_signature(entity) == (None, "03ab5ccd7caaaaaa", 0)


def test_incomplete_entity_is_missing_protocol_members() -> None:
    """Objects lacking the required members should stay obviously incomplete."""

    class IncompleteEntity:
        @property
        def unique_id(self) -> str:
            return "incomplete"

    entity = IncompleteEntity()

    assert hasattr(entity, "unique_id")
    assert not hasattr(entity, "device")
    assert not hasattr(entity, "get_protected_keys")
