"""Schedule-related endpoints and helpers for the formal REST facade."""

from __future__ import annotations

from collections.abc import Sequence
import logging
from typing import Any, cast

from ....const.api import (
    PATH_BLE_SCHEDULE_ADD,
    PATH_BLE_SCHEDULE_DELETE,
    PATH_BLE_SCHEDULE_GET,
    PATH_SCHEDULE_ADD,
    PATH_SCHEDULE_DELETE,
    PATH_SCHEDULE_GET,
)
from ...utils.identifiers import normalize_iot_device_id as _normalize_iot_device_id
from .. import response_safety as _response_safety
from ..errors import LiproApiError, LiproAuthError
from ..schedule_codec import (
    coerce_int_list as _coerce_schedule_int_list,
    normalize_mesh_timing_rows as _normalize_mesh_schedule_rows,
    parse_mesh_schedule_json as _parse_mesh_schedule_payload,
)
from ..schedule_endpoint import (
    build_mesh_schedule_add_body,
    build_mesh_schedule_delete_body,
    build_mesh_schedule_get_body,
    build_schedule_add_body,
    build_schedule_delete_body,
    build_schedule_get_body,
    encode_mesh_schedule_json,
    is_mesh_group_id,
    resolve_mesh_schedule_candidate_ids,
)
from ..schedule_service import (
    CandidateRequest,
    CandidateRequestResult,
    ScheduleRequestBody,
    ScheduleRows,
    add_mesh_schedule_by_candidates as add_mesh_schedule_by_candidates_service,
    delete_mesh_schedules_by_candidates as delete_mesh_schedules_by_candidates_service,
    execute_mesh_schedule_candidate_request as execute_mesh_schedule_candidate_request_service,
    get_mesh_schedules_by_candidates as get_mesh_schedules_by_candidates_service,
)
from .connect_status import coerce_connect_status
from .payloads import _EndpointAdapter

# Use the same logger instance as custom_components.lipro.core.api.client._LOGGER
# so tests patching client._LOGGER.* still intercept logs here.
_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")


class ScheduleEndpoints(_EndpointAdapter):
    """Legacy schedule helper mixin retained for focused helper coverage."""

    @staticmethod
    def _is_mesh_group_id(device_id: str) -> bool:
        """Check whether the identifier is a mesh-group ID."""
        return is_mesh_group_id(device_id)

    @classmethod
    def _resolve_mesh_schedule_candidate_ids(
        cls,
        device_id: str,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[str]:
        """Resolve candidate IoT device IDs for mesh schedule APIs."""
        return resolve_mesh_schedule_candidate_ids(
            device_id,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
            normalize_iot_device_id=_normalize_iot_device_id,
        )

    def _require_mesh_schedule_candidate_ids(
        self,
        *,
        device_id: str,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[str]:
        """Resolve mesh schedule candidate IoT IDs or raise a clear error."""
        candidate_ids = self._resolve_ble_schedule_candidate_ids(
            device_id=device_id,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )
        if candidate_ids:
            return candidate_ids

        msg = "Mesh schedule candidate IoT IDs unavailable; refresh device status and try again"
        raise LiproApiError(msg, code="mesh_schedule_candidates_unavailable")

    async def _schedule_iot_request(
        self,
        path: str,
        body: ScheduleRequestBody,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> object:
        """Execute one typed schedule IoT request through shared transport."""
        request_body = cast(dict[str, Any], body)
        if is_retry or retry_count:
            return await self._iot_request(
                path,
                request_body,
                is_retry=is_retry,
                retry_count=retry_count,
            )
        return await self._iot_request(path, request_body)

    def _extract_schedule_timing_rows(self, result: object) -> ScheduleRows:
        """Extract raw timing rows for schedule-service helpers."""
        return self._extract_timings_list(result)

    async def _request_schedule_timings(
        self,
        path: str,
        body: ScheduleRequestBody,
    ) -> ScheduleRows:
        """Request schedule endpoint and normalize timings-list payload variants."""
        result = await self._schedule_iot_request(path, body)
        return self._extract_schedule_timing_rows(result)

    @staticmethod
    def _coerce_int_list(value: object) -> list[int]:
        """Convert mixed list payloads into a clean integer list."""
        return _coerce_schedule_int_list(value)

    @classmethod
    def _parse_mesh_schedule_json(cls, schedule_json: object) -> dict[str, list[int]]:
        """Parse mesh ``scheduleJson`` into ``days/time/evt`` arrays."""
        return _parse_mesh_schedule_payload(
            schedule_json,
            mask_sensitive_data=_response_safety.mask_sensitive_data,
        )

    @classmethod
    def _normalize_mesh_timing_rows(
        cls,
        rows: Sequence[object],
        *,
        fallback_device_id: str = "",
    ) -> ScheduleRows:
        """Normalize mesh timing rows to include ``schedule`` dict payload."""
        return _normalize_mesh_schedule_rows(
            list(rows),
            fallback_device_id=fallback_device_id,
            parse_schedule_json=cls._parse_mesh_schedule_json,
            coerce_connect_status=coerce_connect_status,
        )

    @staticmethod
    def coerce_int_list(value: object) -> list[int]:
        """Convert mixed list payloads into a clean integer list."""
        return _coerce_schedule_int_list(value)

    @classmethod
    def parse_mesh_schedule_json(cls, schedule_json: object) -> dict[str, list[int]]:
        """Parse mesh ``scheduleJson`` into canonical ``days/time/evt`` arrays."""
        return _parse_mesh_schedule_payload(
            schedule_json,
            mask_sensitive_data=_response_safety.mask_sensitive_data,
        )

    @classmethod
    def normalize_mesh_timing_rows(
        cls,
        rows: Sequence[object],
        *,
        fallback_device_id: str = "",
    ) -> ScheduleRows:
        """Normalize mesh timing rows into schedule-aware dictionaries."""
        return _normalize_mesh_schedule_rows(
            list(rows),
            fallback_device_id=fallback_device_id,
            parse_schedule_json=cls.parse_mesh_schedule_json,
            coerce_connect_status=coerce_connect_status,
        )

    async def _execute_mesh_schedule_candidate_request(
        self,
        *,
        candidate_id: str,
        operation: str,
        request: CandidateRequest,
    ) -> CandidateRequestResult:
        """Execute one mesh schedule candidate request with shared error handling."""
        return await execute_mesh_schedule_candidate_request_service(
            candidate_id=candidate_id,
            operation=operation,
            request=request,
            lipro_auth_error=LiproAuthError,
            lipro_api_error=LiproApiError,
            logger=_LOGGER,
        )

    async def _get_mesh_schedules_by_candidates(
        self,
        candidate_device_ids: list[str],
        raise_on_total_failure: bool = True,
    ) -> ScheduleRows:
        """Query mesh schedule list from candidate device IDs."""

        async def _typed_iot_request(
            path: str,
            body: ScheduleRequestBody,
            is_retry: bool = False,
            retry_count: int = 0,
        ) -> object:
            return await self._schedule_iot_request(
                path,
                body,
                is_retry=is_retry,
                retry_count=retry_count,
            )

        return await get_mesh_schedules_by_candidates_service(
            candidate_device_ids=candidate_device_ids,
            execute_candidate_request=self._execute_mesh_schedule_candidate_request,
            iot_request=_typed_iot_request,
            extract_timings_list=self._extract_schedule_timing_rows,
            normalize_mesh_timing_rows=self._normalize_mesh_timing_rows,
            path_ble_schedule_get=PATH_BLE_SCHEDULE_GET,
            build_mesh_schedule_get_body=build_mesh_schedule_get_body,
            raise_on_total_failure=raise_on_total_failure,
        )

    async def _add_mesh_schedule_by_candidates(
        self,
        candidate_device_ids: list[str],
        *,
        days: list[int],
        times: list[int],
        events: list[int],
    ) -> ScheduleRows:
        """Try mesh schedule add across candidates and return refreshed schedule rows."""

        async def _typed_iot_request(
            path: str,
            body: ScheduleRequestBody,
            is_retry: bool = False,
            retry_count: int = 0,
        ) -> object:
            return await self._schedule_iot_request(
                path,
                body,
                is_retry=is_retry,
                retry_count=retry_count,
            )

        return await add_mesh_schedule_by_candidates_service(
            candidate_device_ids=candidate_device_ids,
            days=days,
            times=times,
            events=events,
            execute_candidate_request=self._execute_mesh_schedule_candidate_request,
            iot_request=_typed_iot_request,
            get_mesh_schedules_by_candidates_request=self._get_mesh_schedules_by_candidates,
            path_ble_schedule_add=PATH_BLE_SCHEDULE_ADD,
            build_mesh_schedule_add_body=build_mesh_schedule_add_body,
            encode_mesh_schedule_json=encode_mesh_schedule_json,
        )

    def _resolve_ble_schedule_candidate_ids(
        self,
        *,
        device_id: str,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[str]:
        """Resolve candidate IoT IDs for BLE schedule APIs."""
        if self._is_mesh_group_id(device_id):
            return self._resolve_mesh_schedule_candidate_ids(
                device_id,
                mesh_gateway_id=mesh_gateway_id,
                mesh_member_ids=mesh_member_ids,
            )

        normalized = _normalize_iot_device_id(device_id)
        if normalized is None:
            return []
        return [normalized]

    async def _delete_mesh_schedules_by_candidates(
        self,
        candidate_device_ids: list[str],
        *,
        schedule_ids: list[int],
    ) -> ScheduleRows:
        """Try mesh schedule delete across candidates and return refreshed rows."""

        async def _typed_iot_request(
            path: str,
            body: ScheduleRequestBody,
            is_retry: bool = False,
            retry_count: int = 0,
        ) -> object:
            return await self._schedule_iot_request(
                path,
                body,
                is_retry=is_retry,
                retry_count=retry_count,
            )

        return await delete_mesh_schedules_by_candidates_service(
            candidate_device_ids=candidate_device_ids,
            schedule_ids=schedule_ids,
            execute_candidate_request=self._execute_mesh_schedule_candidate_request,
            iot_request=_typed_iot_request,
            get_mesh_schedules_by_candidates_request=self._get_mesh_schedules_by_candidates,
            path_ble_schedule_delete=PATH_BLE_SCHEDULE_DELETE,
            build_mesh_schedule_delete_body=build_mesh_schedule_delete_body,
        )

    async def get_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> ScheduleRows:
        """Get timing schedules for a device."""
        if self._is_mesh_group_id(device_id):
            candidate_ids = self._require_mesh_schedule_candidate_ids(
                device_id=device_id,
                mesh_gateway_id=mesh_gateway_id,
                mesh_member_ids=mesh_member_ids,
            )
            return await self._get_mesh_schedules_by_candidates(candidate_ids)

        device_type_hex = self._to_device_type_hex(device_type)
        return await self._request_schedule_timings(
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
        if self._is_mesh_group_id(device_id):
            candidate_ids = self._require_mesh_schedule_candidate_ids(
                device_id=device_id,
                mesh_gateway_id=mesh_gateway_id,
                mesh_member_ids=mesh_member_ids,
            )
            return await self._add_mesh_schedule_by_candidates(
                candidate_ids,
                days=days,
                times=times,
                events=events,
            )

        device_type_hex = self._to_device_type_hex(device_type)
        return await self._request_schedule_timings(
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
        if self._is_mesh_group_id(device_id):
            candidate_ids = self._require_mesh_schedule_candidate_ids(
                device_id=device_id,
                mesh_gateway_id=mesh_gateway_id,
                mesh_member_ids=mesh_member_ids,
            )
            return await self._delete_mesh_schedules_by_candidates(
                candidate_ids,
                schedule_ids=schedule_ids,
            )

        device_type_hex = self._to_device_type_hex(device_type)
        return await self._request_schedule_timings(
            PATH_SCHEDULE_DELETE,
            build_schedule_delete_body(
                device_id,
                device_type_hex=device_type_hex,
                schedule_ids=schedule_ids,
                group_id=group_id,
            ),
        )




__all__ = ["ScheduleEndpoints"]
