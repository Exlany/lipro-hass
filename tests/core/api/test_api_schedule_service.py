"""Tests for schedule endpoint public behavior."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api.endpoints.schedule import ScheduleEndpoints
from custom_components.lipro.core.api.errors import LiproApiError


def _make_endpoint() -> ScheduleEndpoints:
    client = MagicMock()
    client.to_device_type_hex.side_effect = str
    return ScheduleEndpoints(client)


@pytest.mark.asyncio
async def test_schedule_endpoint_get_uses_mesh_candidates_for_mesh_groups() -> None:
    endpoint = cast(Any, _make_endpoint())
    endpoint._get_mesh_schedules_by_candidates = AsyncMock(return_value=[{"id": 7}])

    result = await endpoint.get_device_schedules(
        "mesh_group_49155",
        "ff000001",
        mesh_gateway_id="03ab0000000000a1",
    )

    assert result == [{"id": 7}]
    endpoint._get_mesh_schedules_by_candidates.assert_awaited_once_with(["03ab0000000000a1"])


@pytest.mark.asyncio
async def test_schedule_endpoint_add_uses_mesh_candidates_for_mesh_groups() -> None:
    endpoint = cast(Any, _make_endpoint())
    endpoint._add_mesh_schedule_by_candidates = AsyncMock(return_value=[{"id": 1}])

    result = await endpoint.add_device_schedule(
        "mesh_group_49155",
        "ff000001",
        [1],
        [3600],
        [1],
        group_id="mesh_group_49155",
        mesh_gateway_id="03ab0000000000a1",
    )

    assert result == [{"id": 1}]
    endpoint._add_mesh_schedule_by_candidates.assert_awaited_once_with(
        ["03ab0000000000a1"],
        days=[1],
        times=[3600],
        events=[1],
    )


@pytest.mark.asyncio
async def test_schedule_endpoint_delete_uses_mesh_candidates_for_mesh_groups() -> None:
    endpoint = cast(Any, _make_endpoint())
    endpoint._delete_mesh_schedules_by_candidates = AsyncMock(return_value=[{"id": 1}])

    result = await endpoint.delete_device_schedules(
        "mesh_group_49155",
        "ff000001",
        [1],
        group_id="mesh_group_49155",
        mesh_gateway_id="03ab0000000000a1",
    )

    assert result == [{"id": 1}]
    endpoint._delete_mesh_schedules_by_candidates.assert_awaited_once_with(
        ["03ab0000000000a1"],
        schedule_ids=[1],
    )


@pytest.mark.asyncio
async def test_schedule_endpoint_get_propagates_missing_mesh_candidates() -> None:
    endpoint = _make_endpoint()

    with pytest.raises(
        LiproApiError, match="Mesh schedule candidate IoT IDs unavailable"
    ):
        await endpoint.get_device_schedules("mesh_group_49155", "ff000001")


@pytest.mark.asyncio
async def test_schedule_endpoint_add_validates_matching_time_and_event_lengths() -> None:
    endpoint = _make_endpoint()

    with pytest.raises(ValueError, match="times and events must have same length"):
        await endpoint.add_device_schedule(
            "03ab5ccd7c123456",
            "ff000001",
            [1],
            [3600],
            [0, 1],
        )
