"""Shared payload helpers and collaborator adapters for REST endpoint families."""

from __future__ import annotations

import logging
from typing import Protocol, TypeGuard, cast

from ...utils.identifiers import (
    normalize_iot_device_id as _normalize_iot_device_id,
    normalize_mesh_group_id as _normalize_mesh_group_id,
)
from ..types import JsonObject, JsonValue, LoginResponse, ScheduleTimingRow

_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")


def _is_json_object(value: object) -> TypeGuard[JsonObject]:
    """Return whether one raw payload value is a JSON-like mapping."""
    return isinstance(value, dict)


class _AuthApiPort(Protocol):
    async def login(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> LoginResponse: ...

    async def refresh_access_token(self) -> LoginResponse: ...


class _EndpointClientPort(Protocol):
    @property
    def _auth_api(self) -> _AuthApiPort: ...

    async def smart_home_request(
        self,
        path: str,
        data: JsonObject,
        require_auth: bool = True,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> JsonValue: ...

    async def iot_request(
        self,
        path: str,
        body_data: JsonObject,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> JsonValue: ...

    async def request_iot_mapping(
        self,
        path: str,
        body_data: JsonObject,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[JsonObject, str | None]: ...

    async def request_iot_mapping_raw(
        self,
        path: str,
        body: str,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[JsonObject, str | None]: ...

    async def iot_request_with_busy_retry(
        self,
        path: str,
        body_data: JsonObject,
        *,
        target_id: str,
        command: str,
    ) -> JsonObject: ...

    def to_device_type_hex(self, device_type: int | str) -> str: ...
    def is_success_code(self, code: object) -> bool: ...
    def unwrap_iot_success_payload(self, result: JsonObject) -> JsonValue: ...
    def require_mapping_response(self, path: str, result: object) -> JsonObject: ...
    def is_invalid_param_error_code(self, code: object) -> bool: ...


class _EndpointAdapter:
    """Base adapter that delegates shared protocol operations to the facade."""

    def __init__(self, client: _EndpointClientPort) -> None:
        self._client = client
        self._auth_api = client._auth_api  # noqa: SLF001

    async def _smart_home_request(
        self,
        path: str,
        data: JsonObject,
        require_auth: bool = True,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> JsonValue:
        if require_auth is True and not is_retry and not retry_count:
            return await self._client.smart_home_request(path, data)
        return await self._client.smart_home_request(
            path,
            data,
            require_auth=require_auth,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def _iot_request(
        self,
        path: str,
        body_data: JsonObject,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> JsonValue:
        if not is_retry and not retry_count:
            return await self._client.iot_request(path, body_data)
        return await self._client.iot_request(
            path,
            body_data,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def _request_iot_mapping(
        self,
        path: str,
        body_data: JsonObject,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[JsonObject, str | None]:
        if not is_retry and not retry_count:
            return await self._client.request_iot_mapping(path, body_data)
        return await self._client.request_iot_mapping(
            path,
            body_data,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def _request_iot_mapping_raw(
        self,
        path: str,
        body: str,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[JsonObject, str | None]:
        if not is_retry and not retry_count:
            return await self._client.request_iot_mapping_raw(path, body)
        return await self._client.request_iot_mapping_raw(
            path,
            body,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def _iot_request_with_busy_retry(
        self,
        path: str,
        body_data: JsonObject,
        *,
        target_id: str,
        command: str,
    ) -> JsonObject:
        return await self._client.iot_request_with_busy_retry(
            path,
            body_data,
            target_id=target_id,
            command=command,
        )

    def _to_device_type_hex(self, device_type: int | str) -> str:
        return self._client.to_device_type_hex(device_type)

    def _is_success_code(self, code: object) -> bool:
        return self._client.is_success_code(code)

    def _unwrap_iot_success_payload(self, result: JsonObject) -> JsonValue:
        return self._client.unwrap_iot_success_payload(result)

    def _require_mapping_response(self, path: str, result: object) -> JsonObject:
        return self._client.require_mapping_response(path, result)

    def _is_invalid_param_error_code(self, code: object) -> bool:
        return self._client.is_invalid_param_error_code(code)


    @staticmethod
    def _extract_list_payload(
        result: object,
        *keys: str,
    ) -> list[JsonObject]:
        return EndpointPayloadNormalizers.extract_list_payload(result, *keys)

    @staticmethod
    def _extract_data_list(result: object) -> list[JsonObject]:
        return EndpointPayloadNormalizers.extract_data_list(result)

    @staticmethod
    def _extract_timings_list(result: object) -> list[ScheduleTimingRow]:
        return EndpointPayloadNormalizers.extract_timings_list(result)

    @staticmethod
    def _sanitize_iot_device_ids(
        device_ids: list[str],
        *,
        endpoint: str,
    ) -> list[str]:
        return EndpointPayloadNormalizers.sanitize_iot_device_ids(
            device_ids,
            endpoint=endpoint,
        )

    @staticmethod
    def _normalize_power_target_id(device_id: object) -> str | None:
        return EndpointPayloadNormalizers.normalize_power_target_id(device_id)


class EndpointPayloadNormalizers:
    """Explicit payload-normalizer collaborator for endpoint families."""

    @staticmethod
    def extract_list_payload(
        result: object,
        *keys: str,
    ) -> list[JsonObject]:
        """Extract a filtered list payload from one response object."""
        if isinstance(result, list):
            return [row for row in result if _is_json_object(row)]
        if isinstance(result, dict):
            for key in keys:
                value = result.get(key)
                if isinstance(value, list):
                    return [row for row in value if _is_json_object(row)]
        return []

    @staticmethod
    def extract_data_list(result: object) -> list[JsonObject]:
        """Extract the canonical ``data`` list payload from one response object."""
        return EndpointPayloadNormalizers.extract_list_payload(result, "data")

    @staticmethod
    def extract_timings_list(result: object) -> list[ScheduleTimingRow]:
        """Extract schedule timing rows from timing- or data-shaped payloads."""
        return [
            cast(ScheduleTimingRow, row)
            for row in EndpointPayloadNormalizers.extract_list_payload(
                result, "timings", "data"
            )
        ]

    @staticmethod
    def sanitize_iot_device_ids(
        device_ids: list[str],
        *,
        endpoint: str,
    ) -> list[str]:
        """Filter, normalize, and de-duplicate IoT device identifiers."""
        valid_ids: list[str] = []
        seen: set[str] = set()
        skipped = 0
        for raw_id in device_ids:
            normalized = _normalize_iot_device_id(raw_id)
            if normalized is None:
                skipped += 1
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            valid_ids.append(normalized)

        if skipped:
            _LOGGER.debug(
                "Skipped %d non-IoT IDs for %s",
                skipped,
                endpoint,
            )
        return valid_ids

    @staticmethod
    def normalize_power_target_id(device_id: object) -> str | None:
        """Normalize one power target into an IoT or mesh-group identifier."""
        return _normalize_iot_device_id(device_id) or _normalize_mesh_group_id(
            device_id
        )


__all__ = ["EndpointPayloadNormalizers"]
