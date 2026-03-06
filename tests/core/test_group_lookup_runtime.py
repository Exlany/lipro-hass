"""Tests for group lookup runtime decision helpers."""

from __future__ import annotations

from custom_components.lipro.core.coordinator.runtime.group_lookup_runtime import (
    index_lookup_ids_by_normalized,
)


def test_index_lookup_ids_by_normalized_returns_empty_for_non_list() -> None:
    assert index_lookup_ids_by_normalized("not-a-list") == {}


def test_index_lookup_ids_by_normalized_skips_invalid_and_preserves_first_seen() -> (
    None
):
    indexed = index_lookup_ids_by_normalized(
        [
            "  GW_001  ",
            None,
            "   ",
            1,
            "gw_001",
            "GW_002",
        ]
    )

    assert indexed == {"gw_001": "GW_001", "gw_002": "GW_002"}
