"""Device/coordinator lookup helpers for Lipro services."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er


def extract_device_id_from_entity_ids(
    hass: HomeAssistant,
    entity_ids: Any,
    *,
    serial_pattern: Any,
) -> str | None:
    """Resolve one Lipro device ID from entity targets.

    Returns None when no target can be resolved or targets are ambiguous.
    """
    ent_reg = er.async_get(hass)
    matched_serials: set[str] = set()
    for entity_id in entity_ids:
        entity_entry = ent_reg.async_get(entity_id)
        if not entity_entry or not entity_entry.unique_id:
            continue

        unique_id = entity_entry.unique_id
        if not unique_id.startswith("lipro_") or len(unique_id) <= 6:
            continue

        match = serial_pattern.match(unique_id[6:])
        if match:
            matched_serials.add(cast(str, match.group(1)))

    if len(matched_serials) == 1:
        return next(iter(matched_serials))
    return None


def resolve_device_id_from_service_call(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    domain: str,
    serial_pattern: Any,
    attr_device_id: str,
) -> Any:
    """Resolve device identifier from service data or targeted entities."""
    device_id = call.data.get(attr_device_id)
    if device_id:
        return device_id

    entity_ids = call.data.get(ATTR_ENTITY_ID, [])
    if isinstance(entity_ids, str):
        entity_ids = [entity_ids]

    if not entity_ids:
        raise ServiceValidationError(
            translation_domain=domain,
            translation_key="no_device_specified",
        )
    if len(entity_ids) != 1:
        raise ServiceValidationError(
            translation_domain=domain,
            translation_key="cannot_determine_device",
        )

    resolved_device_id = extract_device_id_from_entity_ids(
        hass, entity_ids, serial_pattern=serial_pattern
    )
    if not resolved_device_id:
        raise ServiceValidationError(
            translation_domain=domain,
            translation_key="cannot_determine_device",
        )

    return resolved_device_id


def find_device_in_coordinator(coordinator: Any, device_id: Any) -> Any:
    """Find device by serial first, then by alias mapping."""
    device = coordinator.get_device(device_id)
    if device is None:
        return coordinator.get_device_by_id(device_id)
    return device


def iter_runtime_coordinators(
    hass: HomeAssistant,
    *,
    domain: str,
) -> Iterator[Any]:
    """Iterate all active coordinators for the Lipro domain."""
    for entry in hass.config_entries.async_entries(domain):
        coordinator = entry.runtime_data
        if coordinator is None:
            continue
        yield coordinator


async def get_device_and_coordinator(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    domain: str,
    serial_pattern: Any,
    attr_device_id: str,
) -> tuple[Any, Any]:
    """Get device and coordinator from service call."""
    device_id = resolve_device_id_from_service_call(
        hass,
        call,
        domain=domain,
        serial_pattern=serial_pattern,
        attr_device_id=attr_device_id,
    )

    for coordinator in iter_runtime_coordinators(hass, domain=domain):
        device = find_device_in_coordinator(coordinator, device_id)
        if device:
            return device, coordinator

    raise ServiceValidationError(
        translation_domain=domain,
        translation_key="device_not_found",
        translation_placeholders={"device_id": device_id},
    )
