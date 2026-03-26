"""Optional-capability API surface regressions."""
from __future__ import annotations

from .conftest import (
    PATH_FETCH_BODY_SENSOR_HISTORY,
    PATH_FETCH_DOOR_SENSOR_HISTORY,
    PATH_GET_CITY,
    PATH_QUERY_COMMAND_RESULT,
    PATH_QUERY_CONTROLLER_OTA,
    PATH_QUERY_OTA_INFO,
    PATH_QUERY_OTA_INFO_V2,
    PATH_QUERY_USER_CLOUD,
    AsyncMock,
    LiproRestFacade,
    patch,
    pytest,
)


class TestLiproRestFacadeOptionalCapabilities:
    """Tests for optional developer capability APIs."""

    @pytest.mark.asyncio
    async def test_query_command_result(self):
        """query_command_result should call endpoint with msgSn payload."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        success_payload = {"code": "0000", "message": "success", "success": True}

        with patch.object(
            client, "_request_iot_mapping", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = (success_payload, None)
            result = await client.query_command_result(
                msg_sn="682550445474476112",
                device_id="mesh_group_49155",
                device_type="ff000001",
            )

        assert result == success_payload
        mock_request.assert_awaited_once_with(
            PATH_QUERY_COMMAND_RESULT,
            {
                "msgSn": "682550445474476112",
                "deviceId": "mesh_group_49155",
                "deviceType": "ff000001",
            },
        )

    @pytest.mark.asyncio
    async def test_query_command_result_returns_raw_failure_mapping(self):
        """query_command_result should preserve backend business failure payload."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        failure_payload = {
            "code": "140006",
            "message": "设备未响应",
            "success": False,
        }

        with patch.object(
            client, "_request_iot_mapping", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = (failure_payload, None)
            result = await client.query_command_result(
                msg_sn="682550445474476112",
                device_id="mesh_group_49155",
                device_type="ff000001",
            )

        assert result == failure_payload
        mock_request.assert_awaited_once_with(
            PATH_QUERY_COMMAND_RESULT,
            {
                "msgSn": "682550445474476112",
                "deviceId": "mesh_group_49155",
                "deviceType": "ff000001",
            },
        )

    @pytest.mark.asyncio
    async def test_get_city(self):
        """get_city should send empty body and return mapping payload."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"province": "广东省", "city": "江门市"}
            result = await client.get_city()

        assert result == {"province": "广东省", "city": "江门市"}
        mock_request.assert_awaited_once_with(PATH_GET_CITY, {})

    @pytest.mark.asyncio
    async def test_query_user_cloud(self):
        """query_user_cloud should use the verified raw empty-body payload."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_request_iot_mapping_raw", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = ({"data": []}, "access-token")
            result = await client.query_user_cloud()

        assert result == {"data": []}
        mock_request.assert_awaited_once_with(PATH_QUERY_USER_CLOUD, "")

    @pytest.mark.asyncio
    async def test_query_ota_info(self):
        """query_ota_info should merge v1/v2 and controller OTA payloads."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        ota_v1_rows = [{"deviceType": "ff000001", "firmwareVersion": "7.10.9"}]
        controller_rows = [{"bleName": "T21JC", "version": "2.6.43"}]

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                ota_v1_rows,
                ota_v1_rows,
                controller_rows,
            ]
            result = await client.query_ota_info(
                device_id="mesh_group_49155",
                device_type="ff000001",
            )

        assert result == ota_v1_rows + controller_rows
        assert mock_request.await_count == 3
        mock_request.assert_any_await(
            PATH_QUERY_OTA_INFO,
            {"deviceId": "mesh_group_49155", "deviceType": "ff000001"},
        )
        mock_request.assert_any_await(
            PATH_QUERY_OTA_INFO_V2,
            {"deviceId": "mesh_group_49155", "deviceType": "ff000001"},
        )
        mock_request.assert_any_await(PATH_QUERY_CONTROLLER_OTA, {})

    @pytest.mark.asyncio
    async def test_query_ota_info_light_v2_fallback(self):
        """query_ota_info should probe richer v2 payload for light devices."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        ota_v2_rows = [{"deviceType": "ff000001", "firmwareVersion": "7.10.9"}]

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                [],
                [],
                ota_v2_rows,
                [],
            ]
            result = await client.query_ota_info(
                device_id="mesh_group_49155",
                device_type="ff000001",
                iot_name="21P3",
                allow_rich_v2_fallback=True,
            )

        assert result == ota_v2_rows
        mock_request.assert_any_await(
            PATH_QUERY_OTA_INFO_V2,
            {"deviceId": "mesh_group_49155", "deviceType": "ff000001"},
        )
        mock_request.assert_any_await(
            PATH_QUERY_OTA_INFO_V2,
            {
                "deviceId": "mesh_group_49155",
                "deviceType": "ff000001",
                "iotName": "21P3",
                "skuId": "",
                "hasMacRule": True,
            },
        )

    @pytest.mark.asyncio
    async def test_fetch_body_sensor_history(self):
        """fetch_body_sensor_history should follow API contract fields."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"humanSensorStateList": []}
            result = await client.fetch_body_sensor_history(
                device_id="mesh_group_49155",
                device_type="ff000001",
                sensor_device_id="03ab5ccd7c7167d8",
                mesh_type="2",
            )

        assert result == {"humanSensorStateList": []}
        mock_request.assert_awaited_once_with(
            PATH_FETCH_BODY_SENSOR_HISTORY,
            {
                "deviceId": "mesh_group_49155",
                "deviceType": "ff000001",
                "sensorDeviceId": "03ab5ccd7c7167d8",
                "meshType": "2",
            },
        )

    @pytest.mark.asyncio
    async def test_fetch_door_sensor_history(self):
        """fetch_door_sensor_history should follow API contract fields."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"doorStateList": []}
            result = await client.fetch_door_sensor_history(
                device_id="mesh_group_49155",
                device_type="ff000001",
                sensor_device_id="03ab5ccd7c7167d8",
                mesh_type="2",
            )

        assert result == {"doorStateList": []}
        mock_request.assert_awaited_once_with(
            PATH_FETCH_DOOR_SENSOR_HISTORY,
            {
                "deviceId": "mesh_group_49155",
                "deviceType": "ff000001",
                "sensorDeviceId": "03ab5ccd7c7167d8",
                "meshType": "2",
            },
        )
