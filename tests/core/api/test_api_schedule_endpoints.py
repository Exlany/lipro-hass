"""Tests for schedule endpoint helper methods."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.lipro.core.api.endpoints.schedule import ScheduleEndpoints
from custom_components.lipro.core.api.errors import LiproApiError


def _make_endpoint() -> ScheduleEndpoints:
    client = MagicMock()
    client.to_device_type_hex.side_effect = str
    return ScheduleEndpoints(client)


def test_resolve_ble_schedule_candidate_ids_invalid_device_id_returns_empty() -> None:
    client = _make_endpoint()

    assert client._resolve_ble_schedule_candidate_ids(device_id="not-an-iot-id") == []


def test_require_mesh_schedule_candidate_ids_returns_gateway_then_members() -> None:
    client = _make_endpoint()

    result = client._require_mesh_schedule_candidate_ids(
        device_id="mesh_group_49155",
        mesh_gateway_id="03ab0000000000a1",
        mesh_member_ids=["03ab0000000000a2", "bad-id", "03ab0000000000a3"],
    )

    assert result == ["03ab0000000000a1", "03ab0000000000a2", "03ab0000000000a3"]


def test_require_mesh_schedule_candidate_ids_raises_when_no_candidates() -> None:
    client = _make_endpoint()

    with pytest.raises(
        LiproApiError, match="Mesh schedule candidate IoT IDs unavailable"
    ):
        client._require_mesh_schedule_candidate_ids(device_id="mesh_group_49155")


def test_resolve_ble_schedule_candidate_ids_non_mesh_returns_normalized_id() -> None:
    client = _make_endpoint()

    assert client._resolve_ble_schedule_candidate_ids(device_id="03ab5ccd7caaaaaa") == [
        "03ab5ccd7caaaaaa"
    ]
