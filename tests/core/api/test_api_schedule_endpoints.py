"""Tests for schedule endpoint mixin helpers."""

from __future__ import annotations

import pytest

from custom_components.lipro.core.api.endpoints.schedule import (
    _ClientScheduleEndpointsMixin,
)
from custom_components.lipro.core.api.errors import LiproApiError


class _DummyClient(_ClientScheduleEndpointsMixin):
    pass


def test_resolve_ble_schedule_candidate_ids_invalid_device_id_returns_empty() -> None:
    client = _DummyClient()

    assert client._resolve_ble_schedule_candidate_ids(device_id="not-an-iot-id") == []


def test_require_mesh_schedule_candidate_ids_returns_gateway_then_members() -> None:
    client = _DummyClient()

    result = client._require_mesh_schedule_candidate_ids(
        device_id="mesh_group_49155",
        mesh_gateway_id="03ab0000000000a1",
        mesh_member_ids=["03ab0000000000a2", "bad-id", "03ab0000000000a3"],
    )

    assert result == ["03ab0000000000a1", "03ab0000000000a2", "03ab0000000000a3"]


def test_require_mesh_schedule_candidate_ids_raises_when_no_candidates() -> None:
    client = _DummyClient()

    with pytest.raises(LiproApiError, match="Mesh schedule candidate IoT IDs unavailable"):
        client._require_mesh_schedule_candidate_ids(device_id="mesh_group_49155")
