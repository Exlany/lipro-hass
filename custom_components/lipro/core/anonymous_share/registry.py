"""Anonymous share manager registry and scope resolution helpers."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from ...domain_data import ensure_domain_data
from .manager import AnonymousShareManager

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_AGGREGATE_MANAGER_KEY = "anonymous_share_manager"
_SCOPED_MANAGERS_KEY = "anonymous_share_managers"


@lru_cache(maxsize=1)
def _get_root_manager() -> AnonymousShareManager:
    """Return the process-local aggregate manager shared outside HA scope."""
    return AnonymousShareManager(_aggregate=True)


def get_anonymous_share_manager(
    hass: HomeAssistant | None = None,
    *,
    entry_id: str | None = None,
) -> AnonymousShareManager:
    """Resolve the anonymous-share manager for the requested scope."""
    resolved_entry_id = entry_id
    root_manager = _get_root_manager()
    if hass is not None:
        domain_data = ensure_domain_data(hass)
        if domain_data is None:
            if resolved_entry_id is not None:
                return root_manager.for_scope(resolved_entry_id)
            return root_manager.aggregate_view()

        aggregate_manager = domain_data.get(_AGGREGATE_MANAGER_KEY)
        if not isinstance(aggregate_manager, AnonymousShareManager):
            aggregate_manager = root_manager.aggregate_view()
            domain_data[_AGGREGATE_MANAGER_KEY] = aggregate_manager
        if resolved_entry_id is None:
            return aggregate_manager

        scoped_managers = domain_data.get(_SCOPED_MANAGERS_KEY)
        if not isinstance(scoped_managers, dict):
            scoped_managers = {}
            domain_data[_SCOPED_MANAGERS_KEY] = scoped_managers

        manager = scoped_managers.get(resolved_entry_id)
        if not isinstance(manager, AnonymousShareManager):
            manager = root_manager.for_scope(resolved_entry_id)
            scoped_managers[resolved_entry_id] = manager
        return manager
    if resolved_entry_id is not None:
        return root_manager.for_scope(resolved_entry_id)
    return root_manager


__all__ = ["_get_root_manager", "get_anonymous_share_manager"]
