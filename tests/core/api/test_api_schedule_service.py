"""Tests for ScheduleApiService wrapper behavior."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.core.api.errors import LiproApiError
from custom_components.lipro.core.api.schedule_service import ScheduleApiService


@pytest.mark.asyncio
async def test_schedule_api_service_get_uses_mesh_candidates_for_mesh_groups() -> None:
    client = SimpleNamespace(
        _is_mesh_group_id=lambda device_id: device_id.startswith("mesh_group_"),
        _require_mesh_schedule_candidate_ids=lambda **_kwargs: ["03ab0000000000a1"],
        _get_mesh_schedules_by_candidates=AsyncMock(return_value=[{"id": 7}]),
        _request_schedule_timings=AsyncMock(return_value=[{"id": 8}]),
        _to_device_type_hex=lambda value: str(value),
    )

    service = ScheduleApiService(client)
    result = await service.get_device_schedules("mesh_group_49155", "ff000001")

    assert result == [{"id": 7}]
    client._get_mesh_schedules_by_candidates.assert_awaited_once_with(
        ["03ab0000000000a1"]
    )
    client._request_schedule_timings.assert_not_awaited()


@pytest.mark.asyncio
async def test_schedule_api_service_add_uses_mesh_candidates_for_mesh_groups() -> None:
    client = SimpleNamespace(
        _is_mesh_group_id=lambda device_id: device_id.startswith("mesh_group_"),
        _require_mesh_schedule_candidate_ids=lambda **_kwargs: ["03ab0000000000a1"],
        _add_mesh_schedule_by_candidates=AsyncMock(return_value=[{"id": 1}]),
        _request_schedule_timings=AsyncMock(return_value=[{"id": 2}]),
        _to_device_type_hex=lambda value: str(value),
    )

    service = ScheduleApiService(client)
    result = await service.add_device_schedule(
        "mesh_group_49155",
        "ff000001",
        [1],
        [3600],
        [1],
        group_id="mesh_group_49155",
    )

    assert result == [{"id": 1}]
    client._add_mesh_schedule_by_candidates.assert_awaited_once_with(
        ["03ab0000000000a1"],
        days=[1],
        times=[3600],
        events=[1],
    )
    client._request_schedule_timings.assert_not_awaited()


@pytest.mark.asyncio
async def test_schedule_api_service_delete_uses_mesh_candidates_for_mesh_groups() -> (
    None
):
    client = SimpleNamespace(
        _is_mesh_group_id=lambda device_id: device_id.startswith("mesh_group_"),
        _require_mesh_schedule_candidate_ids=lambda **_kwargs: ["03ab0000000000a1"],
        _delete_mesh_schedules_by_candidates=AsyncMock(return_value=[{"id": 1}]),
        _request_schedule_timings=AsyncMock(return_value=[{"id": 2}]),
        _to_device_type_hex=lambda value: str(value),
    )

    service = ScheduleApiService(client)
    result = await service.delete_device_schedules(
        "mesh_group_49155",
        "ff000001",
        [1],
        group_id="mesh_group_49155",
    )

    assert result == [{"id": 1}]
    client._delete_mesh_schedules_by_candidates.assert_awaited_once_with(
        ["03ab0000000000a1"],
        schedule_ids=[1],
    )
    client._request_schedule_timings.assert_not_awaited()


@pytest.mark.asyncio
async def test_schedule_api_service_get_propagates_missing_mesh_candidates() -> None:
    client = SimpleNamespace(
        _is_mesh_group_id=lambda device_id: device_id.startswith("mesh_group_"),
        _require_mesh_schedule_candidate_ids=lambda **_kwargs: (_ for _ in ()).throw(
            LiproApiError(
                "Mesh schedule candidate IoT IDs unavailable",
                code="mesh_schedule_candidates_unavailable",
            )
        ),
        _get_mesh_schedules_by_candidates=AsyncMock(return_value=[]),
        _request_schedule_timings=AsyncMock(return_value=[]),
        _to_device_type_hex=lambda value: str(value),
    )

    service = ScheduleApiService(client)
    with pytest.raises(
        LiproApiError, match="Mesh schedule candidate IoT IDs unavailable"
    ):
        await service.get_device_schedules("mesh_group_49155", "ff000001")

    client._request_schedule_timings.assert_not_awaited()


@pytest.mark.asyncio
async def test_schedule_api_service_add_validates_matching_time_and_event_lengths() -> (
    None
):
    client = SimpleNamespace(
        _is_mesh_group_id=lambda _device_id: False,
        _request_schedule_timings=AsyncMock(),
        _to_device_type_hex=lambda value: str(value),
    )

    service = ScheduleApiService(client)
    with pytest.raises(ValueError, match="times and events must have same length"):
        await service.add_device_schedule(
            "03ab5ccd7c123456",
            "ff000001",
            [1],
            [3600],
            [0, 1],
        )
