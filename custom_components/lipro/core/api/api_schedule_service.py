"""Schedule endpoint service for Lipro API client."""
# ruff: noqa: SLF001

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, cast

from ...const.api import PATH_SCHEDULE_ADD, PATH_SCHEDULE_DELETE, PATH_SCHEDULE_GET
from .schedule_endpoint import (
    build_schedule_add_body,
    build_schedule_delete_body,
    build_schedule_get_body,
)

_MESH_SCHEDULE_CANDIDATE_CONCURRENCY = 3


async def execute_mesh_schedule_candidate_request(
    *,
    candidate_id: str,
    operation: str,
    request: Callable[[str], Awaitable[Any]],
    lipro_auth_error: type[Exception],
    lipro_api_error: type[Exception],
    logger: Any,
) -> tuple[bool, Any, Exception | None]:
    """Execute one mesh schedule candidate request with shared error handling."""
    try:
        return True, await request(candidate_id), None
    except lipro_auth_error:
        raise
    except lipro_api_error as err:
        logger.debug(
            "Mesh schedule %s failed for %s: %s (code=%s)",
            operation,
            candidate_id,
            err,
            getattr(err, "code", None),
        )
        return False, None, err


async def get_mesh_schedules_by_candidates(
    *,
    candidate_device_ids: list[str],
    execute_candidate_request: Callable[
        ..., Awaitable[tuple[bool, Any, Exception | None]]
    ],
    iot_request: Callable[[str, dict[str, Any]], Awaitable[Any]],
    extract_timings_list: Callable[[Any], list[dict[str, Any]]],
    normalize_mesh_timing_rows: Callable[..., list[dict[str, Any]]],
    path_ble_schedule_get: str,
    build_mesh_schedule_get_body: Callable[[str], dict[str, Any]],
    raise_on_total_failure: bool = True,
) -> list[dict[str, Any]]:
    """Query mesh schedule list from candidate device IDs."""
    if not candidate_device_ids:
        return []

    last_error: Exception | None = None
    has_successful_call = False

    for start in range(
        0,
        len(candidate_device_ids),
        _MESH_SCHEDULE_CANDIDATE_CONCURRENCY,
    ):
        batch = candidate_device_ids[
            start : start + _MESH_SCHEDULE_CANDIDATE_CONCURRENCY
        ]

        async def _run_candidate(
            candidate_id: str,
        ) -> tuple[str, tuple[bool, Any, Exception | None]]:
            result = await execute_candidate_request(
                candidate_id=candidate_id,
                operation="GET",
                request=lambda candidate: iot_request(
                    path_ble_schedule_get,
                    build_mesh_schedule_get_body(candidate),
                ),
            )
            return candidate_id, result

        tasks = [
            asyncio.create_task(_run_candidate(candidate_id)) for candidate_id in batch
        ]
        for completed in asyncio.as_completed(tasks):
            candidate_id, (ok, result, err) = await completed
            if not ok:
                if err is not None:
                    last_error = err
                continue

            has_successful_call = True
            rows = extract_timings_list(result)
            normalized_rows = normalize_mesh_timing_rows(
                rows,
                fallback_device_id=candidate_id,
            )
            if not normalized_rows:
                continue

            for task in tasks:
                if task.done():
                    continue
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            return normalized_rows

    if has_successful_call:
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
    execute_candidate_request: Callable[
        ..., Awaitable[tuple[bool, Any, Exception | None]]
    ],
    iot_request: Callable[[str, dict[str, Any]], Awaitable[Any]],
    get_mesh_schedules_by_candidates_request: Callable[
        ..., Awaitable[list[dict[str, Any]]]
    ],
    path_ble_schedule_add: str,
    build_mesh_schedule_add_body: Callable[..., dict[str, Any]],
    encode_mesh_schedule_json: Callable[[list[int], list[int], list[int]], str],
) -> list[dict[str, Any]]:
    """Try mesh schedule add across candidates and return refreshed schedule rows."""
    schedule_json = encode_mesh_schedule_json(days, times, events)
    last_error: Exception | None = None

    for candidate_id in candidate_device_ids:
        ok, _, err = await execute_candidate_request(
            candidate_id=candidate_id,
            operation="ADD",
            request=lambda candidate: iot_request(
                path_ble_schedule_add,
                build_mesh_schedule_add_body(candidate, schedule_json=schedule_json),
            ),
        )
        if ok:
            return await get_mesh_schedules_by_candidates_request(
                candidate_device_ids,
                raise_on_total_failure=False,
            )
        if err is not None:
            last_error = err

    if last_error is not None:
        raise last_error
    return []


async def delete_mesh_schedules_by_candidates(
    *,
    candidate_device_ids: list[str],
    schedule_ids: list[int],
    execute_candidate_request: Callable[
        ..., Awaitable[tuple[bool, Any, Exception | None]]
    ],
    iot_request: Callable[[str, dict[str, Any]], Awaitable[Any]],
    get_mesh_schedules_by_candidates_request: Callable[
        ..., Awaitable[list[dict[str, Any]]]
    ],
    path_ble_schedule_delete: str,
    build_mesh_schedule_delete_body: Callable[..., dict[str, Any]],
) -> list[dict[str, Any]]:
    """Try mesh schedule delete across candidates and return refreshed rows."""
    deleted = False
    last_error: Exception | None = None

    for start in range(
        0,
        len(candidate_device_ids),
        _MESH_SCHEDULE_CANDIDATE_CONCURRENCY,
    ):
        batch = candidate_device_ids[
            start : start + _MESH_SCHEDULE_CANDIDATE_CONCURRENCY
        ]
        batch_results = await asyncio.gather(
            *(
                execute_candidate_request(
                    candidate_id=candidate_id,
                    operation="DELETE",
                    request=lambda candidate: iot_request(
                        path_ble_schedule_delete,
                        build_mesh_schedule_delete_body(
                            candidate, schedule_ids=schedule_ids
                        ),
                    ),
                )
                for candidate_id in batch
            )
        )

        for ok, _, err in batch_results:
            if ok:
                deleted = True
                continue
            if err is not None:
                last_error = err

    if deleted:
        return await get_mesh_schedules_by_candidates_request(
            candidate_device_ids,
            raise_on_total_failure=False,
        )
    if last_error is not None:
        raise last_error
    return []


class ScheduleApiService:
    """Schedule endpoints extracted from LiproClient."""

    def __init__(self, client: Any) -> None:
        """Initialize schedule endpoint service."""
        self._client = client

    async def get_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Get timing schedules for a device."""
        candidate_ids, device_type_hex = self._client._resolve_schedule_request_context(
            device_id=device_id,
            device_type=device_type,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )
        ble_candidate_ids = self._client._resolve_ble_schedule_candidate_ids(
            device_id=device_id,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )
        mesh_request = self._client._get_mesh_schedules_by_candidates
        result = await self._client._execute_schedule_operation(
            device_id=device_id,
            candidate_ids=candidate_ids,
            ble_candidate_ids=ble_candidate_ids,
            ble_operation="GET",
            ble_request=mesh_request,
            mesh_request=mesh_request,
            standard_request=lambda: self._client._request_schedule_timings(
                PATH_SCHEDULE_GET,
                build_schedule_get_body(device_id, device_type_hex=device_type_hex),
            ),
        )
        return cast(list[dict[str, Any]], result)

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
    ) -> list[dict[str, Any]]:
        """Add or update a timing schedule for a device."""
        if len(times) != len(events):
            msg = "times and events arrays must have the same length"
            raise ValueError(msg)

        candidate_ids, device_type_hex = self._client._resolve_schedule_request_context(
            device_id=device_id,
            device_type=device_type,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )
        ble_candidate_ids = self._client._resolve_ble_schedule_candidate_ids(
            device_id=device_id,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

        async def _mesh_add_request(ids: list[str]) -> list[dict[str, Any]]:
            raw = await self._client._add_mesh_schedule_by_candidates(
                ids,
                days=days,
                times=times,
                events=events,
            )
            return cast(list[dict[str, Any]], raw)

        result = await self._client._execute_schedule_operation(
            device_id=device_id,
            candidate_ids=candidate_ids,
            ble_candidate_ids=ble_candidate_ids,
            ble_operation="ADD",
            ble_request=_mesh_add_request,
            mesh_request=_mesh_add_request,
            standard_request=lambda: self._client._request_schedule_timings(
                PATH_SCHEDULE_ADD,
                build_schedule_add_body(
                    device_id,
                    device_type_hex=device_type_hex,
                    days=days,
                    times=times,
                    events=events,
                    group_id=group_id,
                ),
            ),
        )
        return cast(list[dict[str, Any]], result)

    async def delete_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        schedule_ids: list[int],
        group_id: str = "",
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Delete timing schedules for a device."""
        candidate_ids, device_type_hex = self._client._resolve_schedule_request_context(
            device_id=device_id,
            device_type=device_type,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )
        ble_candidate_ids = self._client._resolve_ble_schedule_candidate_ids(
            device_id=device_id,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

        async def _mesh_delete_request(ids: list[str]) -> list[dict[str, Any]]:
            raw = await self._client._delete_mesh_schedules_by_candidates(
                ids,
                schedule_ids=schedule_ids,
            )
            return cast(list[dict[str, Any]], raw)

        result = await self._client._execute_schedule_operation(
            device_id=device_id,
            candidate_ids=candidate_ids,
            ble_candidate_ids=ble_candidate_ids,
            ble_operation="DELETE",
            ble_request=_mesh_delete_request,
            mesh_request=_mesh_delete_request,
            standard_request=lambda: self._client._request_schedule_timings(
                PATH_SCHEDULE_DELETE,
                build_schedule_delete_body(
                    device_id,
                    device_type_hex=device_type_hex,
                    schedule_ids=schedule_ids,
                    group_id=group_id,
                ),
            ),
        )
        return cast(list[dict[str, Any]], result)
