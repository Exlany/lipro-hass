"""Misc endpoints and collaborators for the REST facade."""

from __future__ import annotations

import logging
from typing import cast

from ....const.api import PATH_GET_MQTT_CONFIG, PATH_QUERY_OUTLET_POWER
from ..diagnostics_api_service import (
    fetch_body_sensor_history as fetch_body_sensor_history_service,
    fetch_door_sensor_history as fetch_door_sensor_history_service,
    get_city as get_city_service,
    query_command_result as query_command_result_service,
    query_ota_info as query_ota_info_service,
    query_user_cloud as query_user_cloud_service,
)
from ..errors import LiproApiError
from ..mqtt_api_service import get_mqtt_config as get_mqtt_config_service
from ..power_service import (
    OutletPowerInfoResult,
    fetch_outlet_power_info as fetch_outlet_power_info_service,
)
from ..types import CommandResultApiResponse, JsonObject, MqttConfigResponse, OtaInfoRow
from .payloads import _EndpointAdapter

_LOGGER = logging.getLogger("custom_components.lipro.core.api")

type ResponseMapping = JsonObject


def _as_mqtt_config_response(payload: JsonObject) -> MqttConfigResponse:
    """Project one normalized JSON mapping onto the MQTT config response contract."""
    return cast(MqttConfigResponse, payload)


def _as_command_result_response(payload: JsonObject) -> CommandResultApiResponse:
    """Project one normalized JSON mapping onto the command-result response contract."""
    return cast(CommandResultApiResponse, payload)


class MiscEndpoints(_EndpointAdapter):
    """Focused misc endpoint collaborator for the REST facade."""

    async def get_mqtt_config(self) -> MqttConfigResponse:
        """Get MQTT configuration information."""
        return _as_mqtt_config_response(await get_mqtt_config_service(
            request_iot_mapping=self._request_iot_mapping,
            is_success_code=self._is_success_code,
            unwrap_iot_success_payload=self._unwrap_iot_success_payload,
            require_mapping_response=self._require_mapping_response,
            lipro_api_error=LiproApiError,
            path_get_mqtt_config=PATH_GET_MQTT_CONFIG,
        ))

    async def fetch_outlet_power_info(self, device_id: str) -> OutletPowerInfoResult:
        """Fetch power information for outlet devices."""
        return await fetch_outlet_power_info_service(
            normalize_power_target_id=self._normalize_power_target_id,
            iot_request=self._iot_request,
            require_mapping_response=self._require_mapping_response,
            is_invalid_param_error_code=self._is_invalid_param_error_code,
            lipro_api_error=LiproApiError,
            path_query_outlet_power=PATH_QUERY_OUTLET_POWER,
            logger=_LOGGER,
            device_id=device_id,
        )

    async def query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: int | str,
    ) -> CommandResultApiResponse:
        """Query command result status."""
        return _as_command_result_response(await query_command_result_service(
            msg_sn=msg_sn,
            device_id=device_id,
            device_type=device_type,
            request_iot_mapping=self._request_iot_mapping,
            require_mapping_response=self._require_mapping_response,
            to_device_type_hex=self._to_device_type_hex,
        ))

    async def get_city(self) -> ResponseMapping:
        """Get city information used for schedules/weather context."""
        return await get_city_service(
            iot_request=self._iot_request,
            require_mapping_response=self._require_mapping_response,
        )

    async def query_user_cloud(self) -> ResponseMapping:
        """Query cloud-assistant metadata for diagnostics."""
        return await query_user_cloud_service(
            request_iot_mapping_raw=self._request_iot_mapping_raw,
            require_mapping_response=self._require_mapping_response,
        )

    async def query_ota_info(
        self,
        device_id: str,
        device_type: int | str,
        *,
        iot_name: str | None = None,
        allow_rich_v2_fallback: bool = False,
    ) -> list[OtaInfoRow]:
        """Fetch OTA information for diagnostics."""
        return await query_ota_info_service(
            iot_request=self._iot_request,
            extract_data_list=self._extract_data_list,
            is_invalid_param_error_code=self._is_invalid_param_error_code,
            to_device_type_hex=self._to_device_type_hex,
            lipro_api_error=LiproApiError,
            device_id=device_id,
            device_type=device_type,
            iot_name=iot_name,
            allow_rich_v2_fallback=allow_rich_v2_fallback,
        )

    async def fetch_body_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> ResponseMapping:
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
    ) -> ResponseMapping:
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


__all__ = ["MiscEndpoints"]
