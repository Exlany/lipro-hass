"""Tests for API schedule service helpers."""

from __future__ import annotations

import asyncio
from time import monotonic
from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.core.api.api_schedule_service import (
    add_mesh_schedule_by_candidates,
    delete_mesh_schedules_by_candidates,
    get_mesh_schedules_by_candidates,
)


class DummyApiError(Exception):
    """Test-only API error with optional code."""

    def __init__(self, message: str, code: int | str | None = None) -> None:
        super().__init__(message)
        self.code = code


@pytest.mark.asyncio
async def test_get_mesh_schedules_by_candidates_returns_first_non_empty_rows() -> None:
    execute_candidate_request = AsyncMock(
        side_effect=[
            (False, None, DummyApiError("busy", 500)),
            (True, {"data": [{"id": 7}]}, None),
        ]
    )

    result = await get_mesh_schedules_by_candidates(
        candidate_device_ids=["03ab0000000000a1", "03ab0000000000a2"],
        execute_candidate_request=execute_candidate_request,
        iot_request=AsyncMock(return_value={}),
        extract_timings_list=lambda payload: payload.get("data", []),
        normalize_mesh_timing_rows=lambda rows, fallback_device_id: [
            {"id": row["id"], "deviceId": fallback_device_id} for row in rows
        ],
        path_ble_schedule_get="/v2/schedule/get",
        build_mesh_schedule_get_body=lambda candidate: {"deviceId": candidate},
        raise_on_total_failure=True,
    )

    assert result == [{"id": 7, "deviceId": "03ab0000000000a2"}]
    assert execute_candidate_request.await_count == 2


@pytest.mark.asyncio
async def test_get_mesh_schedules_by_candidates_returns_without_waiting_slow_candidates() -> (
    None
):
    async def execute_candidate_request(*, candidate_id: str, **_kwargs):
        if candidate_id.endswith("a1"):
            await asyncio.sleep(0.3)
            return False, None, DummyApiError("slow fail", 500)
        return True, {"data": [{"id": 9}]}, None

    started = monotonic()
    result = await get_mesh_schedules_by_candidates(
        candidate_device_ids=["03ab0000000000a1", "03ab0000000000a2"],
        execute_candidate_request=execute_candidate_request,
        iot_request=AsyncMock(return_value={}),
        extract_timings_list=lambda payload: payload.get("data", []),
        normalize_mesh_timing_rows=lambda rows, fallback_device_id: [
            {"id": row["id"], "deviceId": fallback_device_id} for row in rows
        ],
        path_ble_schedule_get="/v2/schedule/get",
        build_mesh_schedule_get_body=lambda candidate: {"deviceId": candidate},
        raise_on_total_failure=True,
    )
    elapsed = monotonic() - started

    assert result == [{"id": 9, "deviceId": "03ab0000000000a2"}]
    assert elapsed < 0.2


@pytest.mark.asyncio
async def test_add_mesh_schedule_by_candidates_returns_refreshed_rows_on_success() -> (
    None
):
    execute_candidate_request = AsyncMock(
        side_effect=[
            (False, None, DummyApiError("busy", 500)),
            (True, {"ok": True}, None),
        ]
    )
    get_mesh_schedules = AsyncMock(return_value=[{"id": 1}])

    result = await add_mesh_schedule_by_candidates(
        candidate_device_ids=["03ab0000000000a1", "03ab0000000000a2"],
        days=[1],
        times=[3600],
        events=[0],
        execute_candidate_request=execute_candidate_request,
        iot_request=AsyncMock(return_value={}),
        get_mesh_schedules_by_candidates_request=get_mesh_schedules,
        path_ble_schedule_add="/v2/schedule/add",
        build_mesh_schedule_add_body=lambda candidate, schedule_json: {
            "deviceId": candidate,
            "scheduleJson": schedule_json,
        },
        encode_mesh_schedule_json=lambda *_: '{"days":[1],"time":[3600],"evt":[0]}',
    )

    assert result == [{"id": 1}]
    assert execute_candidate_request.await_count == 2
    get_mesh_schedules.assert_awaited_once_with(
        ["03ab0000000000a1", "03ab0000000000a2"],
        raise_on_total_failure=False,
    )


@pytest.mark.asyncio
async def test_add_mesh_schedule_by_candidates_raises_last_error_on_total_failure() -> (
    None
):
    execute_candidate_request = AsyncMock(
        side_effect=[
            (False, None, DummyApiError("bad1", 500)),
            (False, None, DummyApiError("bad2", 501)),
        ]
    )

    with pytest.raises(DummyApiError, match="bad2"):
        await add_mesh_schedule_by_candidates(
            candidate_device_ids=["03ab0000000000a1", "03ab0000000000a2"],
            days=[1],
            times=[3600],
            events=[0],
            execute_candidate_request=execute_candidate_request,
            iot_request=AsyncMock(return_value={}),
            get_mesh_schedules_by_candidates_request=AsyncMock(return_value=[]),
            path_ble_schedule_add="/v2/schedule/add",
            build_mesh_schedule_add_body=lambda candidate, schedule_json: {
                "deviceId": candidate,
                "scheduleJson": schedule_json,
            },
            encode_mesh_schedule_json=lambda *_: '{"days":[1],"time":[3600],"evt":[0]}',
        )


@pytest.mark.asyncio
async def test_add_mesh_schedule_by_candidates_empty_candidates_returns_empty() -> None:
    result = await add_mesh_schedule_by_candidates(
        candidate_device_ids=[],
        days=[1],
        times=[3600],
        events=[0],
        execute_candidate_request=AsyncMock(),
        iot_request=AsyncMock(return_value={}),
        get_mesh_schedules_by_candidates_request=AsyncMock(return_value=[]),
        path_ble_schedule_add="/v2/schedule/add",
        build_mesh_schedule_add_body=lambda candidate, schedule_json: {
            "deviceId": candidate,
            "scheduleJson": schedule_json,
        },
        encode_mesh_schedule_json=lambda *_: '{"days":[1],"time":[3600],"evt":[0]}',
    )

    assert result == []


@pytest.mark.asyncio
async def test_delete_mesh_schedules_by_candidates_returns_refreshed_rows_if_any_deleted() -> (
    None
):
    execute_candidate_request = AsyncMock(
        side_effect=[
            (False, None, DummyApiError("bad1", 500)),
            (True, {"ok": True}, None),
            (False, None, DummyApiError("bad3", 503)),
        ]
    )
    get_mesh_schedules = AsyncMock(return_value=[{"id": 2}])

    result = await delete_mesh_schedules_by_candidates(
        candidate_device_ids=[
            "03ab0000000000a1",
            "03ab0000000000a2",
            "03ab0000000000a3",
        ],
        schedule_ids=[1],
        execute_candidate_request=execute_candidate_request,
        iot_request=AsyncMock(return_value={}),
        get_mesh_schedules_by_candidates_request=get_mesh_schedules,
        path_ble_schedule_delete="/v2/schedule/delete",
        build_mesh_schedule_delete_body=lambda candidate, schedule_ids: {
            "deviceId": candidate,
            "scheduleIdList": schedule_ids,
        },
    )

    assert result == [{"id": 2}]
    assert execute_candidate_request.await_count == 3
    get_mesh_schedules.assert_awaited_once_with(
        ["03ab0000000000a1", "03ab0000000000a2", "03ab0000000000a3"],
        raise_on_total_failure=False,
    )


@pytest.mark.asyncio
async def test_delete_mesh_schedules_by_candidates_raises_last_error_if_none_deleted() -> (
    None
):
    execute_candidate_request = AsyncMock(
        side_effect=[
            (False, None, DummyApiError("bad1", 500)),
            (False, None, DummyApiError("bad2", 501)),
        ]
    )

    with pytest.raises(DummyApiError, match="bad2"):
        await delete_mesh_schedules_by_candidates(
            candidate_device_ids=["03ab0000000000a1", "03ab0000000000a2"],
            schedule_ids=[1],
            execute_candidate_request=execute_candidate_request,
            iot_request=AsyncMock(return_value={}),
            get_mesh_schedules_by_candidates_request=AsyncMock(return_value=[]),
            path_ble_schedule_delete="/v2/schedule/delete",
            build_mesh_schedule_delete_body=lambda candidate, schedule_ids: {
                "deviceId": candidate,
                "scheduleIdList": schedule_ids,
            },
        )
