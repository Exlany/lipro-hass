"""Tests for device lookup service helpers."""

from __future__ import annotations

import re

import pytest

from custom_components.lipro.services.device_lookup import (
    _normalize_entity_ids,
    extract_device_id_from_entity_ids,
    resolve_device_id_from_service_call,
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
    entity_ids: list[object] = [" light.demo ", 123, "", "   ", None, "switch.demo"]

    result = _normalize_entity_ids(entity_ids)

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


def test_resolve_device_id_from_service_call_prefers_explicit_device_id(hass) -> None:
    """An explicit device_id should win before entity-target resolution."""
    resolved = resolve_device_id_from_service_call(
        hass,
        service_call(hass, {"device_id": " 03ab0000000000a1 "}),
        domain="lipro",
        serial_pattern=_SERIAL_PATTERN,
        attr_device_id="device_id",
    )

    assert resolved == "03ab0000000000a1"


def test_resolve_device_id_from_service_call_reads_target_entity_ids(hass) -> None:
    """ServiceCall.target.entity_id should feed the service-facing resolver."""
    entity_id = (
        er.async_get(hass)
        .async_get_or_create(
            "light",
            "lipro",
            "lipro_03ab0000000000a1_light",
            suggested_object_id="lookup_target_lipro",
        )
        .entity_id
    )

    resolved = resolve_device_id_from_service_call(
        hass,
        service_call(hass, {}, target_entity_ids=[entity_id]),
        domain="lipro",
        serial_pattern=_SERIAL_PATTERN,
        attr_device_id="device_id",
    )

    assert resolved == "03ab0000000000a1"


def test_resolve_device_id_from_service_call_raises_when_missing_targets(hass) -> None:
    """The service-facing resolver should still reject empty targets."""
    with pytest.raises(ServiceValidationError) as exc_info:
        resolve_device_id_from_service_call(
            hass,
            service_call(hass, {}),
            domain="lipro",
            serial_pattern=_SERIAL_PATTERN,
            attr_device_id="device_id",
        )

    assert exc_info.value.translation_key == "no_device_specified"
