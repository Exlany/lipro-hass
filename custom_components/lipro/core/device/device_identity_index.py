"""Device identity index with coordinator-compatible lookup behavior."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from . import LiproDevice


class DeviceIdentityIndex:
    """Mutable identity index for case-insensitive device lookups."""

    _MAX_DIRECT_MUTATION_SCAN: int = 2048

    def __init__(self, mapping: Mapping[str, LiproDevice] | None = None) -> None:
        """Initialize index and optionally seed with an existing mapping."""
        self._mapping: dict[str, LiproDevice] = {}
        if mapping is not None:
            self.replace(mapping)

    @property
    def mapping(self) -> dict[str, LiproDevice]:
        """Return the underlying mutable mapping."""
        return self._mapping

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

        # Compatibility: callers may mutate `mapping` directly without using register().
        # Guard against turning a bad lookup into O(n) on pathological mappings.
        if len(self._mapping) > self._MAX_DIRECT_MUTATION_SCAN:
            return None
        for known_id, known_device in self._mapping.items():
            if known_id.strip().lower() != normalized_lower:
                continue
            self._register_into(self._mapping, normalized, known_device)
            return known_device
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
