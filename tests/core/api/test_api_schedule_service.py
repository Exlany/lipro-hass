"""Tests for API schedule service helpers."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, call

import pytest

from custom_components.lipro.core.api.errors import LiproApiError
from custom_components.lipro.core.api.schedule_service import (
    ScheduleApiService,
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
    calls: list[str] = []
    slow_started = asyncio.Event()
    slow_release = asyncio.Event()
    slow_cancelled = asyncio.Event()

    async def execute_candidate_request(*, candidate_id: str, **_kwargs):
        calls.append(candidate_id)
        if candidate_id.endswith("a1"):
            slow_started.set()
            try:
                await slow_release.wait()
                return False, None, DummyApiError("slow fail", 500)
            except asyncio.CancelledError:
                slow_cancelled.set()
                raise
        await slow_started.wait()
        return True, {"data": [{"id": 9}]}, None

    try:
        result = await asyncio.wait_for(
            get_mesh_schedules_by_candidates(
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
            ),
            timeout=1,
        )
    finally:
        slow_release.set()

    assert result == [{"id": 9, "deviceId": "03ab0000000000a2"}]
    assert len(calls) == 2
    assert slow_cancelled.is_set()


@pytest.mark.asyncio
async def test_add_mesh_schedule_by_candidates_returns_refreshed_rows_on_success() -> (
    None
):
    async def execute_candidate_request(*, candidate_id, request, **_kwargs):
        await request(candidate_id)
        if candidate_id.endswith("a1"):
            return False, None, DummyApiError("busy", 500)
        return True, {"ok": True}, None

    iot_request = AsyncMock(return_value={})
    get_mesh_schedules = AsyncMock(
        side_effect=[[{"id": 0}], [{"id": 0}], [{"id": 1}]]
    )

    result = await add_mesh_schedule_by_candidates(
        candidate_device_ids=["03ab0000000000a1", "03ab0000000000a2"],
        days=[1],
        times=[3600],
        events=[0],
        execute_candidate_request=execute_candidate_request,
        iot_request=iot_request,
        get_mesh_schedules_by_candidates_request=get_mesh_schedules,
        path_ble_schedule_add="/v2/schedule/add",
        build_mesh_schedule_add_body=lambda candidate, schedule_json, schedule_id: {
            "deviceId": candidate,
            "scheduleJson": schedule_json,
            "id": schedule_id,
        },
        encode_mesh_schedule_json=lambda *_: '{"days":[1],"time":[3600],"evt":[0]}',
    )

    assert result == [{"id": 1}]
    assert iot_request.await_count == 2
    assert iot_request.await_args_list[0].args[1]["id"] == 1
    assert iot_request.await_args_list[1].args[1]["id"] == 1
    assert get_mesh_schedules.await_args_list == [
        call(
            candidate_device_ids=["03ab0000000000a1"],
            raise_on_total_failure=True,
        ),
        call(
            candidate_device_ids=["03ab0000000000a2"],
            raise_on_total_failure=True,
        ),
        call(
            candidate_device_ids=["03ab0000000000a1", "03ab0000000000a2"],
            raise_on_total_failure=False,
        ),
    ]


@pytest.mark.asyncio
async def test_add_mesh_schedule_by_candidates_uses_first_free_gap() -> None:
    async def execute_candidate_request(*, candidate_id, request, **_kwargs):
        await request(candidate_id)
        return True, {"ok": True}, None

    iot_request = AsyncMock(return_value={})
    get_mesh_schedules = AsyncMock(
        side_effect=[[{"id": 0}, {"id": 2}], [{"id": 1}]]
    )

    result = await add_mesh_schedule_by_candidates(
        candidate_device_ids=["03ab0000000000a1"],
        days=[1],
        times=[3600],
        events=[0],
        execute_candidate_request=execute_candidate_request,
        iot_request=iot_request,
        get_mesh_schedules_by_candidates_request=get_mesh_schedules,
        path_ble_schedule_add="/v2/schedule/add",
        build_mesh_schedule_add_body=lambda candidate, schedule_json, schedule_id: {
            "deviceId": candidate,
            "scheduleJson": schedule_json,
            "id": schedule_id,
        },
        encode_mesh_schedule_json=lambda *_: '{"days":[1],"time":[3600],"evt":[0]}',
    )

    assert result == [{"id": 1}]
    assert iot_request.await_args_list[0].args[1]["id"] == 1
    assert get_mesh_schedules.await_args_list == [
        call(
            candidate_device_ids=["03ab0000000000a1"],
            raise_on_total_failure=True,
        ),
        call(
            candidate_device_ids=["03ab0000000000a1"],
            raise_on_total_failure=False,
        ),
    ]



@pytest.mark.asyncio
async def test_add_mesh_schedule_by_candidates_aborts_when_pre_read_totally_fails() -> None:
    execute_candidate_request = AsyncMock()
    get_mesh_schedules = AsyncMock(side_effect=DummyApiError("pre-read failed", 599))

    with pytest.raises(DummyApiError, match="pre-read failed"):
        await add_mesh_schedule_by_candidates(
            candidate_device_ids=["03ab0000000000a1"],
            days=[1],
            times=[3600],
            events=[0],
            execute_candidate_request=execute_candidate_request,
            iot_request=AsyncMock(return_value={}),
            get_mesh_schedules_by_candidates_request=get_mesh_schedules,
            path_ble_schedule_add="/v2/schedule/add",
            build_mesh_schedule_add_body=lambda candidate, schedule_json, schedule_id: {
                "deviceId": candidate,
                "scheduleJson": schedule_json,
                "id": schedule_id,
            },
            encode_mesh_schedule_json=lambda *_: '{"days":[1],"time":[3600],"evt":[0]}',
        )

    execute_candidate_request.assert_not_awaited()
    get_mesh_schedules.assert_awaited_once_with(
        candidate_device_ids=["03ab0000000000a1"],
        raise_on_total_failure=True,
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
            build_mesh_schedule_add_body=lambda candidate, schedule_json, schedule_id: {
                "deviceId": candidate,
                "scheduleJson": schedule_json,
                "id": schedule_id,
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
        build_mesh_schedule_add_body=lambda candidate, schedule_json, schedule_id: {
            "deviceId": candidate,
            "scheduleJson": schedule_json,
            "id": schedule_id,
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
        candidate_device_ids=[
            "03ab0000000000a1",
            "03ab0000000000a2",
            "03ab0000000000a3",
        ],
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


@pytest.mark.asyncio
async def test_delete_mesh_schedules_by_candidates_returns_empty_when_no_deleted_and_no_errors() -> (
    None
):
    execute_candidate_request = AsyncMock(return_value=(False, None, None))
    get_mesh_schedules = AsyncMock(return_value=[{"id": 123}])

    result = await delete_mesh_schedules_by_candidates(
        candidate_device_ids=["03ab0000000000a1"],
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

    assert result == []
    execute_candidate_request.assert_awaited_once()
    get_mesh_schedules.assert_not_awaited()


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
    client._get_mesh_schedules_by_candidates.assert_awaited_once_with(["03ab0000000000a1"])
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
async def test_schedule_api_service_delete_uses_mesh_candidates_for_mesh_groups() -> None:
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
            LiproApiError("Mesh schedule candidate IoT IDs unavailable", code="mesh_schedule_candidates_unavailable")
        ),
        _get_mesh_schedules_by_candidates=AsyncMock(return_value=[]),
        _request_schedule_timings=AsyncMock(return_value=[]),
        _to_device_type_hex=lambda value: str(value),
    )

    service = ScheduleApiService(client)
    with pytest.raises(LiproApiError, match="Mesh schedule candidate IoT IDs unavailable"):
        await service.get_device_schedules("mesh_group_49155", "ff000001")

    client._request_schedule_timings.assert_not_awaited()
