"""Status/query endpoints for LiproClient."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ....const.api import (
    ERROR_DEVICE_NOT_CONNECTED,
    ERROR_DEVICE_NOT_CONNECTED_STR,
    ERROR_DEVICE_NOT_FOUND,
    ERROR_DEVICE_NOT_FOUND_STR,
    ERROR_DEVICE_OFFLINE,
    ERROR_DEVICE_OFFLINE_LEGACY,
    ERROR_DEVICE_OFFLINE_LEGACY_STR,
    ERROR_DEVICE_OFFLINE_STR,
    ERROR_DEVICE_UPDATING,
    ERROR_DEVICE_UPDATING_STR,
    ERROR_NO_PERMISSION,
    ERROR_NO_PERMISSION_STR,
    MAX_DEVICES_PER_QUERY,
    PATH_QUERY_CONNECT_STATUS,
    PATH_QUERY_DEVICE_STATUS,
    PATH_QUERY_MESH_GROUP_STATUS,
)
from .. import response_safety as _response_safety
from ..errors import LiproApiError
from ..status_service import (
    query_connect_status as query_connect_status_service,
    query_device_status as query_device_status_service,
    query_mesh_group_status as query_mesh_group_status_service,
)
from ..types import DeviceStatusItem
from .connect_status import coerce_connect_status
from .payloads import _ClientEndpointPayloadsMixin

if TYPE_CHECKING:
    from collections.abc import Callable


# Use the same logger instance as custom_components.lipro.core.api.client._LOGGER
# so tests patching client._LOGGER.* still intercept logs here.
_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")

_BATCH_FALLBACK_EXPECTED_OFFLINE_CODES = (
    ERROR_DEVICE_OFFLINE,
    ERROR_DEVICE_OFFLINE_STR,
    ERROR_DEVICE_OFFLINE_LEGACY,
    ERROR_DEVICE_OFFLINE_LEGACY_STR,
    ERROR_DEVICE_NOT_FOUND,
    ERROR_DEVICE_NOT_FOUND_STR,
)


class _ClientStatusEndpointsMixin(_ClientEndpointPayloadsMixin):
    """Endpoints: status queries."""

    @staticmethod
    def _is_retriable_device_error(err: Exception) -> bool:
        """Return True when error should trigger per-device fallback retries."""
        normalized = _response_safety.normalize_response_code(
            getattr(err, "code", None)
        )
        return normalized in (
            ERROR_DEVICE_OFFLINE,
            ERROR_DEVICE_OFFLINE_STR,
            ERROR_DEVICE_OFFLINE_LEGACY,
            ERROR_DEVICE_OFFLINE_LEGACY_STR,
            ERROR_DEVICE_NOT_CONNECTED,
            ERROR_DEVICE_NOT_CONNECTED_STR,
            ERROR_DEVICE_NOT_FOUND,
            ERROR_DEVICE_NOT_FOUND_STR,
            ERROR_DEVICE_UPDATING,
            ERROR_DEVICE_UPDATING_STR,
            ERROR_NO_PERMISSION,
            ERROR_NO_PERMISSION_STR,
        )

    async def query_device_status(
        self,
        device_ids: list[str],
        *,
        max_devices_per_query: int = MAX_DEVICES_PER_QUERY,
        on_batch_metric: Callable[[int, float, int], None] | None = None,
    ) -> list[DeviceStatusItem]:
        """Query status of multiple devices.

        Returns:
            List of device status items
        """
        return await query_device_status_service(
            device_ids=device_ids,
            max_devices_per_query=max_devices_per_query,
            iot_request=self._iot_request,
            extract_data_list=self._extract_data_list,
            is_retriable_device_error=self._is_retriable_device_error,
            lipro_api_error=LiproApiError,
            normalize_response_code=_response_safety.normalize_response_code,
            expected_offline_codes=_BATCH_FALLBACK_EXPECTED_OFFLINE_CODES,
            logger=_LOGGER,
            path_query_device_status=PATH_QUERY_DEVICE_STATUS,
            on_batch_metric=on_batch_metric,
        )  # type: ignore[return-value]

    async def query_mesh_group_status(
        self, group_ids: list[str]
    ) -> list[dict[str, Any]]:
        """Query status of mesh groups."""
        return await query_mesh_group_status_service(
            group_ids=group_ids,
            iot_request=self._iot_request,
            extract_data_list=self._extract_data_list,
            is_retriable_device_error=self._is_retriable_device_error,
            lipro_api_error=LiproApiError,
            normalize_response_code=_response_safety.normalize_response_code,
            expected_offline_codes=_BATCH_FALLBACK_EXPECTED_OFFLINE_CODES,
            logger=_LOGGER,
            path_query_mesh_group_status=PATH_QUERY_MESH_GROUP_STATUS,
        )

    async def query_connect_status(self, device_ids: list[str]) -> dict[str, bool]:
        """Query real-time connection status for devices."""
        return await query_connect_status_service(
            device_ids=device_ids,
            iot_request=self._iot_request,
            sanitize_iot_device_ids=self._sanitize_iot_device_ids,
            path_query_connect_status=PATH_QUERY_CONNECT_STATUS,
            coerce_connect_status=coerce_connect_status,
            lipro_api_error=LiproApiError,
            logger=_LOGGER,
        )


__all__ = ["_ClientStatusEndpointsMixin"]
