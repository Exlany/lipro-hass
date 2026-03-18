"""Tests for Lipro API client."""

from __future__ import annotations

import hashlib
import json
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.lipro.const.api import (
    PATH_BLE_SCHEDULE_ADD,
    PATH_BLE_SCHEDULE_DELETE,
    PATH_BLE_SCHEDULE_GET,
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
    PATH_SCHEDULE_ADD,
    PATH_SCHEDULE_DELETE,
    PATH_SCHEDULE_GET,
)
from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRestFacade,
)


class TestLiproRestFacadeInit:
    """Tests for LiproRestFacade initialization."""

    def test_init_with_session(self):
        """Test initialization with provided session."""
        session = MagicMock(spec=aiohttp.ClientSession)
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000", session)

        assert client.phone_id == "550e8400-e29b-41d4-a716-446655440000"
        assert client.access_token is None
        assert client.refresh_token is None
        assert client.user_id is None

    def test_init_without_session(self):
        """Test initialization without session."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        assert client.phone_id == "550e8400-e29b-41d4-a716-446655440000"
        assert client._session is None


class TestLiproRestFacadeTokens:
    """Tests for token management."""

    def test_set_tokens(self):
        """Test setting tokens."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens(
            access_token="access123",
            refresh_token="refresh456",
            user_id=10001,
            biz_id="lip_biz001",
        )

        assert client.access_token == "access123"
        assert client.refresh_token == "refresh456"
        assert client.user_id == 10001

    def test_set_token_refresh_callback(self):
        """Test setting token refresh callback."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        callback = AsyncMock()
        client.set_token_refresh_callback(callback)

        assert client._on_token_refresh is callback


class TestLiproRestFacadeSignature:
    """Tests for API signature generation."""

    def test_smart_home_sign(self):
        """Test Smart Home API signature generation."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        sign = client._smart_home_sign()

        # Verify it's a valid MD5 hash (32 hex chars)
        assert len(sign) == 32
        assert all(c in "0123456789abcdef" for c in sign)

    def test_iot_sign(self):
        """Test IoT API signature generation."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token_123", "refresh_token")

        sign = client._iot_sign(1234567890, '{"test": "body"}')

        # Verify it's a valid MD5 hash
        assert len(sign) == 32
        assert all(c in "0123456789abcdef" for c in sign)


class TestLiproRestFacadeLogin:
    """Tests for login functionality."""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Test successful login."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        mock_response = {
            "code": 0,
            "value": {
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "userId": 10001,
                "bizId": "lip_biz001",
                "phone": "13800000000",
                "userName": "Test User",
            },
        }

        with patch.object(
            client, "_smart_home_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response["value"]

            result = await client.login("13800000000", "password123")

            assert result["access_token"] == "new_access_token"
            assert result["refresh_token"] == "new_refresh_token"
            assert result["user_id"] == 10001
            assert client.access_token == "new_access_token"
            assert client.refresh_token == "new_refresh_token"

    @pytest.mark.asyncio
    async def test_login_password_hashed(self):
        """Test that password is MD5 hashed before sending."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        captured_data = {}

        async def capture_request(path, data, require_auth=True):
            captured_data.update(data)
            return {
                "access_token": "token",
                "refresh_token": "refresh",
                "userId": 1,
            }

        with patch.object(client, "_smart_home_request", side_effect=capture_request):
            await client.login("13800000000", "mypassword")

            # Verify password was MD5 hashed
            expected_hash = hashlib.md5(b"mypassword").hexdigest()
            assert captured_data.get("password") == expected_hash


class TestLiproRestFacadeRefreshToken:
    """Tests for token refresh functionality."""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self):
        """Test successful token refresh."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("old_access", "old_refresh")

        with patch.object(
            client, "_smart_home_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "userId": 10001,
            }

            result = await client.refresh_access_token()

            assert result["access_token"] == "new_access_token"
            assert client.access_token == "new_access_token"

    @pytest.mark.asyncio
    async def test_refresh_token_no_token(self):
        """Test refresh fails without refresh token."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with pytest.raises(LiproAuthError, match="No refresh token"):
            await client.refresh_access_token()


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


class TestLiproRestFacadeErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Test handling connection errors."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_get_session", new_callable=AsyncMock
        ) as mock_get_session:
            mock_session = MagicMock()
            mock_session.post = MagicMock(
                return_value=AsyncMock(
                    __aenter__=AsyncMock(
                        side_effect=aiohttp.ClientError("Connection failed")
                    )
                )
            )
            mock_get_session.return_value = mock_session

            with pytest.raises(LiproConnectionError, match="Connection error"):
                await client.login("phone", "password")

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """Test handling timeout errors."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_get_session", new_callable=AsyncMock
        ) as mock_get_session:
            mock_session = MagicMock()
            mock_session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(side_effect=TimeoutError()))
            )
            mock_get_session.return_value = mock_session

            with pytest.raises(LiproConnectionError, match="timeout"):
                await client.login("phone", "password")

    @pytest.mark.asyncio
    async def test_api_error(self):
        """Test handling API errors."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        mock_response = {
            "code": 500,
            "message": "Internal server error",
        }

        with patch.object(
            client, "_get_session", new_callable=AsyncMock
        ) as mock_get_session:
            mock_session = MagicMock()
            mock_response_obj = AsyncMock()
            mock_response_obj.status = 200
            mock_response_obj.headers = {}
            mock_response_obj.json = AsyncMock(return_value=mock_response)
            mock_session.post = MagicMock(
                return_value=AsyncMock(
                    __aenter__=AsyncMock(return_value=mock_response_obj)
                )
            )
            mock_get_session.return_value = mock_session

            with pytest.raises(LiproApiError, match="Internal server error"):
                await client.login("phone", "password")


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


class TestLiproRestFacadeSuccessCodes:
    """Tests for success-code behavior."""

    @pytest.mark.asyncio
    async def test_smart_home_request_accepts_string_success_code(self):
        """Smart Home API should accept string success code variants."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (200, {"code": "0000", "value": {"ok": True}}, {})
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                result = await client._smart_home_request(
                    "/test",
                    {},
                    require_auth=False,
                )

        assert result == {"ok": True}

    @pytest.mark.asyncio
    async def test_smart_home_request_accepts_zero_success_code(self):
        """Smart Home API should accept legacy numeric zero success code."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (200, {"code": 0, "value": {"ok": True}}, {})
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                result = await client._smart_home_request(
                    "/test",
                    {},
                    require_auth=False,
                )

        assert result == {"ok": True}

    @pytest.mark.asyncio
    async def test_smart_home_request_accepts_whitespace_success_code(self):
        """Smart Home API should tolerate string success codes with spaces."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (
                200,
                {"code": " 0000 ", "value": {"ok": True}},
                {},
            )
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                result = await client._smart_home_request(
                    "/test",
                    {},
                    require_auth=False,
                )

        assert result == {"ok": True}

    @pytest.mark.asyncio
    async def test_smart_home_request_preserves_empty_list_value(self):
        """Smart Home API should preserve empty list payload on success."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (200, {"code": "0000", "value": []}, {})
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                result = await client._smart_home_request(
                    "/test",
                    {},
                    require_auth=False,
                )

        assert result == []

    @pytest.mark.asyncio
    async def test_smart_home_request_non_object_response_raises_api_error(self):
        """Non-object Smart Home response should raise LiproApiError."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (200, ["not", "an", "object"], {})
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                with pytest.raises(LiproApiError, match="expected object"):
                    await client._smart_home_request(
                        "/test",
                        {},
                        require_auth=False,
                    )

    @pytest.mark.asyncio
    async def test_smart_home_request_accepts_string_auth_code(self):
        """Smart Home API should treat string auth code variants as auth errors."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (
                200,
                {"code": "401", "message": "Unauthorized"},
                {},
            )
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                with pytest.raises(LiproAuthError):
                    await client._smart_home_request(
                        "/test",
                        {},
                        require_auth=False,
                    )

    @pytest.mark.asyncio
    async def test_smart_home_request_auth_error_without_auth_skips_refresh(self):
        """require_auth=False auth errors should not trigger token refresh callback."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        refresh_callback = AsyncMock()
        client.set_token_refresh_callback(refresh_callback)

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (200, {"code": 401, "message": "Unauthorized"}, {})
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                with pytest.raises(LiproAuthError):
                    await client._smart_home_request(
                        "/test",
                        {},
                        require_auth=False,
                    )

        refresh_callback.assert_not_called()

    @pytest.mark.asyncio
    async def test_smart_home_request_prefers_error_code_for_auth_error(self):
        """Auth errors in errorCode field should propagate with the right code."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (
                200,
                {"code": 500, "errorCode": 2001, "message": "Unauthorized"},
                {},
            )
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                with pytest.raises(LiproAuthError) as err:
                    await client._smart_home_request(
                        "/test",
                        {},
                        require_auth=False,
                    )

        assert err.value.code == 2001

    @pytest.mark.asyncio
    async def test_smart_home_request_non_auth_prefers_error_code(self):
        """Non-auth errors should keep the more specific errorCode value."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (
                200,
                {"code": 500, "errorCode": "100000", "message": "Invalid parameter"},
                {},
            )
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                with pytest.raises(LiproApiError) as err:
                    await client._smart_home_request(
                        "/test",
                        {},
                        require_auth=False,
                    )

        assert err.value.code == 100000

    @pytest.mark.asyncio
    async def test_smart_home_request_token_expired_case_insensitive(self):
        """token_expired auth code should be matched case-insensitively."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (
                200,
                {"code": " TOKEN_EXPIRED ", "message": "Unauthorized"},
                {},
            )
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                with pytest.raises(LiproAuthError) as err:
                    await client._smart_home_request(
                        "/test",
                        {},
                        require_auth=False,
                    )

        assert err.value.code == "token_expired"

    @pytest.mark.asyncio
    async def test_smart_home_request_refresh_expired_treated_as_auth_error(self):
        """Refresh-expired codes should be classified as LiproAuthError."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (
                200,
                {"code": 20002, "message": "Refresh token expired"},
                {},
            )
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                with pytest.raises(LiproAuthError) as err:
                    await client._smart_home_request(
                        "/v1/user/token/refresh.do",
                        {},
                        require_auth=False,
                    )

        assert err.value.code == 20002

    @pytest.mark.asyncio
    async def test_iot_request_accepts_string_success_code(self):
        """IoT API should accept string success code variants."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (200, {"code": "200", "data": {"ok": True}}, {})
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                result = await client._iot_request("/test", {})

        assert result == {"ok": True}

    @pytest.mark.asyncio
    async def test_iot_request_accepts_zero_string_success_code(self):
        """IoT API should accept legacy string zero success code."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (200, {"code": "0", "data": {"ok": True}}, {})
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                result = await client._iot_request("/test", {})

        assert result == {"ok": True}

    @pytest.mark.asyncio
    async def test_iot_request_auth_error_with_whitespace_code(self):
        """IoT API should treat space-padded auth code as auth failure."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (
                200,
                {"code": " 2001 ", "message": "Auth error"},
                {},
            )
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                with pytest.raises(LiproAuthError) as err:
                    await client._iot_request("/test", {})

        assert err.value.code == 2001

    @pytest.mark.asyncio
    async def test_iot_request_non_auth_prefers_error_code(self):
        """IoT non-auth errors should preserve specific errorCode."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (
                200,
                {"code": 500, "errorCode": 140003, "message": "Device offline"},
                {},
            )
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                with pytest.raises(LiproApiError) as err:
                    await client._iot_request("/test", {})

        assert err.value.code == 140003

    @pytest.mark.asyncio
    async def test_iot_request_token_expired_error_code_case_insensitive(self):
        """IoT errorCode token_expired should be case-insensitive."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (
                200,
                {"code": 500, "errorCode": "Token_Expired", "message": "Unauthorized"},
                {},
            )
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                with pytest.raises(LiproAuthError) as err:
                    await client._iot_request("/test", {})

        assert err.value.code == "token_expired"

    @pytest.mark.asyncio
    async def test_iot_request_refresh_expired_treated_as_auth_error(self):
        """IoT refresh-expired-like codes should be treated as auth failures."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (
                200,
                {"code": "1202", "message": "Refresh token expired"},
                {},
            )
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                with pytest.raises(LiproAuthError) as err:
                    await client._iot_request("/test", {})

        assert err.value.code == 1202

    @pytest.mark.asyncio
    async def test_iot_request_preserves_empty_data_payload(self):
        """IoT API should keep empty data payload instead of wrapper fields."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (
                200,
                {"code": "0000", "data": {}, "message": "success", "success": True},
                {},
            )
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                result = await client._iot_request("/test", {})

        assert result == {}

    @pytest.mark.asyncio
    async def test_iot_request_none_data_payload_returns_empty_dict(self):
        """IoT API should normalize data=None to empty dict."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (200, {"code": "0000", "data": None}, {})
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                result = await client._iot_request("/test", {})

        assert result == {}

    @pytest.mark.asyncio
    async def test_iot_request_non_object_response_raises_api_error(self):
        """Non-object IoT response should raise LiproApiError."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (200, ["not", "an", "object"], {})
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session:
                mock_session.return_value = MagicMock()
                with pytest.raises(LiproApiError, match="expected object"):
                    await client._iot_request("/test", {})


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


class TestLiproRestFacade429Handling:
    """Tests for 429 rate limit handling."""

    @pytest.mark.asyncio
    async def test_429_with_retry_after_seconds(self):
        """Test 429 handling with Retry-After header in seconds."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        call_count = 0

        async def mock_execute_request(request_ctx, path):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call returns 429
                return (
                    429,
                    {"code": 429, "message": "Too Many Requests"},
                    {"Retry-After": "0.01"},
                )
            # Second call succeeds (code 200 is RESPONSE_SUCCESS)
            return 200, {"code": 200, "value": {"devices": []}}, {}

        with (
            patch.object(client, "_execute_request", side_effect=mock_execute_request),
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
        ):
            mock_session.return_value = MagicMock()
            result = await client.get_devices()

        assert call_count == 2
        assert "devices" in result

    @pytest.mark.asyncio
    async def test_429_max_retries_exceeded(self):
        """Test 429 raises error after max retries."""
        from custom_components.lipro.core.api import LiproRateLimitError

        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        async def mock_execute_request(request_ctx, path):
            # Always return 429
            return (
                429,
                {"code": 429, "message": "Too Many Requests"},
                {"Retry-After": "0.01"},
            )

        with (
            patch.object(client, "_execute_request", side_effect=mock_execute_request),
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
        ):
            mock_session.return_value = MagicMock()
            with pytest.raises(
                LiproRateLimitError, match="Rate limited after 2 retries"
            ):
                await client.get_devices()

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

class TestLiproRestFacadeIotRequest:
    """Tests for IoT API request handling."""

    @pytest.mark.asyncio
    async def test_iot_request_no_access_token(self):
        """Test IoT request fails without access token."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        # No tokens set

        with pytest.raises(LiproAuthError, match="No access token"):
            await client._iot_request("/test", {})

    @pytest.mark.asyncio
    async def test_iot_request_auth_error_codes(self):
        """Test IoT request handles various auth error codes."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        # Test different auth error codes
        for code in [401, "401", 2001, 2002]:
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_get_session:
                mock_session = MagicMock()
                mock_response_obj = AsyncMock()
                mock_response_obj.status = 200
                mock_response_obj.headers = {}
                mock_response_obj.json = AsyncMock(
                    return_value={
                        "code": code,
                        "message": "Auth error",
                    }
                )
                mock_session.post = MagicMock(
                    return_value=AsyncMock(
                        __aenter__=AsyncMock(return_value=mock_response_obj)
                    )
                )
                mock_get_session.return_value = mock_session

                with pytest.raises(LiproAuthError):
                    await client._iot_request("/test", {})


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


class TestLiproRestFacadeBizId:
    """Tests for biz_id handling."""

    def test_biz_id_stored(self):
        """Test that biz_id is stored when setting tokens."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens(
            access_token="access",
            refresh_token="refresh",
            user_id=123,
            biz_id="lip_biz001",
        )

        assert client._biz_id == "lip_biz001"

    def test_biz_id_default(self):
        """Test that biz_id defaults to None."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        assert client._biz_id is None

    @pytest.mark.asyncio
    async def test_429_with_huge_retry_after_is_capped(self):
        """Test that 429 with huge Retry-After doesn't hang (integration test)."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        call_count = 0

        async def mock_execute_request(request_ctx, path):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return (
                    429,
                    {"code": 429, "message": "Too Many Requests"},
                    {"Retry-After": "999999"},
                )
            return 200, {"code": 200, "value": {"devices": []}}, {}

        with (
            patch.object(client, "_execute_request", side_effect=mock_execute_request),
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
            patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
        ):
            mock_session.return_value = MagicMock()
            await client.get_devices()

        # Verify sleep was called with capped value (60), not 999999
        mock_sleep.assert_called_once()
        actual_wait = mock_sleep.call_args[0][0]
        assert actual_wait == 60.0


class TestLiproRestFacadeAdditionalBranchCoverage:
    """Additional branch-focused tests for API client helpers and edge paths."""

    def test_normalize_iot_device_id_non_string(self):
        """Non-string IDs should be rejected by IoT ID normalizer."""
        from custom_components.lipro.core.utils.identifiers import (
            normalize_iot_device_id,
        )

        assert normalize_iot_device_id(123) is None

    @pytest.mark.asyncio
    async def test_get_session_without_injected_session_raises(self):
        """Session access should fail fast when no aiohttp session is injected."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with pytest.raises(LiproConnectionError, match="No aiohttp session"):
            await client._get_session()

    def test_resolve_error_code_returns_none_for_empty_values(self):
        """Empty/zero code fields should normalize to None."""
        assert LiproRestFacade._resolve_error_code(None, 0) is None

    def test_is_command_busy_error_false_for_empty_message(self):
        """Empty error message with non-busy code should not be treated as busy."""
        assert LiproRestFacade._is_command_busy_error(LiproApiError("", 500)) is False

    @pytest.mark.asyncio
    async def test_smart_home_request_requires_access_token_when_auth_enabled(self):
        """Authenticated smart-home requests should fail without access token."""
        session = MagicMock()
        session.closed = False
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000", session)

        with pytest.raises(LiproAuthError, match="No access token available"):
            await client._smart_home_request("/test", {"k": "v"}, require_auth=True)

    @pytest.mark.asyncio
    async def test_smart_home_request_typed_value_paths(self):
        """typedValue response should be unwrapped, including None fallback."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with (
            patch.object(
                client, "_execute_request", new_callable=AsyncMock
            ) as mock_exec,
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
        ):
            mock_session.return_value = MagicMock()
            mock_exec.side_effect = [
                (200, {"code": 200, "typedValue": {"ok": True}}, {}),
                (200, {"code": 200, "typedValue": None}, {}),
            ]
            first = await client._smart_home_request("/typed", {}, require_auth=False)
            second = await client._smart_home_request("/typed", {}, require_auth=False)

        assert first == {"ok": True}
        assert second == {}

    @pytest.mark.asyncio
    async def test_iot_request_429_retries_then_succeeds(self):
        """IoT request should retry once on 429 and then return success payload."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with (
            patch.object(
                client, "_execute_request", new_callable=AsyncMock
            ) as mock_exec,
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
            patch(
                "custom_components.lipro.core.api.client_pacing.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            mock_session.return_value = MagicMock()
            mock_exec.side_effect = [
                (429, {"code": 429}, {"Retry-After": "0.01"}),
                (200, {"code": 200, "data": {"ok": True}}, {}),
            ]
            result = await client._iot_request("/iot", {"x": 1})

        assert result == {"ok": True}
        assert mock_exec.await_count == 2

    @pytest.mark.asyncio
    async def test_iot_request_http_401_without_refresh_raises_auth_error(self):
        """HTTP 401 should raise auth error when refresh retry is unavailable."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with (
            patch.object(
                client, "_execute_request", new_callable=AsyncMock
            ) as mock_exec,
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
        ):
            mock_session.return_value = MagicMock()
            mock_exec.return_value = (401, {"message": "Unauthorized"}, {})
            with pytest.raises(LiproAuthError, match="HTTP 401 Unauthorized"):
                await client._iot_request("/iot", {"x": 1})

    @pytest.mark.asyncio
    async def test_iot_request_auth_code_refreshes_and_retries(self):
        """Auth error in body should refresh token once and retry request."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_old", "refresh")
        refresh_callback = AsyncMock(
            side_effect=lambda: client.set_tokens("access_new", "refresh")
        )
        client.set_token_refresh_callback(refresh_callback)

        with (
            patch.object(
                client, "_execute_request", new_callable=AsyncMock
            ) as mock_exec,
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
        ):
            mock_session.return_value = MagicMock()
            mock_exec.side_effect = [
                (200, {"code": 2001, "message": "Unauthorized"}, {}),
                (200, {"code": 200, "data": {"ok": True}}, {}),
            ]
            result = await client._iot_request("/iot", {"x": 1})

        assert result == {"ok": True}
        refresh_callback.assert_called_once()

    def test_unwrap_iot_success_payload_without_data_returns_original(self):
        """IoT success unwrapping should keep original payload when data key is absent."""
        payload = {"code": 200, "message": "ok"}
        assert LiproRestFacade._unwrap_iot_success_payload(payload) == payload

    @pytest.mark.asyncio
    async def test_login_with_prehashed_password_keeps_hash(self):
        """login(password_is_hashed=True) should pass hash through unchanged."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        captured_data: dict[str, str] = {}

        async def _capture(path, data, require_auth=True):
            captured_data.update(data)
            return {"access_token": "a", "refresh_token": "r", "userId": 1}

        with patch.object(client, "_smart_home_request", side_effect=_capture):
            await client.login("13800000000", "already_hashed", password_is_hashed=True)

        assert captured_data["password"] == "already_hashed"

    @pytest.mark.asyncio
    async def test_login_missing_tokens_raises_auth_error(self):
        """Login response without tokens should fail explicitly."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_smart_home_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"access_token": "a_only"}
            with pytest.raises(
                LiproAuthError, match="missing access_token or refresh_token"
            ):
                await client.login("13800000000", "password")

    @pytest.mark.asyncio
    async def test_refresh_access_token_missing_tokens_raises_auth_error(self):
        """Refresh endpoint response without token pair should raise auth error."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("old_access", "old_refresh")

        with patch.object(
            client, "_smart_home_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"access_token": "new_only"}
            with pytest.raises(
                LiproAuthError, match="missing access_token or refresh_token"
            ):
                await client.refresh_access_token()

    @pytest.mark.asyncio
    async def test_get_product_configs_handles_list_and_non_list_payloads(self):
        """Product configs should return list payload or empty list fallback."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_smart_home_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                [{"productId": 1}],
                {"unexpected": True},
            ]
            list_result = await client.get_product_configs()
            fallback_result = await client.get_product_configs()

        assert list_result == [{"productId": 1}]
        assert fallback_result == []

    @pytest.mark.asyncio
    async def test_get_mqtt_config_429_retries_then_succeeds(self):
        """MQTT config endpoint should retry once on 429."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with (
            patch.object(
                client, "_execute_request", new_callable=AsyncMock
            ) as mock_exec,
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
            patch(
                "custom_components.lipro.core.api.client_pacing.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            mock_session.return_value = MagicMock()
            mock_exec.side_effect = [
                (429, {"code": 429}, {"Retry-After": "0.01"}),
                (200, {"accessKey": "ak", "secretKey": "sk"}, {}),
            ]
            result = await client.get_mqtt_config()

        assert result == {"accessKey": "ak", "secretKey": "sk"}
        assert mock_exec.await_count == 2

    @pytest.mark.asyncio
    async def test_get_mqtt_config_401_refresh_retry_success(self):
        """MQTT config endpoint should retry after successful token refresh."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_old", "refresh")
        refresh_callback = AsyncMock(
            side_effect=lambda: client.set_tokens("access_new", "refresh")
        )
        client.set_token_refresh_callback(refresh_callback)

        with (
            patch.object(
                client, "_execute_request", new_callable=AsyncMock
            ) as mock_exec,
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
        ):
            mock_session.return_value = MagicMock()
            mock_exec.side_effect = [
                (401, {"message": "Unauthorized"}, {}),
                (200, {"accessKey": "ak", "secretKey": "sk"}, {}),
            ]
            result = await client.get_mqtt_config()

        assert result == {"accessKey": "ak", "secretKey": "sk"}
        refresh_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_mqtt_config_non_success_response_raises_api_error(self):
        """Non-success wrapped MQTT config should raise LiproApiError."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with (
            patch.object(
                client, "_execute_request", new_callable=AsyncMock
            ) as mock_exec,
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
        ):
            mock_session.return_value = MagicMock()
            mock_exec.return_value = (200, {"code": 500, "message": "bad"}, {})
            with pytest.raises(LiproApiError, match="bad"):
                await client.get_mqtt_config()
