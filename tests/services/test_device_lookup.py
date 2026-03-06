"""Tests for device lookup service helpers."""

from __future__ import annotations

import re
from unittest.mock import MagicMock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.services.device_lookup import (
    _normalize_entity_ids,
    extract_device_id_from_entity_ids,
    get_device_and_coordinator,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er
from tests.helpers.service_call import service_call

_SERIAL_PATTERN = re.compile(
    r"(03ab[0-9a-f]{12}|mesh_group_\d+)(?:_|$)",
    re.IGNORECASE,
)


def test_normalize_entity_ids_filters_non_string_values() -> None:
    """Normalization should skip non-string and blank entity ids."""
    result = _normalize_entity_ids(
        [" light.demo ", 123, "", "   ", None, "switch.demo"]
    )

    assert result == ["light.demo", "switch.demo"]


def test_extract_device_id_skips_missing_entry_and_non_lipro_unique_id(hass) -> None:
    """Entity lookup should skip unresolved entities and non-lipro unique_ids."""
    entity_registry = er.async_get(hass)
    non_lipro_entity_id = entity_registry.async_get_or_create(
        "light",
        "lipro",
        "other_03ab0000000000a1_light",
        suggested_object_id="lookup_non_lipro",
    ).entity_id
    valid_entity_id = entity_registry.async_get_or_create(
        "switch",
        "lipro",
        "lipro_03ab0000000000a1_switch",
        suggested_object_id="lookup_valid_lipro",
    ).entity_id

    result = extract_device_id_from_entity_ids(
        hass,
        ["light.missing_entity", non_lipro_entity_id, valid_entity_id],
        serial_pattern=_SERIAL_PATTERN,
    )

    assert result == "03ab0000000000a1"


@pytest.mark.asyncio
async def test_get_device_and_coordinator_raises_device_not_found(hass) -> None:
    """Raise a translated validation error when no coordinator owns the device."""
    entry = MockConfigEntry(domain="lipro", data={"phone": "13800000000"})
    entry.add_to_hass(hass)

    coordinator = MagicMock()
    coordinator.get_device.return_value = None
    coordinator.get_device_by_id.return_value = None
    entry.runtime_data = coordinator

    with pytest.raises(ServiceValidationError) as exc_info:
        await get_device_and_coordinator(
            hass,
            service_call(hass, {"device_id": "03ab0000000000a1"}),
            domain="lipro",
            serial_pattern=_SERIAL_PATTERN,
            attr_device_id="device_id",
        )

    assert exc_info.value.translation_key == "device_not_found"
