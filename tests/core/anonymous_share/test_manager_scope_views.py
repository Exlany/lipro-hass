"""Focused tests for anonymous-share scope-view orchestration helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from custom_components.lipro.core.anonymous_share.manager_scope import (
    AnonymousShareScopeViews,
)
from custom_components.lipro.core.anonymous_share.manager_support import _ScopeState

if TYPE_CHECKING:
    from custom_components.lipro.core.anonymous_share.manager import (
        AnonymousShareManager,
    )


@dataclass(slots=True)
class _FakeManager:
    scope_key: str


def _build_views(
    registry: dict[str, _ScopeState],
) -> AnonymousShareScopeViews:
    return AnonymousShareScopeViews(
        registry=registry,
        manager_factory=lambda scope_key: cast("AnonymousShareManager", _FakeManager(scope_key)),
    )


def test_for_scope_caches_manager_instances() -> None:
    views = _build_views({})

    first = cast(_FakeManager, views.for_scope("entry-1"))
    second = cast(_FakeManager, views.for_scope("entry-1"))
    third = cast(_FakeManager, views.for_scope("entry-2"))

    assert first is second
    assert first.scope_key == "entry-1"
    assert third.scope_key == "entry-2"


def test_primary_manager_prefers_enabled_scope() -> None:
    registry = {
        "__default__": _ScopeState(),
        "entry-2": _ScopeState(),
    }
    registry["entry-2"].collector.set_enabled(True, error_reporting=True)
    views = _build_views(registry)

    primary = cast(_FakeManager, views.primary_manager(default_scope="__default__"))

    assert primary.scope_key == "entry-2"


def test_aggregate_pending_count_sums_scoped_errors() -> None:
    registry = {
        "__default__": _ScopeState(),
        "entry-2": _ScopeState(),
    }
    registry["__default__"].collector.set_enabled(True, error_reporting=True)
    registry["entry-2"].collector.set_enabled(True, error_reporting=True)
    registry["__default__"].collector.record_api_error("/api/one", 500, "boom")
    registry["entry-2"].collector.record_api_error("/api/two", 400, "bad")
    views = _build_views(registry)

    assert views.aggregate_enabled() is True
    assert views.aggregate_pending_count() == (0, 2)

