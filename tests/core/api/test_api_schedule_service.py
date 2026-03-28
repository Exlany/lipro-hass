"""Tests for schedule endpoint public behavior and schedule-service helpers."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api.endpoints.schedule import ScheduleEndpoints
from custom_components.lipro.core.api.errors import LiproApiError
from custom_components.lipro.core.api.schedule_service import (
    add_mesh_schedule_by_candidates,
    delete_mesh_schedules_by_candidates,
    get_mesh_schedules_by_candidates,
)
from custom_components.lipro.core.api.types import ScheduleTimingRow


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


@pytest.mark.asyncio
async def test_get_mesh_schedules_by_candidates_returns_first_populated_rows() -> None:
    async def execute_candidate_request(*, candidate_id: str, **_: object) -> tuple[bool, object | None, Exception | None]:
        rows = [] if candidate_id == "candidate-1" else [{"id": 7}]
        return True, {"rows": rows}, None

    def extract_timings_list(payload: object) -> list[object]:
        mapping = cast(dict[str, object], payload)
        rows = mapping.get("rows")
        assert isinstance(rows, list)
        return rows

    def normalize_mesh_timing_rows(
        rows: list[object],
        fallback_device_id: str,
    ) -> list[ScheduleTimingRow]:
        normalized: list[ScheduleTimingRow] = []
        for row in rows:
            mapping = cast(dict[str, object], row)
            row_id = mapping.get("id")
            assert isinstance(row_id, int)
            normalized.append({"id": row_id, "deviceId": fallback_device_id})
        return normalized

    result = await get_mesh_schedules_by_candidates(
        candidate_device_ids=["candidate-1", "candidate-2"],
        execute_candidate_request=execute_candidate_request,
        iot_request=AsyncMock(),
        extract_timings_list=extract_timings_list,
        normalize_mesh_timing_rows=normalize_mesh_timing_rows,
        path_ble_schedule_get="/schedule/get",
        build_mesh_schedule_get_body=lambda candidate_id: {"deviceId": candidate_id},
    )

    assert result == [{"id": 7, "deviceId": "candidate-2"}]


@pytest.mark.asyncio
async def test_add_mesh_schedule_by_candidates_refreshes_full_candidate_set_after_success() -> None:
    refresh_calls: list[tuple[list[str], bool]] = []
    request_bodies: list[dict[str, object]] = []

    async def get_rows(*, candidate_device_ids: list[str], raise_on_total_failure: bool = True) -> list[ScheduleTimingRow]:
        refresh_calls.append((list(candidate_device_ids), raise_on_total_failure))
        if raise_on_total_failure:
            return [{"id": 0}]
        return [{"id": 1, "deviceId": "candidate-1"}]

    async def execute_candidate_request(*, candidate_id: str, request, **_: object) -> tuple[bool, object | None, Exception | None]:
        request_bodies.append(await request(candidate_id))
        return True, None, None

    result = await add_mesh_schedule_by_candidates(
        candidate_device_ids=["candidate-1", "candidate-2"],
        days=[1],
        times=[3600],
        events=[1],
        execute_candidate_request=execute_candidate_request,
        iot_request=AsyncMock(side_effect=lambda _path, body: body),
        get_mesh_schedules_by_candidates_request=get_rows,
        path_ble_schedule_add="/schedule/add",
        build_mesh_schedule_add_body=lambda candidate, *, schedule_json, schedule_id: {
            "deviceId": candidate,
            "scheduleJson": schedule_json,
            "id": schedule_id,
        },
        encode_mesh_schedule_json=lambda days, times, events: f"{days}:{times}:{events}",
    )

    assert result == [{"id": 1, "deviceId": "candidate-1"}]
    assert refresh_calls == [(["candidate-1"], True), (["candidate-1", "candidate-2"], False)]
    assert request_bodies == [
        {
            "deviceId": "candidate-1",
            "scheduleJson": "[1]:[3600]:[1]",
            "id": 1,
        }
    ]


@pytest.mark.asyncio
async def test_delete_mesh_schedules_by_candidates_raises_latest_error_when_all_batches_fail() -> None:
    async def execute_candidate_request(*, candidate_id: str, **_: object) -> tuple[bool, object | None, Exception | None]:
        error = ValueError("first") if candidate_id == "candidate-1" else RuntimeError("last")
        return False, None, error

    with pytest.raises(RuntimeError, match="last"):
        await delete_mesh_schedules_by_candidates(
            candidate_device_ids=["candidate-1", "candidate-2"],
            schedule_ids=[7],
            execute_candidate_request=execute_candidate_request,
            iot_request=AsyncMock(),
            get_mesh_schedules_by_candidates_request=AsyncMock(return_value=[]),
            path_ble_schedule_delete="/schedule/delete",
            build_mesh_schedule_delete_body=lambda candidate, *, schedule_ids: {
                "deviceId": candidate,
                "idList": schedule_ids,
            },
        )
