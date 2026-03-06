"""Protocols used by coordinator to avoid HA/entity layer imports."""

from __future__ import annotations

from typing import Protocol

from ..device import LiproDevice


class LiproEntityProtocol(Protocol):
    """Minimal entity surface used by the coordinator for debounce protection."""

    @property
    def unique_id(self) -> str | None:
        """Return entity unique id."""

    @property
    def device(self) -> LiproDevice:
        """Return the device model associated with entity."""

    def get_protected_keys(self) -> set[str]:
        """Return property keys protected from coordinator overwrites."""
