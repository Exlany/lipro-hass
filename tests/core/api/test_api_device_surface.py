"""Topicized API regression coverage extracted from `tests/core/api/test_api.py` (test_api_device_surface)."""

from __future__ import annotations

from .test_api import (
    PATH_FETCH_BODY_SENSOR_HISTORY,
    PATH_FETCH_DOOR_SENSOR_HISTORY,
    PATH_GET_CITY,
    PATH_QUERY_COMMAND_RESULT,
    PATH_QUERY_CONNECT_STATUS,
    PATH_QUERY_CONTROLLER_OTA,
    PATH_QUERY_OTA_INFO,
    PATH_QUERY_OTA_INFO_V2,
    PATH_QUERY_OUTLET_POWER,
    PATH_QUERY_USER_CLOUD,
    AsyncMock,
    LiproApiError,
    LiproRestFacade,
    patch,
    pytest,
)


class TestLiproRestFacadeDevices:
    """Tests for device-related API calls."""

    @pytest.mark.asyncio
    async def test_get_devices(self):
        """Test getting devices."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        mock_response = {
            "code": 0,
            "value": {
                "devices": [
                    {"deviceId": 1, "deviceName": "Light 1"},
                    {"deviceId": 2, "deviceName": "Light 2"},
                ],
            },
        }

        with patch.object(
            client, "_smart_home_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response["value"]

            result = await client.get_devices(offset=0, limit=100)

            assert "devices" in result
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_device_status_empty(self):
        """Test querying status with empty device list."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        result = await client.query_device_status([])

        assert result == []


class TestLiproRestFacadeDeviceStatus:
    """Tests for device status queries."""

    @pytest.mark.asyncio
    async def test_query_device_status_success(self):
        """Test querying device status successfully."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        mock_result = [
            {"deviceId": "03ab5ccd7cxxxxxx", "powerState": "1"},
            {"deviceId": "03ab5ccd7cyyyyyy", "powerState": "0"},
        ]

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_result

            result = await client.query_device_status(
                ["03ab5ccd7cxxxxxx", "03ab5ccd7cyyyyyy"]
            )

            assert len(result) == 2
            assert result[0]["deviceId"] == "03ab5ccd7cxxxxxx"

    @pytest.mark.asyncio
    async def test_query_device_status_with_dict_response(self):
        """Test querying device status with dict response containing data key."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        mock_result = {
            "data": [
                {"deviceId": "03ab5ccd7cxxxxxx", "powerState": "1"},
            ]
        }

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_result

            result = await client.query_device_status(["03ab5ccd7cxxxxxx"])

            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_query_device_status_offline_fallback(self):
        """Test fallback to individual queries when batch fails with 140003."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        call_count = 0

        async def mock_request(path, body):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First batch call fails
                raise LiproApiError("Device offline", 140003)
            # Individual calls succeed
            device_id = body["deviceIdList"][0]
            return [{"deviceId": device_id, "powerState": "1"}]

        with patch.object(client, "_iot_request", side_effect=mock_request):
            result = await client.query_device_status(
                ["03ab5ccd7cxxxxxx", "03ab5ccd7cyyyyyy"]
            )

            # Should have results from individual queries
            assert len(result) == 2
            # First call (batch) + 2 individual calls
            assert call_count == 3

    @pytest.mark.asyncio
    async def test_query_device_status_140003_fallback_logs_debug_not_warning(self):
        """Expected 140003 fallback should not emit warning-level noise."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        call_count = 0

        async def mock_request(path, body):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise LiproApiError("Device offline", 140003)
            return [{"deviceId": body["deviceIdList"][0], "powerState": "1"}]

        with (
            patch.object(client, "_iot_request", side_effect=mock_request),
            patch(
                "custom_components.lipro.core.api.client._LOGGER.warning"
            ) as mock_warning,
            patch(
                "custom_components.lipro.core.api.client._LOGGER.debug"
            ) as mock_debug,
        ):
            result = await client.query_device_status(["03ab5ccd7cxxxxxx"])

        assert len(result) == 1
        mock_warning.assert_not_called()
        assert mock_debug.call_count >= 1

    @pytest.mark.asyncio
    async def test_query_device_status_other_error_raises(self):
        """Test that non-140003 errors are re-raised."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = LiproApiError("Server error", 500)

            with pytest.raises(LiproApiError, match="Server error"):
                await client.query_device_status(["03ab5ccd7cxxxxxx"])

    @pytest.mark.asyncio
    async def test_query_device_status_retriable_warning_logs_error_code_and_endpoint(
        self,
    ):
        """Retriable non-offline fallback warning should include code and endpoint."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        call_count = 0

        async def mock_request(path, body):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise LiproApiError("Device updating", 140014)
            return [{"deviceId": body["deviceIdList"][0], "powerState": "1"}]

        with (
            patch.object(client, "_iot_request", side_effect=mock_request),
            patch(
                "custom_components.lipro.core.api.client._LOGGER.warning"
            ) as mock_warning,
        ):
            result = await client.query_device_status(["03ab5ccd7cxxxxxx"])

        assert len(result) == 1
        assert any(
            "endpoint=%s" in str(call.args[0])
            and call.args[2] == 140014
            and call.args[3] == "/app/oauth/api/v1/user/query/devices/state.do"
            for call in mock_warning.call_args_list
        )


class TestLiproRestFacadeMeshGroupStatus:
    """Tests for mesh group status queries."""

    @pytest.mark.asyncio
    async def test_query_mesh_group_status_empty(self):
        """Test querying status with empty group list."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        result = await client.query_mesh_group_status([])

        assert result == []

    @pytest.mark.asyncio
    async def test_query_mesh_group_status_success(self):
        """Test querying mesh group status successfully."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        mock_result = [
            {"groupId": "mesh_group_10001", "powerState": "1"},
        ]

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_result

            result = await client.query_mesh_group_status(["mesh_group_10001"])

            assert len(result) == 1
            assert result[0]["groupId"] == "mesh_group_10001"

    @pytest.mark.asyncio
    async def test_query_mesh_group_status_non_list_response(self):
        """Test querying mesh group status with non-list response."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"status": "ok"}  # Not a list

            result = await client.query_mesh_group_status(["mesh_group_10001"])

            assert result == []

    @pytest.mark.asyncio
    async def test_query_mesh_group_status_offline_fallback(self):
        """Test fallback to individual queries when batch fails with 140003."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        call_count = 0

        async def mock_request(path, body):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise LiproApiError("Device offline", 140003)
            group_id = body["groupIdList"][0]
            return [{"groupId": group_id, "powerState": "1"}]

        with patch.object(client, "_iot_request", side_effect=mock_request):
            result = await client.query_mesh_group_status(
                ["mesh_group_10001", "mesh_group_10002"]
            )

            assert len(result) == 2
            assert call_count == 3


class TestLiproRestFacadeConnectStatus:
    """Tests for connection-status parsing."""

    @pytest.mark.asyncio
    async def test_query_connect_status_coerces_backend_variants(self):
        """Bool/int/string variants should be normalized to bool."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {
                "dev_bool_true": True,
                "dev_bool_false": False,
                "dev_int_one": 1,
                "dev_int_zero": 0,
                "dev_str_one": "1",
                "dev_str_zero": "0",
                "dev_str_true": "true",
                "dev_str_false": "false",
                "dev_yes": "yes",
                "dev_off": "off",
            }

            result = await client.query_connect_status(["03ab5ccd7caaaaaa"])

        assert result == {
            "dev_bool_true": True,
            "dev_bool_false": False,
            "dev_int_one": True,
            "dev_int_zero": False,
            "dev_str_one": True,
            "dev_str_zero": False,
            "dev_str_true": True,
            "dev_str_false": False,
            "dev_yes": True,
            "dev_off": False,
        }

    @pytest.mark.asyncio
    async def test_query_connect_status_non_dict_response_returns_empty(self):
        """Non-dict API payload should be ignored safely."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = []
            result = await client.query_connect_status(["03ab5ccd7caaaaaa"])

        assert result == {}

    @pytest.mark.asyncio
    async def test_query_connect_status_unknown_values_default_to_false(self):
        """Unknown backend variants should be treated as offline."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {
                "dev_unknown_str": "offline",
                "dev_unknown_obj": {"status": "up"},
                "dev_none": None,
            }

            result = await client.query_connect_status(["03ab5ccd7caaaaaa"])

        assert result == {
            "dev_unknown_str": False,
            "dev_unknown_obj": False,
            "dev_none": False,
        }

    @pytest.mark.asyncio
    async def test_query_connect_status_ignores_wrapped_payload(self):
        """Wrapped payload should not be interpreted as device-status map."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {
                "code": "0000",
                "data": {},
                "message": "success",
                "success": True,
            }
            result = await client.query_connect_status(["03ab5ccd7caaaaaa"])

        assert result == {}

    @pytest.mark.asyncio
    async def test_query_connect_status_filters_invalid_ids(self):
        """Non-IoT IDs should be filtered out before API request."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"03ab5ccd7cabcdef": "1"}
            result = await client.query_connect_status(
                [
                    "03AB5CCD7CABCDEF",
                    "mesh_group_10001",
                    "bad/dev",
                    "03ab5ccd7cabcdef",
                ]
            )

        mock_request.assert_called_once_with(
            PATH_QUERY_CONNECT_STATUS,
            {"deviceIdList": ["03ab5ccd7cabcdef"]},
        )
        assert result == {"03ab5ccd7cabcdef": True}

    @pytest.mark.asyncio
    async def test_query_connect_status_all_invalid_ids_short_circuit(self):
        """All invalid IDs should return empty result without API call."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            result = await client.query_connect_status(["mesh_group_1", "bad/dev"])

        mock_request.assert_not_called()
        assert result == {}


class TestLiproRestFacadeOutletPower:
    """Tests for outlet power-info queries."""

    @pytest.mark.asyncio
    async def test_fetch_outlet_power_info_filters_invalid_ids(self):
        """Power-info should skip invalid IDs before request."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            result = await client.fetch_outlet_power_info("invalid")

        mock_request.assert_not_called()
        assert result == {}

    @pytest.mark.asyncio
    async def test_fetch_outlet_power_info_accepts_mesh_group_id(self):
        """Power-info should accept mesh-group IDs supported by the endpoint."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"nowPower": 3.2}
            result = await client.fetch_outlet_power_info("mesh_group_10001")

        mock_request.assert_called_once_with(
            PATH_QUERY_OUTLET_POWER,
            {"deviceId": "mesh_group_10001"},
        )
        assert result == {"nowPower": 3.2}

    @pytest.mark.asyncio
    async def test_fetch_outlet_power_info_normalizes_iot_ids(self):
        """Power-info should normalize valid IoT IDs before request."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"nowPower": 3.2}
            result = await client.fetch_outlet_power_info("03AB5CCD7CABCDEF")

        mock_request.assert_called_once_with(
            PATH_QUERY_OUTLET_POWER,
            {"deviceId": "03ab5ccd7cabcdef"},
        )
        assert result == {"nowPower": 3.2}

    @pytest.mark.asyncio
    async def test_fetch_outlet_power_info_invalid_param_error_returns_empty(self):
        """Endpoint-level invalid-param code should degrade to empty payload."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = LiproApiError("Invalid parameter", "100000")
            result = await client.fetch_outlet_power_info("03ab5ccd7cabcdef")

        mock_request.assert_called_once()
        assert result == {}

    @pytest.mark.asyncio
    async def test_fetch_outlet_power_info_other_api_error_raises(self):
        """Non-invalid-param API errors should still bubble up."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = LiproApiError("Server error", 500)
            with pytest.raises(LiproApiError, match="Server error"):
                await client.fetch_outlet_power_info("03ab5ccd7cabcdef")


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
