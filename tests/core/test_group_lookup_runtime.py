"""Tests for group lookup runtime decision helpers."""

from __future__ import annotations

from custom_components.lipro.core.coordinator.runtime.group_lookup_runtime import (
    compute_group_lookup_mapping_decision,
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


def test_compute_group_lookup_mapping_decision_tracks_gateway_and_member_changes() -> (
    None
):
    decision = compute_group_lookup_mapping_decision(
        previous_gateway_id=" GW_OLD ",
        current_gateway_id="gw_new",
        previous_member_lookup_ids=["M1", "M2"],
        current_member_lookup_ids=[" m2 ", "M3"],
        member_ids=["device-1", "device-2"],
    )

    assert decision.gateway_unregister_id == " GW_OLD "
    assert decision.gateway_register_id == "gw_new"
    assert decision.gateway_extra_data_value == "gw_new"
    assert decision.member_unregister_ids == ["M1"]
    assert decision.member_register_ids == ["m2", "M3"]
    assert decision.member_lookup_ids_extra_data == ["m2", "M3"]
    assert decision.member_ids_extra_data == ["device-1", "device-2"]
    assert decision.member_count == 2


def test_compute_group_lookup_mapping_decision_ignores_equivalent_gateway_ids() -> None:
    decision = compute_group_lookup_mapping_decision(
        previous_gateway_id=" GW_001 ",
        current_gateway_id="gw_001",
        previous_member_lookup_ids=None,
        current_member_lookup_ids="invalid",
        member_ids=[],
    )

    assert decision.gateway_unregister_id is None
    assert decision.gateway_register_id == "gw_001"
    assert decision.gateway_extra_data_value == "gw_001"
    assert decision.member_unregister_ids == []
    assert decision.member_register_ids == []
    assert decision.member_lookup_ids_extra_data == []
    assert decision.member_count == 0
