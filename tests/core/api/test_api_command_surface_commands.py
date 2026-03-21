"""Topicized API regression coverage extracted from `tests/core/api/test_api.py` (test_api_command_surface)."""

from __future__ import annotations

from .test_api import AsyncMock, LiproRestFacade, patch, pytest


class TestLiproRestFacadeCommands:
    """Tests for command sending."""

    @pytest.mark.asyncio
    async def test_send_command(self):
        """Test sending command to device."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"success": True}

            result = await client.send_command(
                device_id="03ab5ccd7caaaaaa",
                command="POWER_ON",
                device_type=1,
                properties=[{"key": "powerState", "value": "1"}],
            )

            assert result["success"] is True
            mock_request.assert_called_once()

            # Verify the body structure
            call_args = mock_request.call_args
            body = call_args[0][1]
            assert body["command"] == "POWER_ON"
            assert body["deviceId"] == "03ab5ccd7caaaaaa"
            assert body["deviceType"] == "ff000001"

    @pytest.mark.asyncio
    async def test_send_command_hex_device_type(self):
        """Test sending command with hex device type."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"success": True}

            await client.send_command(
                device_id="03ab5ccd7caaaaaa",
                command="POWER_ON",
                device_type="ff000002",  # Hex string
            )

            call_args = mock_request.call_args
            body = call_args[0][1]
            assert body["deviceType"] == "ff000002"

    @pytest.mark.asyncio
    async def test_send_command_decimal_string_device_type(self):
        """Decimal string device type should be normalized to hex."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"success": True}

            await client.send_command(
                device_id="03ab5ccd7caaaaaa",
                command="POWER_ON",
                device_type="99",
            )

            call_args = mock_request.call_args
            body = call_args[0][1]
            assert body["deviceType"] == "ff000063"

    @pytest.mark.asyncio
    async def test_send_command_invalid_string_device_type_raises(self):
        """Non-hex/non-numeric device type strings should be rejected."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with pytest.raises(ValueError, match="Invalid deviceType format"):
            await client.send_command(
                device_id="03ab5ccd7caaaaaa",
                command="POWER_ON",
                device_type="light",
            )

    @pytest.mark.asyncio
    async def test_send_group_command(self):
        """Test sending command to mesh group."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"success": True}

            result = await client.send_group_command(
                group_id="mesh_group_10001",
                command="POWER_ON",
                device_type=1,
            )

            assert result["success"] is True
            call_args = mock_request.call_args
            body = call_args[0][1]
            assert body["groupId"] == "mesh_group_10001"


class TestLiproRestFacadeCommandsExtended:
    """Extended tests for command sending."""

    @pytest.mark.asyncio
    async def test_send_command_with_properties(self):
        """Test sending command with properties."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"success": True}

            await client.send_command(
                device_id="03ab5ccd7caaaaaa",
                command="CHANGE_STATE",
                device_type=1,
                properties=[
                    {"key": "brightness", "value": "80"},
                    {"key": "temperature", "value": "4000"},
                ],
                iot_name="lipro_led",
            )

            call_args = mock_request.call_args
            body = call_args[0][1]
            assert body["properties"] == [
                {"key": "brightness", "value": "80"},
                {"key": "temperature", "value": "4000"},
            ]
            assert body["iotName"] == "lipro_led"

    @pytest.mark.asyncio
    async def test_send_command_without_properties(self):
        """Test sending command without properties sends empty list."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"success": True}

            await client.send_command(
                device_id="03ab5ccd7caaaaaa",
                command="POWER_ON",
                device_type=1,
            )

            call_args = mock_request.call_args
            body = call_args[0][1]
            # Real API always sends properties field (empty list for POWER_ON/OFF)
            assert body["properties"] == []

    @pytest.mark.asyncio
    async def test_send_group_command_with_properties(self):
        """Test sending group command with properties."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"success": True}

            await client.send_group_command(
                group_id="mesh_group_10001",
                command="CHANGE_STATE",
                device_type=1,
                properties=[{"key": "powerState", "value": "1"}],
            )

            call_args = mock_request.call_args
            body = call_args[0][1]
            assert body["properties"] == [{"key": "powerState", "value": "1"}]
            assert body["groupId"] == "mesh_group_10001"
            assert body["deviceId"] == "mesh_group_10001"
