"""Schedule helper services for explicit REST schedule endpoints."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence

from .schedule_codec import next_mesh_schedule_id
from .schedule_service_support import (
    _redact_candidate_id as _support_redact_candidate_id,
    add_mesh_schedule_for_candidate,
    collect_schedule_rows_from_batch,
    delete_mesh_schedule_batch,
    execute_mesh_schedule_candidate_request as _execute_mesh_schedule_candidate_request,
    iter_candidate_batches,
    refresh_mesh_schedule_rows,
    remember_last_error,
)
from .types import ScheduleTimingRow

type ScheduleRows = list[ScheduleTimingRow]
type RawScheduleRows = Sequence[object]
type ScheduleRequestBody = dict[str, object]
type CandidateRequestResult = tuple[bool, object | None, Exception | None]
type CandidateRequest = Callable[[str], Awaitable[object]]
type CandidateRequestExecutor = Callable[..., Awaitable[CandidateRequestResult]]
type IotRequest = Callable[..., Awaitable[object]]
type ExtractTimingsList = Callable[[object], RawScheduleRows]
type NormalizeMeshTimingRows = Callable[..., ScheduleRows]
type BuildMeshScheduleGetBody = Callable[[str], ScheduleRequestBody]
type BuildMeshScheduleAddBody = Callable[..., ScheduleRequestBody]
type BuildMeshScheduleDeleteBody = Callable[..., ScheduleRequestBody]
type GetMeshSchedulesByCandidatesRequest = Callable[..., Awaitable[ScheduleRows]]
type EncodeMeshScheduleJson = Callable[..., str]
type CandidateBatch = Sequence[str]


_redact_candidate_id = _support_redact_candidate_id
execute_mesh_schedule_candidate_request = _execute_mesh_schedule_candidate_request


def _next_mesh_schedule_id(rows: ScheduleRows) -> int:
    """Return the first free non-negative mesh schedule ID."""
    return next_mesh_schedule_id(rows)


async def get_mesh_schedules_by_candidates(
    *,
    candidate_device_ids: list[str],
    execute_candidate_request: CandidateRequestExecutor,
    iot_request: IotRequest,
    extract_timings_list: ExtractTimingsList,
    normalize_mesh_timing_rows: NormalizeMeshTimingRows,
    path_ble_schedule_get: str,
    build_mesh_schedule_get_body: BuildMeshScheduleGetBody,
    raise_on_total_failure: bool = True,
) -> ScheduleRows:
    """Query mesh schedule list from candidate device IDs."""
    if not candidate_device_ids:
        return []

    last_error: Exception | None = None
    any_candidate_succeeded = False

    for batch in iter_candidate_batches(candidate_device_ids):
        (
            normalized_rows,
            batch_succeeded,
            batch_error,
        ) = await collect_schedule_rows_from_batch(
            candidate_ids=batch,
            execute_candidate_request=execute_candidate_request,
            iot_request=iot_request,
            extract_timings_list=extract_timings_list,
            normalize_mesh_timing_rows=normalize_mesh_timing_rows,
            path_ble_schedule_get=path_ble_schedule_get,
            build_mesh_schedule_get_body=build_mesh_schedule_get_body,
        )
        any_candidate_succeeded = any_candidate_succeeded or batch_succeeded
        last_error = remember_last_error(last_error, batch_error)
        if normalized_rows:
            return normalized_rows

    if any_candidate_succeeded:
        return []
    if raise_on_total_failure and last_error is not None:
        raise last_error
    return []


async def add_mesh_schedule_by_candidates(
    *,
    candidate_device_ids: list[str],
    days: list[int],
    times: list[int],
    events: list[int],
    execute_candidate_request: CandidateRequestExecutor,
    iot_request: IotRequest,
    get_mesh_schedules_by_candidates_request: GetMeshSchedulesByCandidatesRequest,
    path_ble_schedule_add: str,
    build_mesh_schedule_add_body: BuildMeshScheduleAddBody,
    encode_mesh_schedule_json: EncodeMeshScheduleJson,
) -> ScheduleRows:
    """Try mesh schedule add across candidates and return refreshed rows."""
    schedule_json = encode_mesh_schedule_json(days, times, events)

    last_error: Exception | None = None
    for candidate_id in candidate_device_ids:
        succeeded, _, error = await add_mesh_schedule_for_candidate(
            candidate_id=candidate_id,
            schedule_json=schedule_json,
            execute_candidate_request=execute_candidate_request,
            iot_request=iot_request,
            get_mesh_schedules_by_candidates_request=get_mesh_schedules_by_candidates_request,
            path_ble_schedule_add=path_ble_schedule_add,
            build_mesh_schedule_add_body=build_mesh_schedule_add_body,
        )
        if succeeded:
            return await refresh_mesh_schedule_rows(
                candidate_device_ids=candidate_device_ids,
                get_mesh_schedules_by_candidates_request=get_mesh_schedules_by_candidates_request,
            )
        last_error = remember_last_error(last_error, error)

    if last_error is not None:
        raise last_error
    return []


async def delete_mesh_schedules_by_candidates(
    *,
    candidate_device_ids: list[str],
    schedule_ids: list[int],
    execute_candidate_request: CandidateRequestExecutor,
    iot_request: IotRequest,
    get_mesh_schedules_by_candidates_request: GetMeshSchedulesByCandidatesRequest,
    path_ble_schedule_delete: str,
    build_mesh_schedule_delete_body: BuildMeshScheduleDeleteBody,
) -> ScheduleRows:
    """Try mesh schedule delete across candidates and return refreshed rows."""
    any_deleted = False
    last_error: Exception | None = None

    for batch in iter_candidate_batches(candidate_device_ids):
        batch_deleted, batch_error = await delete_mesh_schedule_batch(
            candidate_ids=batch,
            schedule_ids=schedule_ids,
            execute_candidate_request=execute_candidate_request,
            iot_request=iot_request,
            path_ble_schedule_delete=path_ble_schedule_delete,
            build_mesh_schedule_delete_body=build_mesh_schedule_delete_body,
        )
        any_deleted = any_deleted or batch_deleted
        last_error = remember_last_error(last_error, batch_error)

    if any_deleted:
        return await refresh_mesh_schedule_rows(
            candidate_device_ids=candidate_device_ids,
            get_mesh_schedules_by_candidates_request=get_mesh_schedules_by_candidates_request,
        )
    if last_error is not None:
        raise last_error
    return []


__all__ = [
    "BuildMeshScheduleAddBody",
    "BuildMeshScheduleDeleteBody",
    "BuildMeshScheduleGetBody",
    "CandidateBatch",
    "CandidateRequest",
    "CandidateRequestExecutor",
    "CandidateRequestResult",
    "EncodeMeshScheduleJson",
    "ExtractTimingsList",
    "GetMeshSchedulesByCandidatesRequest",
    "IotRequest",
    "NormalizeMeshTimingRows",
    "RawScheduleRows",
    "ScheduleRequestBody",
    "ScheduleRows",
    "_next_mesh_schedule_id",
    "_redact_candidate_id",
    "add_mesh_schedule_by_candidates",
    "delete_mesh_schedules_by_candidates",
    "execute_mesh_schedule_candidate_request",
    "get_mesh_schedules_by_candidates",
]
