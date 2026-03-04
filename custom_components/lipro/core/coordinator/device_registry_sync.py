"""Device-registry sync helpers used by coordinator refresh workflows."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
import logging
from typing import Any

from homeassistant.helpers import area_registry as ar, device_registry as dr

from ..device.device import LiproDevice


def _iter_domain_identifiers(
    identifiers: Iterable[tuple[str, object]],
    *,
    domain: str,
) -> Iterable[str]:
    """Yield normalized identifier values for one integration domain."""
    for identifier_domain, identifier_value in identifiers:
        if identifier_domain != domain:
            continue
        if not isinstance(identifier_value, str):
            continue
        normalized = identifier_value.strip()
        if normalized:
            yield normalized


def collect_registry_serials_for_entry(
    *,
    device_registry: dr.DeviceRegistry,
    config_entry_id: str,
    domain: str,
) -> set[str]:
    """Collect existing serial identifiers from HA device registry."""
    serials: set[str] = set()
    try:
        entries = dr.async_entries_for_config_entry(device_registry, config_entry_id)
    except Exception:  # noqa: BLE001 # pragma: no cover - defensive fallback.
        return serials

    for entry in entries:
        serials.update(
            _iter_domain_identifiers(
                getattr(entry, "identifiers", set()),
                domain=domain,
            )
        )
    return serials


def sync_device_room_assignments(
    *,
    devices: Mapping[str, LiproDevice],
    previous_devices: Mapping[str, LiproDevice],
    room_area_sync_force: bool,
    domain: str,
    device_registry: dr.DeviceRegistry,
    area_registry: ar.AreaRegistry,
    normalize_room_name: Callable[[str | None], str | None],
    resolve_room_area_target_name: Callable[..., tuple[bool, str | None]],
    logger: logging.Logger,
) -> None:
    """Sync cloud room changes into HA device-registry area assignments."""
    area_id_cache: dict[str, str] = {}

    def _get_area_id(room_name: str) -> str:
        cached = area_id_cache.get(room_name)
        if cached is not None:
            return cached
        area_id = area_registry.async_get_or_create(room_name).id
        area_id_cache[room_name] = area_id
        return area_id

    for serial, device in devices.items():
        previous = previous_devices.get(serial)
        if previous is None:
            continue

        old_room_name = normalize_room_name(previous.room_name)
        new_room_name = normalize_room_name(device.room_name)
        room_changed = old_room_name != new_room_name

        device_entry = device_registry.async_get_device(identifiers={(domain, serial)})
        if device_entry is None:
            continue

        current_area_id = device_entry.area_id
        current_area_name: str | None = None
        if current_area_id is not None:
            current_area = area_registry.async_get_area(current_area_id)
            if current_area is not None:
                current_area_name = normalize_room_name(current_area.name)

        if not room_changed and not room_area_sync_force:
            continue
        if (
            room_area_sync_force
            and not room_changed
            and current_area_name == new_room_name
        ):
            # Force mode is intended to converge divergent cloud-vs-user mappings.
            # Skip no-op writes when already aligned.
            continue

        update_kwargs: dict[str, Any] = {"suggested_area": new_room_name}
        update_area, target_area_name = resolve_room_area_target_name(
            room_area_sync_force=room_area_sync_force,
            old_room_name=old_room_name,
            new_room_name=new_room_name,
            current_area_id=current_area_id,
            current_area_name=current_area_name,
        )
        if update_area:
            if target_area_name is None:
                update_kwargs["area_id"] = None
            else:
                update_kwargs["area_id"] = _get_area_id(target_area_name)

        device_registry.async_update_device(device_entry.id, **update_kwargs)
        logger.debug(
            "Synced room mapping for %s: %s -> %s (area_updated=%s)",
            serial,
            old_room_name,
            new_room_name,
            "area_id" in update_kwargs,
        )


def remove_stale_registry_devices(
    *,
    stale_serials: set[str],
    domain: str,
    device_registry: dr.DeviceRegistry,
    logger: logging.Logger,
) -> None:
    """Remove stale serials from HA device registry when entries exist."""
    for serial in stale_serials:
        device_entry = device_registry.async_get_device(identifiers={(domain, serial)})
        if device_entry is None:
            continue
        logger.info(
            "Removing stale device: %s (serial: %s)",
            device_entry.name,
            serial,
        )
        device_registry.async_remove_device(device_entry.id)
