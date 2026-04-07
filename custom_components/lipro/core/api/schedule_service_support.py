"""Internal candidate-batch support for schedule helper services."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterator, Sequence
import logging

from .schedule_codec import next_mesh_schedule_id
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
type CandidateBatchGetResult = tuple[ScheduleRows | None, bool, Exception | None]
type DeleteBatchResult = tuple[bool, Exception | None]

_MESH_SCHEDULE_CANDIDATE_CONCURRENCY = 3
_MESH_SCHEDULE_CANDIDATE_TIMEOUT_SECONDS = 15.0


def _redact_candidate_id(candidate_id: str) -> str:
    """Redact candidate IDs for logs and task names."""
    if not candidate_id or len(candidate_id) <= 4:
        return "***"
    return f"***{candidate_id[-4:]}"


def iter_candidate_batches(
    candidate_device_ids: Sequence[str],
) -> Iterator[CandidateBatch]:
    """Yield candidate IDs in bounded-concurrency batches."""
    for start in range(0, len(candidate_device_ids), _MESH_SCHEDULE_CANDIDATE_CONCURRENCY):
        yield candidate_device_ids[start : start + _MESH_SCHEDULE_CANDIDATE_CONCURRENCY]


def remember_last_error(
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


def create_get_candidate_tasks(
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


async def drain_candidate_tasks(
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


async def collect_schedule_rows_from_batch(
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
    tasks = create_get_candidate_tasks(
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
                last_error = remember_last_error(last_error, error)
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
        await drain_candidate_tasks(tasks)

    return None, any_candidate_succeeded, last_error


async def refresh_mesh_schedule_rows(
    *,
    candidate_device_ids: Sequence[str],
    get_mesh_schedules_by_candidates_request: GetMeshSchedulesByCandidatesRequest,
) -> ScheduleRows:
    """Refresh schedule rows across the original candidate set after mutation."""
    return await get_mesh_schedules_by_candidates_request(
        candidate_device_ids=list(candidate_device_ids),
        raise_on_total_failure=False,
    )


async def add_mesh_schedule_for_candidate(
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
    schedule_id = next_mesh_schedule_id(current_rows)
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


async def delete_mesh_schedule_batch(
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
        last_error = remember_last_error(last_error, error)
    return any_deleted, last_error


__all__ = [
    'BuildMeshScheduleAddBody',
    'BuildMeshScheduleDeleteBody',
    'BuildMeshScheduleGetBody',
    'CandidateBatch',
    'CandidateRequest',
    'CandidateRequestExecutor',
    'CandidateRequestResult',
    'ExtractTimingsList',
    'GetMeshSchedulesByCandidatesRequest',
    'IotRequest',
    'NormalizeMeshTimingRows',
    'RawScheduleRows',
    'ScheduleRequestBody',
    'ScheduleRows',
    '_redact_candidate_id',
    'add_mesh_schedule_for_candidate',
    'collect_schedule_rows_from_batch',
    'create_get_candidate_tasks',
    'delete_mesh_schedule_batch',
    'drain_candidate_tasks',
    'execute_mesh_schedule_candidate_request',
    'iter_candidate_batches',
    'refresh_mesh_schedule_rows',
    'remember_last_error',
]
