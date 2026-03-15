"""Device/coordinator lookup helpers for Lipro services."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from re import Pattern
from typing import Protocol, runtime_checkable

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er

from ..control.runtime_access import get_entry_runtime_coordinator, iter_runtime_entries
from ..core.device import LiproDevice
from ..runtime_types import LiproCoordinator


@runtime_checkable
class _ServiceTargetLike(Protocol):
    """Service-call target payload surface used for entity resolution."""

    entity_id: str | Iterable[str] | None


class DeviceLookupCoordinator(Protocol):
    """Coordinator surface required for device lookup."""

    def get_device(self, device_id: str) -> LiproDevice | None:
        """Resolve one device by serial."""

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Resolve one device by alternate identifier."""


EntityIdCollection = str | Iterable[object] | None


def _normalize_entity_ids(entity_ids: EntityIdCollection) -> list[str]:
    """Normalize entity_id inputs into a clean list of entity_id strings."""
    if isinstance(entity_ids, str):
        raw_ids: Iterable[object] = [entity_ids]
    elif isinstance(entity_ids, Iterable):
        raw_ids = entity_ids
    else:
        raw_ids = ()

    normalized: list[str] = []
    for entity_id in raw_ids:
        if not isinstance(entity_id, str):
            continue
        stripped = entity_id.strip()
        if stripped:
            normalized.append(stripped)
    return normalized


def extract_device_id_from_entity_ids(
    hass: HomeAssistant,
    entity_ids: Iterable[str],
    *,
    serial_pattern: Pattern[str],
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
            matched_serials.add(match.group(1))

    if len(matched_serials) == 1:
        return next(iter(matched_serials))
    return None


def _collect_target_entity_ids(call: ServiceCall) -> list[str]:
    """Collect entity ids from service data and HA target payload."""
    entity_ids = _normalize_entity_ids(call.data.get(ATTR_ENTITY_ID))
    target = getattr(call, "target", None)
    if isinstance(target, _ServiceTargetLike):
        for entity_id in _normalize_entity_ids(target.entity_id):
            if entity_id not in entity_ids:
                entity_ids.append(entity_id)
    return entity_ids


def resolve_device_id_from_service_call(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    domain: str,
    serial_pattern: Pattern[str],
    attr_device_id: str,
) -> str:
    """Resolve device identifier from service data or targeted entities."""
    device_id = call.data.get(attr_device_id)
    if isinstance(device_id, str):
        normalized = device_id.strip()
        if normalized:
            return normalized

    entity_ids = _collect_target_entity_ids(call)
    if not entity_ids:
        raise ServiceValidationError(
            translation_domain=domain,
            translation_key="no_device_specified",
        )

    resolved_device_id = extract_device_id_from_entity_ids(
        hass,
        entity_ids,
        serial_pattern=serial_pattern,
    )
    if not resolved_device_id:
        raise ServiceValidationError(
            translation_domain=domain,
            translation_key="cannot_determine_device",
        )

    return resolved_device_id


def find_device_in_coordinator(
    coordinator: DeviceLookupCoordinator,
    device_id: str,
) -> LiproDevice | None:
    """Find device by serial first, then by alias mapping."""
    device = coordinator.get_device(device_id)
    if device is None:
        return coordinator.get_device_by_id(device_id)
    return device


def iter_runtime_coordinators(
    hass: HomeAssistant,
    *,
    domain: str,
) -> Iterator[LiproCoordinator]:
    """Iterate all active coordinators for the Lipro domain."""
    del domain
    for entry in iter_runtime_entries(hass):
        coordinator = get_entry_runtime_coordinator(entry)
        if coordinator is not None:
            yield coordinator


async def get_device_and_coordinator(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    domain: str,
    serial_pattern: Pattern[str],
    attr_device_id: str,
) -> tuple[LiproDevice, LiproCoordinator]:
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
        if device is not None:
            return device, coordinator

    raise ServiceValidationError(
        translation_domain=domain,
        translation_key="device_not_found",
        translation_placeholders={"device_id": device_id},
    )
