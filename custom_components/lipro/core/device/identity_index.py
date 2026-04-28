"""Device identity index with normalized lookup behavior."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from .device import LiproDevice


def iter_identity_aliases(device_id: Any) -> tuple[str, ...]:
    """Return normalized identifier aliases used by device lookup indexes."""
    if not isinstance(device_id, str):
        return ()
    normalized = device_id.strip()
    if not normalized:
        return ()
    lowered = normalized.lower()
    if lowered == normalized:
        return (normalized,)
    return (normalized, lowered)


def register_identity_alias(
    mapping: dict[str, LiproDevice],
    device_id: Any,
    device: LiproDevice,
) -> None:
    """Register one identifier and its lowercase alias into a mapping."""
    for key in iter_identity_aliases(device_id):
        mapping[key] = device


class DeviceIdentityIndex:
    """Mutable identity index for case-insensitive device lookups."""

    def __init__(self, mapping: Mapping[str, LiproDevice] | None = None) -> None:
        """Initialize index and optionally seed with an existing mapping."""
        self._mapping: dict[str, LiproDevice] = {}
        if mapping is not None:
            self.replace(mapping)

    @property
    def mapping(self) -> Mapping[str, LiproDevice]:
        """Return a read-only view of the identity mapping."""
        return MappingProxyType(self._mapping)

    def get(self, device_id: Any) -> LiproDevice | None:
        """Get device by any known identifier after normalization."""
        if not isinstance(device_id, str):
            return None

        for key in iter_identity_aliases(device_id):
            device = self._mapping.get(key)
            if device is not None:
                return device
        return None

    def register(self, device_id: Any, device: LiproDevice) -> None:
        """Register one lookup identifier with case-insensitive aliases."""
        register_identity_alias(self._mapping, device_id, device)

    def unregister(self, device_id: Any, *, device: LiproDevice | None = None) -> None:
        """Unregister one identifier and its lowercase alias.

        When ``device`` is provided, only remove entries currently mapped to
        that device to avoid deleting IDs owned by other devices.
        """
        for key in iter_identity_aliases(device_id):
            existing = self._mapping.get(key)
            if existing is None:
                continue
            if device is not None and existing is not device:
                continue
            self._mapping.pop(key, None)

    def replace(self, mapping: Mapping[str, LiproDevice]) -> None:
        """Atomically replace current mapping with a normalized mapping copy."""
        updated: dict[str, LiproDevice] = {}
        for device_id, device in mapping.items():
            register_identity_alias(updated, device_id, device)
        self._mapping = updated

    def clear(self) -> None:
        """Clear all registered identity aliases."""
        self._mapping.clear()
