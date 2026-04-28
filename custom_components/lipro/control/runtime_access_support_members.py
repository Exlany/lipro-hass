"""Support-only explicit-member helpers for runtime access."""

from __future__ import annotations

from collections.abc import Mapping
from inspect import getattr_static
from typing import cast

_MISSING = object()


def _get_static_member(obj: object | None, name: str) -> object:
    """Return one statically declared member without triggering dynamic fallback."""
    if obj is None:
        return _MISSING
    try:
        return getattr_static(obj, name)
    except AttributeError:
        return _MISSING


def _get_explicit_member(obj: object | None, name: str) -> object | None:
    """Return one explicitly declared instance/class member without mock-ghost probing."""
    if _get_static_member(obj, name) is _MISSING:
        return None
    try:
        return cast(object | None, getattr(obj, name))
    except AttributeError:
        return None


def _has_explicit_runtime_member(obj: object | None, name: str) -> bool:
    """Return whether a runtime-facing attribute is explicitly bound on the object."""
    return _get_static_member(obj, name) is not _MISSING


def _get_explicit_bool_member(obj: object | None, name: str) -> bool | None:
    """Return one explicit bool member when present and correctly typed."""
    value = _get_explicit_member(obj, name)
    return value if isinstance(value, bool) else None


def _get_explicit_mapping_member(
    obj: object | None,
    name: str,
) -> Mapping[str, object] | None:
    """Return one explicit mapping member when present and correctly typed."""
    value = _get_explicit_member(obj, name)
    return value if isinstance(value, Mapping) else None
