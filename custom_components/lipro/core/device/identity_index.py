"""Device identity index with coordinator-compatible lookup behavior."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from .device import LiproDevice


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
        """Get device by any known identifier with strip/lower compatibility."""
        if not isinstance(device_id, str):
            return None

        normalized = device_id.strip()
        if not normalized:
            return None

        device = self._mapping.get(normalized)
        if device is not None:
            return device

        normalized_lower = normalized.lower()
        device = self._mapping.get(normalized_lower)
        if device is not None:
            return device

        return None

    def register(self, device_id: Any, device: LiproDevice) -> None:
        """Register one lookup identifier with case-insensitive aliases."""
        self._register_into(self._mapping, device_id, device)

    def unregister(self, device_id: Any, *, device: LiproDevice | None = None) -> None:
        """Unregister one identifier and its lowercase alias.

        When ``device`` is provided, only remove entries currently mapped to
        that device to avoid deleting IDs owned by other devices.
        """
        for key in self._iter_aliases(device_id):
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
            self._register_into(updated, device_id, device)
        self._mapping = updated

    def clear(self) -> None:
        """Clear all registered identity aliases."""
        self._mapping.clear()

    @staticmethod
    def _iter_aliases(device_id: Any) -> tuple[str, ...]:
        """Return normalized identifier aliases used by the index."""
        if not isinstance(device_id, str):
            return ()
        normalized = device_id.strip()
        if not normalized:
            return ()
        lowered = normalized.lower()
        if lowered == normalized:
            return (normalized,)
        return (normalized, lowered)

    @staticmethod
    def _register_into(
        mapping: dict[str, LiproDevice],
        device_id: Any,
        device: LiproDevice,
    ) -> None:
        """Register ID and lowercase alias into the target mapping."""
        for key in DeviceIdentityIndex._iter_aliases(device_id):
            mapping[key] = device
