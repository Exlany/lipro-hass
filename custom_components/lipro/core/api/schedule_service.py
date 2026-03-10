"""Schedule endpoint service for the Lipro API client."""
# ruff: noqa: SLF001

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
import logging
from typing import Protocol

from ...const.api import PATH_SCHEDULE_ADD, PATH_SCHEDULE_DELETE, PATH_SCHEDULE_GET
from .schedule_endpoint import (
    build_schedule_add_body,
    build_schedule_delete_body,
    build_schedule_get_body,
)
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


class ScheduleClientProtocol(Protocol):
    """Internal client operations consumed by ``ScheduleApiService``."""

    def _is_mesh_group_id(self, device_id: str) -> bool: ...

    def _require_mesh_schedule_candidate_ids(
        self,
        *,
        device_id: str,
        mesh_gateway_id: str,
        mesh_member_ids: list[str] | None,
    ) -> list[str]: ...

    async def _get_mesh_schedules_by_candidates(
        self,
        candidate_device_ids: list[str],
    ) -> ScheduleRows: ...

    def _to_device_type_hex(self, device_type: int | str) -> str: ...

    async def _request_schedule_timings(
        self,
        path: str,
        body: ScheduleRequestBody,
    ) -> ScheduleRows: ...

    async def _add_mesh_schedule_by_candidates(
        self,
        candidate_device_ids: list[str],
        *,
        days: list[int],
        times: list[int],
        events: list[int],
    ) -> ScheduleRows: ...

    async def _delete_mesh_schedules_by_candidates(
        self,
        candidate_device_ids: list[str],
        *,
        schedule_ids: list[int],
    ) -> ScheduleRows: ...


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
    except Exception as err:  # noqa: BLE001
        logger.debug(
            "Mesh schedule %s failed for %s (error=%s)",
            operation,
            _redact_candidate_id(candidate_id),
            type(err).__name__,
        )
        return False, None, err


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

    for start in range(0, len(candidate_device_ids), _MESH_SCHEDULE_CANDIDATE_CONCURRENCY):
        batch = candidate_device_ids[start : start + _MESH_SCHEDULE_CANDIDATE_CONCURRENCY]

        async def _run_candidate(candidate_id: str) -> tuple[str, CandidateRequestResult]:
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

        tasks = [
            asyncio.create_task(
                _run_candidate(candidate_id),
                name=f"lipro_mesh_schedule_get:{_redact_candidate_id(candidate_id)}",
            )
            for candidate_id in batch
        ]
        try:
            for completed in asyncio.as_completed(tasks):
                candidate_id, (succeeded, payload, error) = await completed
                if not succeeded:
                    if error is not None:
                        last_error = error
                    continue

                any_candidate_succeeded = True
                if payload is None:
                    continue
                normalized_rows = normalize_mesh_timing_rows(
                    extract_timings_list(payload),
                    fallback_device_id=candidate_id,
                )
                if normalized_rows:
                    return normalized_rows
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except asyncio.CancelledError:
                await asyncio.shield(asyncio.gather(*tasks, return_exceptions=True))
                raise

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
        current_rows = await get_mesh_schedules_by_candidates_request(
            candidate_device_ids=[candidate_id],
            raise_on_total_failure=True,
        )
        schedule_id = _next_mesh_schedule_id(current_rows)
        succeeded, _, error = await execute_candidate_request(
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
        if succeeded:
            return await get_mesh_schedules_by_candidates_request(
                candidate_device_ids=candidate_device_ids,
                raise_on_total_failure=False,
            )
        if error is not None:
            last_error = error

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

    for start in range(0, len(candidate_device_ids), _MESH_SCHEDULE_CANDIDATE_CONCURRENCY):
        batch = candidate_device_ids[start : start + _MESH_SCHEDULE_CANDIDATE_CONCURRENCY]
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
                for candidate_id in batch
            )
        )
        for succeeded, _, error in batch_results:
            if succeeded:
                any_deleted = True
            elif error is not None:
                last_error = error

    if any_deleted:
        return await get_mesh_schedules_by_candidates_request(
            candidate_device_ids=candidate_device_ids,
            raise_on_total_failure=False,
        )
    if last_error is not None:
        raise last_error
    return []


class ScheduleApiService:
    """Schedule endpoints extracted from ``LiproClient``."""

    def __init__(self, client: ScheduleClientProtocol) -> None:
        """Initialize the schedule endpoint service."""
        self._client = client

    async def get_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> ScheduleRows:
        """Get timing schedules for a device."""
        if self._client._is_mesh_group_id(device_id):
            candidate_ids = self._client._require_mesh_schedule_candidate_ids(
                device_id=device_id,
                mesh_gateway_id=mesh_gateway_id,
                mesh_member_ids=mesh_member_ids,
            )
            return await self._client._get_mesh_schedules_by_candidates(candidate_ids)

        device_type_hex = self._client._to_device_type_hex(device_type)
        return await self._client._request_schedule_timings(
            PATH_SCHEDULE_GET,
            build_schedule_get_body(device_id, device_type_hex=device_type_hex),
        )

    async def add_device_schedule(
        self,
        device_id: str,
        device_type: int | str,
        days: list[int],
        times: list[int],
        events: list[int],
        group_id: str = "",
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> ScheduleRows:
        """Add or update a timing schedule for a device."""
        if len(times) != len(events):
            msg = "times and events must have same length"
            raise ValueError(msg)
        if self._client._is_mesh_group_id(device_id):
            candidate_ids = self._client._require_mesh_schedule_candidate_ids(
                device_id=device_id,
                mesh_gateway_id=mesh_gateway_id,
                mesh_member_ids=mesh_member_ids,
            )
            return await self._client._add_mesh_schedule_by_candidates(
                candidate_ids,
                days=days,
                times=times,
                events=events,
            )

        device_type_hex = self._client._to_device_type_hex(device_type)
        return await self._client._request_schedule_timings(
            PATH_SCHEDULE_ADD,
            build_schedule_add_body(
                device_id,
                device_type_hex=device_type_hex,
                days=days,
                times=times,
                events=events,
                group_id=group_id,
            ),
        )

    async def delete_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        schedule_ids: list[int],
        group_id: str = "",
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> ScheduleRows:
        """Delete timing schedules for a device."""
        if self._client._is_mesh_group_id(device_id):
            candidate_ids = self._client._require_mesh_schedule_candidate_ids(
                device_id=device_id,
                mesh_gateway_id=mesh_gateway_id,
                mesh_member_ids=mesh_member_ids,
            )
            return await self._client._delete_mesh_schedules_by_candidates(
                candidate_ids,
                schedule_ids=schedule_ids,
            )

        device_type_hex = self._client._to_device_type_hex(device_type)
        return await self._client._request_schedule_timings(
            PATH_SCHEDULE_DELETE,
            build_schedule_delete_body(
                device_id,
                device_type_hex=device_type_hex,
                schedule_ids=schedule_ids,
                group_id=group_id,
            ),
        )
