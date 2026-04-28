"""Scope-view orchestration helpers for anonymous-share manager homes."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .manager_support import (
    _ScopeState,
    aggregate_pending_count,
    get_scope_state,
    iter_scope_states,
    primary_scope_state,
)

if TYPE_CHECKING:
    from .manager import AnonymousShareManager


@dataclass(slots=True)
class AnonymousShareScopeViews:
    """Coordinate scoped/aggregate manager views over one shared state registry."""

    registry: dict[str, _ScopeState]
    manager_factory: Callable[[str], AnonymousShareManager]
    scoped_views: dict[str, AnonymousShareManager] = field(default_factory=dict)

    def for_scope(self, scope_key: str) -> AnonymousShareManager:
        """Return one cached manager bound to a scope key."""
        manager = self.scoped_views.get(scope_key)
        if manager is None:
            manager = self.manager_factory(scope_key)
            self.scoped_views[scope_key] = manager
        return manager

    def get_scope_state(self, scope_key: str) -> _ScopeState:
        """Return one scope state from the shared registry."""
        return get_scope_state(self.registry, scope_key)

    def iter_scope_states(self) -> list[tuple[str, _ScopeState]]:
        """Return a stable snapshot of all scope states."""
        return iter_scope_states(self.registry)

    def iter_scoped_managers(self) -> Sequence[AnonymousShareManager]:
        """Return managers for all known scopes."""
        return [self.for_scope(scope_key) for scope_key, _ in self.iter_scope_states()]

    def primary_scope_state(self) -> _ScopeState:
        """Return the preferred state for aggregate operations."""
        return primary_scope_state(self.registry)

    def primary_manager(self, *, default_scope: str) -> AnonymousShareManager:
        """Return the scoped manager matching the preferred aggregate state."""
        preferred = self.primary_scope_state()
        for scope_key, state in self.iter_scope_states():
            if state is preferred:
                return self.for_scope(scope_key)
        return self.for_scope(default_scope)

    def aggregate_enabled(self) -> bool:
        """Return whether any scope has anonymous share enabled."""
        return any(state.collector.is_enabled for _, state in self.iter_scope_states())

    def aggregate_pending_count(self) -> tuple[int, int]:
        """Return pending (devices, errors) counts across all scopes."""
        return aggregate_pending_count(self.registry)
