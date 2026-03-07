"""Misc endpoints for LiproClient (MQTT/power/diagnostics)."""

from __future__ import annotations

import logging
from typing import Any

from ....const.api import PATH_GET_MQTT_CONFIG, PATH_QUERY_OUTLET_POWER
from ..diagnostics_service import (
    fetch_body_sensor_history as fetch_body_sensor_history_service,
    fetch_door_sensor_history as fetch_door_sensor_history_service,
    get_city as get_city_service,
    query_command_result as query_command_result_service,
    query_ota_info as query_ota_info_service,
)
from ..errors import LiproApiError
from ..mqtt_service import get_mqtt_config as get_mqtt_config_service
from ..power_service import fetch_outlet_power_info as fetch_outlet_power_info_service
from .payloads import _ClientEndpointPayloadsMixin

# Use the same logger instance as custom_components.lipro.core.api.client._LOGGER
# so tests patching client._LOGGER.* still intercept logs here.
_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")


class _ClientMiscEndpointsMixin(_ClientEndpointPayloadsMixin):
    """Endpoints: MQTT config, outlet power, and diagnostics helpers."""

    async def get_mqtt_config(self) -> dict[str, Any]:
        """Get MQTT configuration information."""
        return await get_mqtt_config_service(
            request_iot_mapping=self._request_iot_mapping,
            is_success_code=self._is_success_code,
            unwrap_iot_success_payload=self._unwrap_iot_success_payload,
            require_mapping_response=self._require_mapping_response,
            lipro_api_error=LiproApiError,
            path_get_mqtt_config=PATH_GET_MQTT_CONFIG,
        )

    async def fetch_outlet_power_info(
        self, device_ids: list[str]
    ) -> dict[str, Any]:
        """Fetch power information for outlet devices."""
        return await fetch_outlet_power_info_service(
            sanitize_iot_device_ids=self._sanitize_iot_device_ids,
            iot_request=self._iot_request,
            require_mapping_response=self._require_mapping_response,
            is_invalid_param_error_code=self._is_invalid_param_error_code,
            lipro_api_error=LiproApiError,
            path_query_outlet_power=PATH_QUERY_OUTLET_POWER,
            logger=_LOGGER,
            device_ids=device_ids,
        )

    async def query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: int | str,
    ) -> dict[str, Any]:
        """Query command result status."""
        return await query_command_result_service(
            msg_sn=msg_sn,
            device_id=device_id,
            device_type=device_type,
            iot_request=self._iot_request,
            require_mapping_response=self._require_mapping_response,
            to_device_type_hex=self._to_device_type_hex,
        )

    async def get_city(self) -> dict[str, Any]:
        """Get city information used for schedules/weather context."""
        return await get_city_service(
            iot_request=self._iot_request,
            require_mapping_response=self._require_mapping_response,
        )

    async def query_ota_info(
        self,
        device_id: str,
        device_type: int | str,
    ) -> list[dict[str, Any]]:
        """Fetch OTA information for diagnostics."""
        return await query_ota_info_service(
            iot_request=self._iot_request,
            extract_data_list=self._extract_data_list,
            is_invalid_param_error_code=self._is_invalid_param_error_code,
            to_device_type_hex=self._to_device_type_hex,
            lipro_api_error=LiproApiError,
            device_id=device_id,
            device_type=device_type,
        )

    async def fetch_body_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> dict[str, Any]:
        """Fetch body sensor history snapshot for diagnostics."""
        return await fetch_body_sensor_history_service(
            iot_request=self._iot_request,
            require_mapping_response=self._require_mapping_response,
            to_device_type_hex=self._to_device_type_hex,
            device_id=device_id,
            device_type=device_type,
            sensor_device_id=sensor_device_id,
            mesh_type=mesh_type,
        )

    async def fetch_door_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> dict[str, Any]:
        """Fetch door sensor history snapshot for diagnostics."""
        return await fetch_door_sensor_history_service(
            iot_request=self._iot_request,
            require_mapping_response=self._require_mapping_response,
            to_device_type_hex=self._to_device_type_hex,
            device_id=device_id,
            device_type=device_type,
            sensor_device_id=sensor_device_id,
            mesh_type=mesh_type,
        )


__all__ = ["_ClientMiscEndpointsMixin"]
