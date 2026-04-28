"""Parsing helpers for Lipro device payloads."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..utils.property_normalization import normalize_properties


def parse_properties_list(properties_list: Sequence[object] | None) -> dict[str, Any]:
    """Parse properties list from API response."""
    if not properties_list:
        return {}
    result: dict[str, Any] = {}
    for prop in properties_list:
        if not isinstance(prop, Mapping):
            continue
        key = prop.get("key")
        if isinstance(key, str) and key:
            result[key] = prop.get("value")
    return normalize_properties(result)


__all__ = ["parse_properties_list"]
