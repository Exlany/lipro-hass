"""Schedule helper services for explicit REST schedule endpoints."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterator, Sequence
import logging

from .types import ScheduleTimingRow

_MESH_SCHEDULE_CANDIDATE_CONCURRENCY = 3
_MESH_SCHEDULE_CANDIDATE_TIMEOUT_SECONDS = 15.0

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
type CandidateBatchGetResult = tuple[ScheduleRows | None, bool, Exception | None]
type DeleteBatchResult = tuple[bool, Exception | None]


def _redact_candidate_id(candidate_id: str) -> str:
    """Redact candidate IDs for logs and task names."""
    if not candidate_id or len(candidate_id) <= 4:
        return "***"
    return f"***{candidate_id[-4:]}"


def _next_mesh_schedule_id(rows: ScheduleRows) -> int:
    """Return the first free non-negative mesh schedule ID."""
    used_ids: set[int] = set()
    for row in rows:
        raw_id = row.get("id")
        if isinstance(raw_id, bool):
            continue
        if isinstance(raw_id, int):
            if raw_id >= 0:
                used_ids.add(raw_id)
            continue
        if isinstance(raw_id, str) and raw_id.strip().isdigit():
            used_ids.add(int(raw_id.strip()))

    next_id = 0
    while next_id in used_ids:
        next_id += 1
    return next_id


def _iter_candidate_batches(
    candidate_device_ids: Sequence[str],
) -> Iterator[CandidateBatch]:
    """Yield candidate IDs in bounded-concurrency batches."""
    for start in range(0, len(candidate_device_ids), _MESH_SCHEDULE_CANDIDATE_CONCURRENCY):
        yield candidate_device_ids[start : start + _MESH_SCHEDULE_CANDIDATE_CONCURRENCY]


def _remember_last_error(
    last_error: Exception | None,
    error: Exception | None,
) -> Exception | None:
    """Prefer the most recent concrete candidate error when present."""
    return error if error is not None else last_error


async def execute_mesh_schedule_candidate_request(
    *,
    candidate_id: str,
    operation: str,
    request: CandidateRequest,
    lipro_auth_error: type[Exception],
    lipro_api_error: type[Exception],
    logger: logging.Logger,
) -> CandidateRequestResult:
    """Execute one mesh schedule candidate request with shared error handling."""
    try:
        return True, await request(candidate_id), None
    except lipro_auth_error:
        raise
    except lipro_api_error as err:
        logger.debug(
            "Mesh schedule %s failed for %s (error=%s, code=%s)",
            operation,
            _redact_candidate_id(candidate_id),
            type(err).__name__,
            getattr(err, "code", None),
        )
        return False, None, err
    except (
        AttributeError,
        LookupError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as err:
        logger.debug(
            "Mesh schedule %s failed for %s (error=%s)",
            operation,
            _redact_candidate_id(candidate_id),
            type(err).__name__,
        )
        return False, None, err


async def _run_timed_get_candidate_request(
    *,
    candidate_id: str,
    execute_candidate_request: CandidateRequestExecutor,
    iot_request: IotRequest,
    path_ble_schedule_get: str,
    build_mesh_schedule_get_body: BuildMeshScheduleGetBody,
) -> tuple[str, CandidateRequestResult]:
    """Execute one GET candidate request with timeout normalization."""
    try:
        result = await asyncio.wait_for(
            execute_candidate_request(
                candidate_id=candidate_id,
                operation="GET",
                request=lambda candidate: iot_request(
                    path_ble_schedule_get,
                    build_mesh_schedule_get_body(candidate),
                ),
            ),
            timeout=_MESH_SCHEDULE_CANDIDATE_TIMEOUT_SECONDS,
        )
    except TimeoutError as err:
        result = (False, None, err)
    return candidate_id, result


def _create_get_candidate_tasks(
    *,
    candidate_ids: CandidateBatch,
    execute_candidate_request: CandidateRequestExecutor,
    iot_request: IotRequest,
    path_ble_schedule_get: str,
    build_mesh_schedule_get_body: BuildMeshScheduleGetBody,
) -> list[asyncio.Task[tuple[str, CandidateRequestResult]]]:
    """Create bounded GET candidate tasks with stable task naming."""
    return [
        asyncio.create_task(
            _run_timed_get_candidate_request(
                candidate_id=candidate_id,
                execute_candidate_request=execute_candidate_request,
                iot_request=iot_request,
                path_ble_schedule_get=path_ble_schedule_get,
                build_mesh_schedule_get_body=build_mesh_schedule_get_body,
            ),
            name=f"lipro_mesh_schedule_get:{_redact_candidate_id(candidate_id)}",
        )
        for candidate_id in candidate_ids
    ]


async def _drain_candidate_tasks(
    tasks: Sequence[asyncio.Task[tuple[str, CandidateRequestResult]]],
) -> None:
    """Cancel unfinished candidate tasks and drain their exceptions."""
    for task in tasks:
        if not task.done():
            task.cancel()
    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except asyncio.CancelledError:
        await asyncio.shield(asyncio.gather(*tasks, return_exceptions=True))
        raise


async def _collect_schedule_rows_from_batch(
    *,
    candidate_ids: CandidateBatch,
    execute_candidate_request: CandidateRequestExecutor,
    iot_request: IotRequest,
    extract_timings_list: ExtractTimingsList,
    normalize_mesh_timing_rows: NormalizeMeshTimingRows,
    path_ble_schedule_get: str,
    build_mesh_schedule_get_body: BuildMeshScheduleGetBody,
) -> CandidateBatchGetResult:
    """Return the first populated normalized row set produced by one batch."""
    last_error: Exception | None = None
    any_candidate_succeeded = False
    tasks = _create_get_candidate_tasks(
        candidate_ids=candidate_ids,
        execute_candidate_request=execute_candidate_request,
        iot_request=iot_request,
        path_ble_schedule_get=path_ble_schedule_get,
        build_mesh_schedule_get_body=build_mesh_schedule_get_body,
    )
    try:
        for completed in asyncio.as_completed(tasks):
            candidate_id, (succeeded, payload, error) = await completed
            if not succeeded:
                last_error = _remember_last_error(last_error, error)
                continue

            any_candidate_succeeded = True
            if payload is None:
                continue

            normalized_rows = normalize_mesh_timing_rows(
                extract_timings_list(payload),
                fallback_device_id=candidate_id,
            )
            if normalized_rows:
                return normalized_rows, True, last_error
    finally:
        await _drain_candidate_tasks(tasks)

    return None, any_candidate_succeeded, last_error


async def _refresh_mesh_schedule_rows(
    *,
    candidate_device_ids: Sequence[str],
    get_mesh_schedules_by_candidates_request: GetMeshSchedulesByCandidatesRequest,
) -> ScheduleRows:
    """Refresh schedule rows across the original candidate set after mutation."""
    return await get_mesh_schedules_by_candidates_request(
        candidate_device_ids=list(candidate_device_ids),
        raise_on_total_failure=False,
    )


async def _add_mesh_schedule_for_candidate(
    *,
    candidate_id: str,
    schedule_json: str,
    execute_candidate_request: CandidateRequestExecutor,
    iot_request: IotRequest,
    get_mesh_schedules_by_candidates_request: GetMeshSchedulesByCandidatesRequest,
    path_ble_schedule_add: str,
    build_mesh_schedule_add_body: BuildMeshScheduleAddBody,
) -> CandidateRequestResult:
    """Add one mesh schedule to a single candidate after picking the next ID."""
    current_rows = await get_mesh_schedules_by_candidates_request(
        candidate_device_ids=[candidate_id],
        raise_on_total_failure=True,
    )
    schedule_id = _next_mesh_schedule_id(current_rows)
    return await execute_candidate_request(
        candidate_id=candidate_id,
        operation="ADD",
        request=lambda candidate, schedule_id=schedule_id: iot_request(
            path_ble_schedule_add,
            build_mesh_schedule_add_body(
                candidate,
                schedule_json=schedule_json,
                schedule_id=schedule_id,
            ),
        ),
    )


async def _delete_mesh_schedule_batch(
    *,
    candidate_ids: CandidateBatch,
    schedule_ids: list[int],
    execute_candidate_request: CandidateRequestExecutor,
    iot_request: IotRequest,
    path_ble_schedule_delete: str,
    build_mesh_schedule_delete_body: BuildMeshScheduleDeleteBody,
) -> DeleteBatchResult:
    """Delete one schedule batch and summarize success plus latest error."""
    any_deleted = False
    last_error: Exception | None = None
    batch_results = await asyncio.gather(
        *(
            execute_candidate_request(
                candidate_id=candidate_id,
                operation="DELETE",
                request=lambda candidate: iot_request(
                    path_ble_schedule_delete,
                    build_mesh_schedule_delete_body(
                        candidate,
                        schedule_ids=schedule_ids,
                    ),
                ),
            )
            for candidate_id in candidate_ids
        )
    )
    for succeeded, _, error in batch_results:
        if succeeded:
            any_deleted = True
            continue
        last_error = _remember_last_error(last_error, error)
    return any_deleted, last_error


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

    for batch in _iter_candidate_batches(candidate_device_ids):
        normalized_rows, batch_succeeded, batch_error = await _collect_schedule_rows_from_batch(
            candidate_ids=batch,
            execute_candidate_request=execute_candidate_request,
            iot_request=iot_request,
            extract_timings_list=extract_timings_list,
            normalize_mesh_timing_rows=normalize_mesh_timing_rows,
            path_ble_schedule_get=path_ble_schedule_get,
            build_mesh_schedule_get_body=build_mesh_schedule_get_body,
        )
        any_candidate_succeeded = any_candidate_succeeded or batch_succeeded
        last_error = _remember_last_error(last_error, batch_error)
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
        succeeded, _, error = await _add_mesh_schedule_for_candidate(
            candidate_id=candidate_id,
            schedule_json=schedule_json,
            execute_candidate_request=execute_candidate_request,
            iot_request=iot_request,
            get_mesh_schedules_by_candidates_request=get_mesh_schedules_by_candidates_request,
            path_ble_schedule_add=path_ble_schedule_add,
            build_mesh_schedule_add_body=build_mesh_schedule_add_body,
        )
        if succeeded:
            return await _refresh_mesh_schedule_rows(
                candidate_device_ids=candidate_device_ids,
                get_mesh_schedules_by_candidates_request=get_mesh_schedules_by_candidates_request,
            )
        last_error = _remember_last_error(last_error, error)

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

    for batch in _iter_candidate_batches(candidate_device_ids):
        batch_deleted, batch_error = await _delete_mesh_schedule_batch(
            candidate_ids=batch,
            schedule_ids=schedule_ids,
            execute_candidate_request=execute_candidate_request,
            iot_request=iot_request,
            path_ble_schedule_delete=path_ble_schedule_delete,
            build_mesh_schedule_delete_body=build_mesh_schedule_delete_body,
        )
        any_deleted = any_deleted or batch_deleted
        last_error = _remember_last_error(last_error, batch_error)

    if any_deleted:
        return await _refresh_mesh_schedule_rows(
            candidate_device_ids=candidate_device_ids,
            get_mesh_schedules_by_candidates_request=get_mesh_schedules_by_candidates_request,
        )
    if last_error is not None:
        raise last_error
    return []
