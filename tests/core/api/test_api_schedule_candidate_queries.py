"""Mesh schedule candidate query helper tests."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.lipro.core.api.errors import LiproAuthError
from custom_components.lipro.core.api.schedule_service import (
    _next_mesh_schedule_id,
    _redact_candidate_id,
    execute_mesh_schedule_candidate_request,
    get_mesh_schedules_by_candidates,
)
from custom_components.lipro.core.api.types import ScheduleTimingRow


def _extract_schedule_rows(payload: object) -> list[ScheduleTimingRow]:
    if isinstance(payload, dict):
        rows = payload.get("data")
        if isinstance(rows, list):
            return [
                cast(ScheduleTimingRow, row) for row in rows if isinstance(row, dict)
            ]
    return []


def _normalize_schedule_rows(
    rows: Sequence[object],
    *,
    fallback_device_id: str = "",
) -> list[ScheduleTimingRow]:
    normalized: list[ScheduleTimingRow] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        raw_id = row.get("id")
        if isinstance(raw_id, bool):
            continue
        if isinstance(raw_id, (str, int)):
            normalized.append({"id": raw_id, "deviceId": fallback_device_id})
    return normalized


class DummyApiError(Exception):
    """Test-only API error with optional code."""

    def __init__(self, message: str, code: int | str | None = None) -> None:
        super().__init__(message)
        self.code = code


def test_redact_candidate_id_masks_short_and_long_ids() -> None:
    assert _redact_candidate_id("") == "***"
    assert _redact_candidate_id("1234") == "***"
    assert _redact_candidate_id("03ab0000000000a1") == "***00a1"


def test_next_mesh_schedule_id_ignores_bool_and_finds_first_gap() -> None:
    assert (
        _next_mesh_schedule_id(
            [
                {"id": False},
                {"id": 0},
                {"id": " 1 "},
                {"id": 3},
            ]
        )
        == 2
    )


@pytest.mark.asyncio
async def test_execute_mesh_schedule_candidate_request_returns_error_tuple_for_unexpected_error() -> (
    None
):
    logger = Mock()

    result = await execute_mesh_schedule_candidate_request(
        candidate_id="03ab0000000000a1",
        operation="GET",
        request=AsyncMock(side_effect=RuntimeError("boom")),
        lipro_auth_error=ValueError,
        lipro_api_error=DummyApiError,
        logger=logger,
    )

    assert result[0] is False
    assert result[1] is None
    assert isinstance(result[2], RuntimeError)
    logger.debug.assert_called_once()


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
        extract_timings_list=_extract_schedule_rows,
        normalize_mesh_timing_rows=_normalize_schedule_rows,
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
                extract_timings_list=_extract_schedule_rows,
                normalize_mesh_timing_rows=_normalize_schedule_rows,
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
async def test_get_mesh_schedules_by_candidates_returns_empty_after_successful_empty_payload() -> (
    None
):
    result = await get_mesh_schedules_by_candidates(
        candidate_device_ids=["03ab0000000000a1"],
        execute_candidate_request=AsyncMock(return_value=(True, None, None)),
        iot_request=AsyncMock(return_value={}),
        extract_timings_list=_extract_schedule_rows,
        normalize_mesh_timing_rows=_normalize_schedule_rows,
        path_ble_schedule_get="/v2/schedule/get",
        build_mesh_schedule_get_body=lambda candidate: {"deviceId": candidate},
        raise_on_total_failure=True,
    )

    assert result == []


@pytest.mark.asyncio
async def test_get_mesh_schedules_by_candidates_empty_returns_empty() -> None:
    result = await get_mesh_schedules_by_candidates(
        candidate_device_ids=[],
        execute_candidate_request=AsyncMock(),
        iot_request=AsyncMock(return_value={}),
        extract_timings_list=_extract_schedule_rows,
        normalize_mesh_timing_rows=_normalize_schedule_rows,
        path_ble_schedule_get="/v2/schedule/get",
        build_mesh_schedule_get_body=lambda candidate: {"deviceId": candidate},
    )

    assert result == []


@pytest.mark.asyncio
async def test_get_mesh_schedules_by_candidates_auth_error_bubbles() -> None:
    with pytest.raises(LiproAuthError, match="auth"):
        await get_mesh_schedules_by_candidates(
            candidate_device_ids=["03ab0000000000a1"],
            execute_candidate_request=AsyncMock(side_effect=LiproAuthError("auth")),
            iot_request=AsyncMock(return_value={}),
            extract_timings_list=_extract_schedule_rows,
            normalize_mesh_timing_rows=_normalize_schedule_rows,
            path_ble_schedule_get="/v2/schedule/get",
            build_mesh_schedule_get_body=lambda candidate: {"deviceId": candidate},
        )


@pytest.mark.asyncio
async def test_get_mesh_schedules_by_candidates_total_failure_behaviors() -> None:
    with pytest.raises(DummyApiError, match="bad2"):
        await get_mesh_schedules_by_candidates(
            candidate_device_ids=["03ab0000000000a1", "03ab0000000000a2"],
            execute_candidate_request=AsyncMock(
                side_effect=[
                    (False, None, DummyApiError("bad1", 500)),
                    (False, None, DummyApiError("bad2", 501)),
                ]
            ),
            iot_request=AsyncMock(return_value={}),
            extract_timings_list=_extract_schedule_rows,
            normalize_mesh_timing_rows=_normalize_schedule_rows,
            path_ble_schedule_get="/v2/schedule/get",
            build_mesh_schedule_get_body=lambda candidate: {"deviceId": candidate},
            raise_on_total_failure=True,
        )

    result = await get_mesh_schedules_by_candidates(
        candidate_device_ids=["03ab0000000000a1", "03ab0000000000a2"],
        execute_candidate_request=AsyncMock(
            side_effect=[
                (False, None, DummyApiError("bad1", 500)),
                (False, None, DummyApiError("bad2", 501)),
            ]
        ),
        iot_request=AsyncMock(return_value={}),
        extract_timings_list=_extract_schedule_rows,
        normalize_mesh_timing_rows=_normalize_schedule_rows,
        path_ble_schedule_get="/v2/schedule/get",
        build_mesh_schedule_get_body=lambda candidate: {"deviceId": candidate},
        raise_on_total_failure=False,
    )

    assert result == []
