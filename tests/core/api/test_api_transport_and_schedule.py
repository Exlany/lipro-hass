"""Topicized API regression coverage extracted from `tests/core/api/test_api.py` (test_api_transport_and_schedule)."""

from __future__ import annotations

from .test_api import (
    PATH_BLE_SCHEDULE_ADD,
    PATH_BLE_SCHEDULE_DELETE,
    PATH_BLE_SCHEDULE_GET,
    PATH_SCHEDULE_ADD,
    PATH_SCHEDULE_DELETE,
    PATH_SCHEDULE_GET,
    AsyncMock,
    LiproApiError,
    LiproAuthError,
    LiproRestFacade,
    MagicMock,
    aiohttp,
    json,
    patch,
    pytest,
)


class TestLiproRestFacadeMqtt:
    """Tests for MQTT configuration."""

    @pytest.mark.asyncio
    async def test_get_mqtt_config_direct_response(self):
        """Test getMqttConfig with real non-standard response (no code wrapper).

        Real API returns: {"accessKey": "hex64", "secretKey": "hex64"}
        without the usual {"code": "0000", "data": {...}} wrapper.
        """
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        # Simulate the real API response (no code field)
        raw_response = {
            "accessKey": "36783B02D66A07777BE171E1C241F3C52421169D555E60F09ECFE13B6E6DD73A",
            "secretKey": "8A5103E4419C495F7CD109536F621576C293B8FA0BFC2269D725A83E32F7C286",
        }

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (200, raw_response, {})

            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                result = await client.get_mqtt_config()

        assert result["accessKey"] == raw_response["accessKey"]
        assert result["secretKey"] == raw_response["secretKey"]
        assert "code" not in result

    @pytest.mark.asyncio
    async def test_get_mqtt_config_data_only_wrapper_returns_payload(self):
        """Data-only MQTT config response without code should still unwrap."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        wrapped_response = {
            "data": {
                "accessKey": "encrypted_ak",
                "secretKey": "encrypted_sk",
            },
        }

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (200, wrapped_response, {})

            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                result = await client.get_mqtt_config()

        assert result == wrapped_response["data"]

    @pytest.mark.asyncio
    async def test_get_mqtt_config_standard_wrapped_response_returns_payload(self):
        """Wrapped MQTT config responses should unwrap successful data payloads."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        wrapped_response = {
            "code": "0000",
            "data": {
                "accessKey": "encrypted_ak",
                "secretKey": "encrypted_sk",
            },
        }

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (200, wrapped_response, {})

            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                result = await client.get_mqtt_config()

        assert result == wrapped_response["data"]

    @pytest.mark.asyncio
    async def test_get_mqtt_config_non_object_response_raises_api_error(self):
        """Non-object MQTT config payload should raise LiproApiError."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (200, ["not", "an", "object"], {})

            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()

                with pytest.raises(LiproApiError, match="expected object"):
                    await client.get_mqtt_config()

    @pytest.mark.asyncio
    async def test_get_mqtt_config_401_raises_auth_error(self):
        """Test getMqttConfig raises LiproAuthError on 401."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (401, {"message": "Unauthorized"}, {})

            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()

                with pytest.raises(LiproAuthError):
                    await client.get_mqtt_config()

    @pytest.mark.asyncio
    async def test_get_mqtt_config_no_token(self):
        """Test getMqttConfig raises LiproAuthError without token."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        # No tokens set

        with pytest.raises(LiproAuthError, match="No access token"):
            await client.get_mqtt_config()


class TestLiproRestFacadeClose:
    """Tests for client cleanup."""

    @pytest.mark.asyncio
    async def test_close_clears_session(self):
        """Test close clears session reference."""
        session = MagicMock(spec=aiohttp.ClientSession)
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000", session)

        await client.close()

        # Session reference should be cleared (HA manages session lifecycle)
        assert client._session is None

    @pytest.mark.asyncio
    async def test_close_external_session(self):
        """Test close does not close HA-managed session."""
        session = MagicMock(spec=aiohttp.ClientSession)
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000", session)

        await client.close()

        # External session should not be closed by client
        session.close.assert_not_called()


class TestLiproRestFacadeSchedules:
    """Tests for schedule API response parsing."""

    @pytest.mark.asyncio
    async def test_get_device_schedules_mesh_uses_ble_endpoint_and_parses_schedule_json(
        self,
    ):
        """Mesh schedule GET should use BLE endpoint and normalize scheduleJson."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        gateway_id = "03ab0000000000a1"
        row = {
            "id": -1,
            "deviceId": gateway_id,
            "active": 1,
            "scheduleJson": '{"days":[1,2,3],"time":[28800],"evt":[0]}',
        }
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"timings": [row]}

            result = await client.get_device_schedules(
                "mesh_group_10001",
                9,
                mesh_gateway_id=gateway_id,
            )

        mock_request.assert_awaited_once_with(
            PATH_BLE_SCHEDULE_GET,
            {"deviceId": gateway_id, "deviceType": "mesh"},
        )
        assert result == [
            {
                "id": -1,
                "deviceId": gateway_id,
                "active": True,
                "scheduleJson": '{"days":[1,2,3],"time":[28800],"evt":[0]}',
                "schedule": {"days": [1, 2, 3], "time": [28800], "evt": [0]},
            }
        ]

    @pytest.mark.asyncio
    async def test_get_device_schedules_mesh_falls_back_to_member_id(self):
        """Mesh schedule GET should try member IDs when gateway has no tasks."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        gateway_id = "03ab0000000000a1"
        member_id = "03ab0000000000a2"
        row = {
            "id": 10,
            "deviceId": member_id,
            "active": True,
            "scheduleJson": '{"days":[4],"time":[36000],"evt":[1]}',
        }
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                {"timings": []},
                {"timings": [row]},
            ]

            result = await client.get_device_schedules(
                "mesh_group_10001",
                9,
                mesh_gateway_id=gateway_id,
                mesh_member_ids=[member_id],
            )

        assert len(mock_request.await_args_list) == 2
        assert mock_request.await_args_list[0].args == (
            PATH_BLE_SCHEDULE_GET,
            {"deviceId": gateway_id, "deviceType": "mesh"},
        )
        assert mock_request.await_args_list[1].args == (
            PATH_BLE_SCHEDULE_GET,
            {"deviceId": member_id, "deviceType": "mesh"},
        )
        assert result[0]["schedule"] == {"days": [4], "time": [36000], "evt": [1]}

    @pytest.mark.asyncio
    async def test_get_device_schedules_mesh_parses_canonical_schedule_json(self):
        """Mesh GET should parse verified canonical scheduleJson payloads."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        gateway_id = "03ab0000000000a1"
        row = {
            "id": 1,
            "active": True,
            "scheduleJson": '{"days":[2],"time":[86340],"evt":[1]}',
        }
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"timings": [row]}

            result = await client.get_device_schedules(
                "mesh_group_10001",
                9,
                mesh_gateway_id=gateway_id,
            )

        assert result[0]["schedule"] == {"days": [2], "time": [86340], "evt": [1]}

    @pytest.mark.asyncio
    async def test_add_device_schedule_mesh_uses_ble_endpoint(self):
        """Mesh schedule ADD should call BLE endpoint with scheduleJson payload."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        gateway_id = "03ab0000000000a1"
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                {"timings": []},
                {"msgSn": "1"},
                {"timings": []},
            ]

            result = await client.add_device_schedule(
                "mesh_group_10001",
                9,
                [1, 2, 3],
                [28800, 61200],
                [0, 1],
                mesh_gateway_id=gateway_id,
            )

        assert result == []
        assert len(mock_request.await_args_list) == 3
        assert mock_request.await_args_list[0].args == (
            PATH_BLE_SCHEDULE_GET,
            {"deviceId": gateway_id, "deviceType": "mesh"},
        )
        add_call = mock_request.await_args_list[1]
        assert add_call.args[0] == PATH_BLE_SCHEDULE_ADD
        assert add_call.args[1]["deviceId"] == gateway_id
        assert add_call.args[1]["id"] == 0
        assert add_call.args[1]["active"] is True
        assert json.loads(add_call.args[1]["scheduleJson"]) == {
            "days": [1, 2, 3],
            "time": [28800, 61200],
            "evt": [0, 1],
        }
        assert mock_request.await_args_list[2].args == (
            PATH_BLE_SCHEDULE_GET,
            {"deviceId": gateway_id, "deviceType": "mesh"},
        )

    @pytest.mark.asyncio
    async def test_add_device_schedule_mesh_uses_first_free_schedule_id(self):
        """Mesh schedule ADD should append to the first free schedule slot."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        gateway_id = "03ab0000000000a1"
        existing_rows = [
            {
                "id": 0,
                "active": True,
                "scheduleJson": '{"days":[1],"time":[28800],"evt":[0]}',
            },
            {
                "id": 2,
                "active": True,
                "scheduleJson": '{"days":[2],"time":[61200],"evt":[1]}',
            },
        ]
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                {"timings": existing_rows},
                {"msgSn": "1"},
                {"timings": []},
            ]

            await client.add_device_schedule(
                "mesh_group_10001",
                9,
                [1, 2, 3],
                [28800, 61200],
                [0, 1],
                mesh_gateway_id=gateway_id,
            )

        add_call = mock_request.await_args_list[1]
        assert add_call.args[0] == PATH_BLE_SCHEDULE_ADD
        assert add_call.args[1]["id"] == 1

    async def test_delete_device_schedules_mesh_uses_ble_endpoint(self):
        """Mesh schedule DELETE should call BLE delete endpoint."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        gateway_id = "03ab0000000000a1"
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                {"msgSn": "2"},
                {"timings": []},
            ]

            result = await client.delete_device_schedules(
                "mesh_group_10001",
                9,
                [22],
                mesh_gateway_id=gateway_id,
            )

        assert result == []
        assert len(mock_request.await_args_list) == 2
        assert mock_request.await_args_list[0].args == (
            PATH_BLE_SCHEDULE_DELETE,
            {"deviceId": gateway_id, "idList": [22]},
        )
        assert mock_request.await_args_list[1].args == (
            PATH_BLE_SCHEDULE_GET,
            {"deviceId": gateway_id, "deviceType": "mesh"},
        )

    @pytest.mark.asyncio
    async def test_get_device_schedules_standard_accepts_list_response(self):
        """Standard schedule GET should accept list payload returned by real API."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        rows = [{"id": 1, "active": True, "schedule": {"days": [1], "time": [3600]}}]
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = rows

            result = await client.get_device_schedules("03ab5ccd7caaaaaa", 1)

        mock_request.assert_awaited_once_with(
            PATH_SCHEDULE_GET,
            {
                "deviceId": "03ab5ccd7caaaaaa",
                "deviceType": client._to_device_type_hex(1),
            },
        )
        assert result == rows

    @pytest.mark.asyncio
    async def test_get_device_schedules_standard_accepts_dict_timings_response(self):
        """Standard schedule GET should also support wrapped timings payload."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        rows = [{"id": 2, "active": False, "schedule": {"days": [2], "time": [7200]}}]
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"timings": rows}

            result = await client.get_device_schedules("03ab5ccd7caaaaaa", 1)

        mock_request.assert_awaited_once_with(
            PATH_SCHEDULE_GET,
            {
                "deviceId": "03ab5ccd7caaaaaa",
                "deviceType": client._to_device_type_hex(1),
            },
        )
        assert result == rows

    @pytest.mark.asyncio
    async def test_add_device_schedule_standard_accepts_list_response(self):
        """Standard schedule ADD should accept list payload variants."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        rows = [{"id": 3, "active": True, "schedule": {"days": [3], "time": [10800]}}]
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = rows

            result = await client.add_device_schedule(
                "03ab5ccd7caaaaaa",
                1,
                [1, 2, 3],
                [3600],
                [0],
            )

        mock_request.assert_awaited_once_with(
            PATH_SCHEDULE_ADD,
            {
                "deviceId": "03ab5ccd7caaaaaa",
                "deviceType": client._to_device_type_hex(1),
                "scheduleInfo": {"days": [1, 2, 3], "time": [3600], "evt": [0]},
                "groupId": "",
                "singleBle": False,
            },
        )
        assert result == rows

    @pytest.mark.asyncio
    async def test_delete_device_schedules_standard_accepts_data_wrapper(self):
        """Standard schedule DELETE should accept data-wrapped rows."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        rows = [{"id": 4, "active": True, "schedule": {"days": [1], "time": [0]}}]
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"data": rows}

            result = await client.delete_device_schedules(
                "03ab5ccd7caaaaaa",
                1,
                [4],
            )

        mock_request.assert_awaited_once_with(
            PATH_SCHEDULE_DELETE,
            {
                "deviceId": "03ab5ccd7caaaaaa",
                "deviceType": client._to_device_type_hex(1),
                "idList": [4],
                "groupId": "",
                "singleBle": False,
            },
        )
        assert result == rows

    @pytest.mark.asyncio
    async def test_get_device_schedules_standard_invalid_payload_returns_empty(self):
        """Unexpected standard schedule payload should degrade to empty list."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"status": "ok"}

            result = await client.get_device_schedules("03ab5ccd7caaaaaa", 1)

        mock_request.assert_awaited_once_with(
            PATH_SCHEDULE_GET,
            {
                "deviceId": "03ab5ccd7caaaaaa",
                "deviceType": client._to_device_type_hex(1),
            },
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_get_device_schedules_non_mesh_uses_standard_endpoint(self):
        """Non-mesh schedule GET should use the standard endpoint directly."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"timings": []}

            await client.get_device_schedules("03ab5ccd7caaaaaa", 1)

        mock_request.assert_awaited_once_with(
            PATH_SCHEDULE_GET,
            {
                "deviceId": "03ab5ccd7caaaaaa",
                "deviceType": client._to_device_type_hex(1),
            },
        )

    @pytest.mark.asyncio
    async def test_get_device_schedules_non_mesh_bubbles_standard_error(self):
        """Standard GET errors should bubble for non-mesh devices."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = LiproApiError("invalid", "100000")

            with pytest.raises(LiproApiError, match="invalid"):
                await client.get_device_schedules("03ab5ccd7caaaaaa", 1)

        mock_request.assert_awaited_once_with(
            PATH_SCHEDULE_GET,
            {
                "deviceId": "03ab5ccd7caaaaaa",
                "deviceType": client._to_device_type_hex(1),
            },
        )

    @pytest.mark.asyncio
    async def test_add_delete_schedule_non_mesh_bubble_standard_errors(self):
        """Standard ADD/DELETE errors should bubble for non-mesh devices."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                LiproApiError("add invalid", "100000"),
                LiproApiError("delete invalid", "100000"),
            ]

            with pytest.raises(LiproApiError, match="add invalid"):
                await client.add_device_schedule(
                    "03ab5ccd7caaaaaa",
                    1,
                    [1],
                    [3600],
                    [0],
                )

            with pytest.raises(LiproApiError, match="delete invalid"):
                await client.delete_device_schedules(
                    "03ab5ccd7caaaaaa",
                    1,
                    [1],
                )

        assert mock_request.await_args_list[0].args == (
            PATH_SCHEDULE_ADD,
            {
                "deviceId": "03ab5ccd7caaaaaa",
                "deviceType": client._to_device_type_hex(1),
                "scheduleInfo": {"days": [1], "time": [3600], "evt": [0]},
                "groupId": "",
                "singleBle": False,
            },
        )
        assert mock_request.await_args_list[1].args == (
            PATH_SCHEDULE_DELETE,
            {
                "deviceId": "03ab5ccd7caaaaaa",
                "deviceType": client._to_device_type_hex(1),
                "idList": [1],
                "groupId": "",
                "singleBle": False,
            },
        )
