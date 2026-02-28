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
    PATH_SCHEDULE_ADD,
    PATH_SCHEDULE_DELETE,
    PATH_SCHEDULE_GET,
)
from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproClient,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
    _mask_sensitive_data,
)
from custom_components.lipro.core.api_status_service import (
    query_with_fallback as query_with_fallback_service,
)


class TestMaskSensitiveData:
    """Tests for sensitive data masking."""

    def test_mask_access_token(self):
        """Test masking access token."""
        data = '{"access_token": "secret123", "other": "value"}'
        result = _mask_sensitive_data(data)
        assert '"access_token": "***"' in result
        assert "secret123" not in result
        assert '"other": "value"' in result

    def test_mask_refresh_token(self):
        """Test masking refresh token."""
        data = '{"refresh_token": "refresh_secret"}'
        result = _mask_sensitive_data(data)
        assert '"refresh_token": "***"' in result
        assert "refresh_secret" not in result

    def test_mask_password(self):
        """Test masking password."""
        data = '{"password": "mypassword123"}'
        result = _mask_sensitive_data(data)
        assert '"password": "***"' in result
        assert "mypassword123" not in result

    def test_mask_phone(self):
        """Test masking phone number (keep first 3 and last 4)."""
        data = '{"phone": "13800001234"}'
        result = _mask_sensitive_data(data)
        assert '"phone": "138****1234"' in result
        assert "13800001234" not in result

    def test_mask_camel_case_tokens(self):
        """Test masking camelCase token fields."""
        data = '{"accessToken": "token1", "refreshToken": "token2"}'
        result = _mask_sensitive_data(data)
        assert '"accessToken": "***"' in result
        assert '"refreshToken": "***"' in result

    def test_mask_mqtt_keys(self):
        """Test masking MQTT access/secret keys."""
        data = '{"accessKey":"ak_test","secretKey":"sk_test"}'
        result = _mask_sensitive_data(data)
        assert '"accessKey": "***"' in result
        assert '"secretKey": "***"' in result
        assert "ak_test" not in result
        assert "sk_test" not in result

    def test_mask_device_name_room_name_and_network_fields(self):
        """Test masking additional privacy-sensitive device/network fields."""
        data = (
            '{"deviceName":"Bedroom Light","roomName":"Master",'
            '"wifi_ssid":"HomeWifi","mac":"5c:cd:7c:11:22:33","ip":"10.0.0.10"}'
        )
        result = _mask_sensitive_data(data)
        assert '"deviceName": "***"' in result
        assert '"roomName": "***"' in result
        assert '"wifi_ssid": "***"' in result
        assert '"mac": "***"' in result
        assert '"ip": "***"' in result
        assert "Bedroom Light" not in result
        assert "Master" not in result
        assert "HomeWifi" not in result


class TestLiproClientInit:
    """Tests for LiproClient initialization."""

    def test_init_with_session(self):
        """Test initialization with provided session."""
        session = MagicMock(spec=aiohttp.ClientSession)
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000", session)

        assert client.phone_id == "550e8400-e29b-41d4-a716-446655440000"
        assert client.access_token is None
        assert client.refresh_token is None
        assert client.user_id is None

    def test_init_without_session(self):
        """Test initialization without session."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        assert client.phone_id == "550e8400-e29b-41d4-a716-446655440000"
        assert client._session is None


class TestLiproClientTokens:
    """Tests for token management."""

    def test_set_tokens(self):
        """Test setting tokens."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        callback = AsyncMock()
        client.set_token_refresh_callback(callback)

        assert client._on_token_refresh is callback


class TestLiproClientSignature:
    """Tests for API signature generation."""

    def test_smart_home_sign(self):
        """Test Smart Home API signature generation."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        sign = client._smart_home_sign()

        # Verify it's a valid MD5 hash (32 hex chars)
        assert len(sign) == 32
        assert all(c in "0123456789abcdef" for c in sign)

    def test_iot_sign(self):
        """Test IoT API signature generation."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token_123", "refresh_token")

        sign = client._iot_sign(1234567890, '{"test": "body"}')

        # Verify it's a valid MD5 hash
        assert len(sign) == 32
        assert all(c in "0123456789abcdef" for c in sign)


class TestLiproClientLogin:
    """Tests for login functionality."""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Test successful login."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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


class TestLiproClientRefreshToken:
    """Tests for token refresh functionality."""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self):
        """Test successful token refresh."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with pytest.raises(LiproAuthError, match="No refresh token"):
            await client.refresh_access_token()


class TestLiproClientDevices:
    """Tests for device-related API calls."""

    @pytest.mark.asyncio
    async def test_get_devices(self):
        """Test getting devices."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        result = await client.query_device_status([])

        assert result == []


class TestLiproClientCommands:
    """Tests for command sending."""

    @pytest.mark.asyncio
    async def test_send_command(self):
        """Test sending command to device."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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


class TestLiproClientErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Test handling connection errors."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
    async def test_invalid_json_error_does_not_expose_raw_body(self):
        """Invalid JSON exceptions should avoid leaking raw response body."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        response = AsyncMock()
        response.status = 500
        response.headers = {}
        response.json = AsyncMock(
            side_effect=aiohttp.ContentTypeError(
                request_info=MagicMock(),
                history=(),
                message="invalid content-type",
            )
        )
        response.text = AsyncMock(return_value='{"access_token":"secret_token_value"}')
        request_ctx = AsyncMock(
            __aenter__=AsyncMock(return_value=response),
            __aexit__=AsyncMock(return_value=None),
        )

        with pytest.raises(LiproApiError) as err_ctx:
            await client._execute_request(request_ctx, "/test/path")

        assert "secret_token_value" not in str(err_ctx.value)
        assert "body_length=" in str(err_ctx.value)

    @pytest.mark.asyncio
    async def test_invalid_json_masks_only_truncated_body_preview(self):
        """Invalid JSON logging should avoid masking the entire response body."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        large_body = '{"access_token":"secret"}' * 2000
        response = AsyncMock()
        response.status = 500
        response.headers = {}
        response.json = AsyncMock(
            side_effect=aiohttp.ContentTypeError(
                request_info=MagicMock(),
                history=(),
                message="invalid content-type",
            )
        )
        response.text = AsyncMock(return_value=large_body)
        request_ctx = AsyncMock(
            __aenter__=AsyncMock(return_value=response),
            __aexit__=AsyncMock(return_value=None),
        )

        with (
            patch(
                "custom_components.lipro.core.api._mask_sensitive_data",
                side_effect=lambda payload: payload,
            ) as mock_mask,
            pytest.raises(LiproApiError),
        ):
            await client._execute_request(request_ctx, "/test/path")

        mock_mask.assert_called_once()
        assert len(mock_mask.call_args.args[0]) < len(large_body)

    @pytest.mark.asyncio
    async def test_api_error(self):
        """Test handling API errors."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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


class TestLiproClient401Handling:
    """Tests for 401 error handling and token refresh."""

    @pytest.mark.asyncio
    async def test_401_triggers_refresh(self):
        """Test that 401 triggers token refresh callback."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("old_access", "old_refresh")

        refresh_callback = AsyncMock(
            side_effect=lambda: client.set_tokens("new_access", "new_refresh")
        )
        client.set_token_refresh_callback(refresh_callback)

        # Test the _handle_401_with_refresh method directly
        result = await client._handle_401_with_refresh("old_access")

        # Verify refresh was called
        assert result is True
        refresh_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_401_double_check_skips_if_token_changed(self):
        """Test that refresh is skipped if token already changed."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("new_access", "refresh")  # Token already changed

        refresh_callback = AsyncMock()
        client.set_token_refresh_callback(refresh_callback)

        # Call with old token - should detect token already changed
        result = await client._handle_401_with_refresh("old_access")

        # Should return True (token was refreshed) but not call callback
        assert result is True
        refresh_callback.assert_not_called()

    @pytest.mark.asyncio
    async def test_401_refresh_callback_without_token_update_returns_false(self):
        """Refresh callback must update token to trigger retry."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("old_access", "old_refresh")

        refresh_callback = AsyncMock()
        client.set_token_refresh_callback(refresh_callback)

        assert await client._handle_401_with_refresh("old_access") is False
        refresh_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_401_refresh_connection_error_bubbles(self):
        """Transient refresh network errors should bubble as LiproConnectionError."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("old_access", "old_refresh")

        refresh_callback = AsyncMock(side_effect=LiproConnectionError("timeout"))
        client.set_token_refresh_callback(refresh_callback)

        with pytest.raises(LiproConnectionError, match="timeout"):
            await client._handle_401_with_refresh("old_access")

    @pytest.mark.asyncio
    async def test_401_no_infinite_retry(self):
        """Test that 401 doesn't cause infinite retry loop."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        refresh_callback = AsyncMock()
        client.set_token_refresh_callback(refresh_callback)

        # Always return 401
        mock_response = {"code": 401, "message": "Unauthorized"}

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

            with pytest.raises(LiproAuthError):
                await client.get_devices()

            # Refresh should only be called once (not infinite)
            assert refresh_callback.call_count == 1

    @pytest.mark.asyncio
    async def test_401_refresh_connection_error_not_reclassified_as_auth(self):
        """Refresh network failure should not be converted to auth failure."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        refresh_callback = AsyncMock(side_effect=LiproConnectionError("timeout"))
        client.set_token_refresh_callback(refresh_callback)

        mock_response = {"code": 401, "message": "Unauthorized"}

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

            with pytest.raises(LiproConnectionError, match="timeout"):
                await client.get_devices()


class TestLiproClientMqtt:
    """Tests for MQTT configuration."""

    @pytest.mark.asyncio
    async def test_get_mqtt_config_direct_response(self):
        """Test getMqttConfig with real non-standard response (no code wrapper).

        Real API returns: {"accessKey": "hex64", "secretKey": "hex64"}
        without the usual {"code": "0000", "data": {...}} wrapper.
        """
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
    async def test_get_mqtt_config_standard_wrapped_response(self):
        """Test getMqttConfig fallback for standard wrapped response."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        # Hypothetical future response with standard wrapper
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

        assert result["accessKey"] == "encrypted_ak"

    @pytest.mark.asyncio
    async def test_get_mqtt_config_non_object_response_raises_api_error(self):
        """Non-object MQTT config payload should raise LiproApiError."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        # No tokens set

        with pytest.raises(LiproAuthError, match="No access token"):
            await client.get_mqtt_config()


class TestLiproClientSuccessCodes:
    """Tests for success-code compatibility."""

    @pytest.mark.asyncio
    async def test_smart_home_request_accepts_string_success_code(self):
        """Smart Home API should accept string success code variants."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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


class TestLiproClientClose:
    """Tests for client cleanup."""

    @pytest.mark.asyncio
    async def test_close_clears_session(self):
        """Test close clears session reference."""
        session = MagicMock(spec=aiohttp.ClientSession)
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000", session)

        await client.close()

        # Session reference should be cleared (HA manages session lifecycle)
        assert client._session is None

    @pytest.mark.asyncio
    async def test_close_external_session(self):
        """Test close does not close HA-managed session."""
        session = MagicMock(spec=aiohttp.ClientSession)
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000", session)

        await client.close()

        # External session should not be closed by client
        session.close.assert_not_called()


class TestLiproClientDeviceStatus:
    """Tests for device status queries."""

    @pytest.mark.asyncio
    async def test_query_device_status_success(self):
        """Test querying device status successfully."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
            patch("custom_components.lipro.core.api._LOGGER.warning") as mock_warning,
            patch("custom_components.lipro.core.api._LOGGER.debug") as mock_debug,
        ):
            result = await client.query_device_status(["03ab5ccd7cxxxxxx"])

        assert len(result) == 1
        mock_warning.assert_not_called()
        assert mock_debug.call_count >= 1

    @pytest.mark.asyncio
    async def test_query_device_status_other_error_raises(self):
        """Test that non-140003 errors are re-raised."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
            patch("custom_components.lipro.core.api._LOGGER.warning") as mock_warning,
        ):
            result = await client.query_device_status(["03ab5ccd7cxxxxxx"])

        assert len(result) == 1
        assert any(
            "endpoint=%s" in str(call.args[0])
            and call.args[2] == 140014
            and call.args[3] == "/app/oauth/api/v1/user/query/devices/state.do"
            for call in mock_warning.call_args_list
        )


class TestLiproClientMeshGroupStatus:
    """Tests for mesh group status queries."""

    @pytest.mark.asyncio
    async def test_query_mesh_group_status_empty(self):
        """Test querying status with empty group list."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        result = await client.query_mesh_group_status([])

        assert result == []

    @pytest.mark.asyncio
    async def test_query_mesh_group_status_success(self):
        """Test querying mesh group status successfully."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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


class TestLiproClientConnectStatus:
    """Tests for connection-status parsing."""

    @pytest.mark.asyncio
    async def test_query_connect_status_coerces_backend_variants(self):
        """Bool/int/string variants should be normalized to bool."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            result = await client.query_connect_status(["mesh_group_1", "bad/dev"])

        mock_request.assert_not_called()
        assert result == {}


class TestLiproClientOutletPower:
    """Tests for outlet power-info queries."""

    @pytest.mark.asyncio
    async def test_fetch_outlet_power_info_filters_invalid_ids(self):
        """Power-info should skip invalid/group IDs before request."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"nowPower": 3.2}
            result = await client.fetch_outlet_power_info(
                [
                    "mesh_group_10001",
                    "03AB5CCD7CABCDEF",
                    "invalid",
                    "03ab5ccd7cabcdef",
                ]
            )

        mock_request.assert_called_once_with(
            PATH_QUERY_OUTLET_POWER,
            {"deviceIds": ["03ab5ccd7cabcdef"]},
        )
        assert result == {"nowPower": 3.2}

    @pytest.mark.asyncio
    async def test_fetch_outlet_power_info_all_invalid_ids_returns_empty(self):
        """Power-info should return empty dict when no valid IoT IDs remain."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            result = await client.fetch_outlet_power_info(["mesh_group_10001"])

        mock_request.assert_not_called()
        assert result == {}

    @pytest.mark.asyncio
    async def test_fetch_outlet_power_info_invalid_param_error_returns_empty(self):
        """Endpoint-level invalid-param code should degrade to empty payload."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = LiproApiError("Invalid parameter", "100000")
            result = await client.fetch_outlet_power_info(["03ab5ccd7cabcdef"])

        mock_request.assert_called_once()
        assert result == {}

    @pytest.mark.asyncio
    async def test_fetch_outlet_power_info_other_api_error_raises(self):
        """Non-invalid-param API errors should still bubble up."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = LiproApiError("Server error", 500)
            with pytest.raises(LiproApiError, match="Server error"):
                await client.fetch_outlet_power_info(["03ab5ccd7cabcdef"])


class TestLiproClientOptionalCapabilities:
    """Tests for optional developer capability APIs."""

    @pytest.mark.asyncio
    async def test_query_command_result(self):
        """query_command_result should call endpoint with msgSn payload."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(client, "_iot_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"success": True}
            result = await client.query_command_result(
                msg_sn="682550445474476112",
                device_id="mesh_group_49155",
                device_type="ff000001",
            )

        assert result == {"success": True}
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(client, "_iot_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"province": "广东省", "city": "江门市"}
            result = await client.get_city()

        assert result == {"province": "广东省", "city": "江门市"}
        mock_request.assert_awaited_once_with(PATH_GET_CITY, {})

    @pytest.mark.asyncio
    async def test_query_ota_info(self):
        """query_ota_info should merge v1/v2 and controller OTA payloads."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        ota_v1_rows = [{"deviceType": "ff000001", "firmwareVersion": "7.10.9"}]
        controller_rows = [{"bleName": "T21JC", "version": "2.6.43"}]

        with patch.object(client, "_iot_request", new_callable=AsyncMock) as mock_request:
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
    async def test_fetch_body_sensor_history(self):
        """fetch_body_sensor_history should follow API contract fields."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(client, "_iot_request", new_callable=AsyncMock) as mock_request:
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(client, "_iot_request", new_callable=AsyncMock) as mock_request:
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


class TestLiproClient429Handling:
    """Tests for 429 rate limit handling."""

    @pytest.mark.asyncio
    async def test_429_with_retry_after_seconds(self):
        """Test 429 handling with Retry-After header in seconds."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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

        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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

    def test_parse_retry_after_seconds(self):
        """Test parsing Retry-After header with seconds value."""
        result = LiproClient._parse_retry_after({"Retry-After": "30"})
        assert result == 30.0

    def test_parse_retry_after_float(self):
        """Test parsing Retry-After header with float value."""
        result = LiproClient._parse_retry_after({"Retry-After": "1.5"})
        assert result == 1.5

    def test_parse_retry_after_missing(self):
        """Test parsing missing Retry-After header."""
        result = LiproClient._parse_retry_after({})
        assert result is None

    def test_parse_retry_after_invalid(self):
        """Test parsing invalid Retry-After header."""
        result = LiproClient._parse_retry_after({"Retry-After": "invalid"})
        # Invalid string that's not a number and not a valid HTTP date
        assert result is None

    def test_parse_retry_after_http_date(self):
        """Test parsing Retry-After header with HTTP date format."""
        # Use a date in the future
        from datetime import UTC, datetime, timedelta

        future = datetime.now(UTC) + timedelta(seconds=60)
        http_date = future.strftime("%a, %d %b %Y %H:%M:%S GMT")
        result = LiproClient._parse_retry_after({"Retry-After": http_date})
        # Should return approximately 60 seconds (allow some tolerance)
        assert result is not None
        assert 55 <= result <= 65

    def test_parse_retry_after_lowercase_header(self):
        """Test parsing lowercase retry-after header."""
        result = LiproClient._parse_retry_after({"retry-after": "10"})
        assert result == 10.0

    def test_parse_retry_after_negative(self):
        """Test parsing negative Retry-After value."""
        # Negative values should still be parsed (clamping happens at usage site)
        result = LiproClient._parse_retry_after({"Retry-After": "-5"})
        assert result == -5.0

    def test_parse_retry_after_zero(self):
        """Test parsing zero Retry-After value."""
        result = LiproClient._parse_retry_after({"Retry-After": "0"})
        assert result == 0.0


class TestLiproRateLimitError:
    """Tests for LiproRateLimitError exception."""

    def test_rate_limit_error_with_retry_after(self):
        """Test LiproRateLimitError stores retry_after value."""
        from custom_components.lipro.core.api import LiproRateLimitError

        error = LiproRateLimitError("Rate limited", retry_after=30.0)
        assert error.retry_after == 30.0
        assert str(error) == "Rate limited"
        assert error.code == 429

    def test_rate_limit_error_without_retry_after(self):
        """Test LiproRateLimitError without retry_after."""
        from custom_components.lipro.core.api import LiproRateLimitError

        error = LiproRateLimitError("Rate limited")
        assert error.retry_after is None

    def test_rate_limit_error_is_api_error(self):
        """Test LiproRateLimitError inherits from LiproApiError."""
        from custom_components.lipro.core.api import LiproRateLimitError

        error = LiproRateLimitError("Rate limited")
        assert isinstance(error, LiproApiError)


class TestLiproClientCommandsExtended:
    """Extended tests for command sending."""

    @pytest.mark.asyncio
    async def test_send_command_with_properties(self):
        """Test sending command with properties."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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

    @pytest.mark.asyncio
    async def test_send_group_command_retries_on_device_busy(self):
        """Transient busy response should be retried for group commands."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with (
            patch.object(
                client, "_iot_request", new_callable=AsyncMock
            ) as mock_request,
            patch.object(
                client, "_throttle_change_state", new_callable=AsyncMock
            ) as throttle,
            patch(
                "custom_components.lipro.core.api.asyncio.sleep", new_callable=AsyncMock
            ) as sleep,
        ):
            mock_request.side_effect = [
                LiproApiError("设备繁忙，请稍候操作", 250001),
                {"pushSuccess": True},
            ]

            result = await client.send_group_command(
                group_id="mesh_group_10001",
                command="CHANGE_STATE",
                device_type=1,
                properties=[{"key": "brightness", "value": "60"}],
            )

        assert result == {"pushSuccess": True}
        assert mock_request.await_count == 2
        assert throttle.await_count == 2
        sleep.assert_awaited_once()
        assert client._change_state_min_interval["mesh_group_10001"] > 0.2
        assert "mesh_group_10001" not in client._change_state_busy_count

    @pytest.mark.asyncio
    async def test_send_command_retries_on_device_busy_message(self):
        """Busy-message variants should also trigger retry for single device."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with (
            patch.object(
                client, "_iot_request", new_callable=AsyncMock
            ) as mock_request,
            patch.object(
                client, "_throttle_change_state", new_callable=AsyncMock
            ) as throttle,
            patch(
                "custom_components.lipro.core.api.asyncio.sleep", new_callable=AsyncMock
            ) as sleep,
        ):
            mock_request.side_effect = [
                LiproApiError("Device busy, please retry", None),
                {"pushSuccess": True},
            ]

            result = await client.send_command(
                device_id="03ab5ccd7caaaaaa",
                command="POWER_ON",
                device_type=1,
            )

        assert result == {"pushSuccess": True}
        assert mock_request.await_count == 2
        assert throttle.await_count == 2
        sleep.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_send_command_non_busy_error_does_not_retry(self):
        """Non-busy errors should propagate without retry."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with (
            patch.object(
                client, "_iot_request", new_callable=AsyncMock
            ) as mock_request,
            patch.object(
                client, "_throttle_change_state", new_callable=AsyncMock
            ) as throttle,
            patch(
                "custom_components.lipro.core.api.asyncio.sleep", new_callable=AsyncMock
            ) as sleep,
        ):
            mock_request.side_effect = LiproApiError("Device offline", 140003)

            with pytest.raises(LiproApiError, match="Device offline"):
                await client.send_command(
                    device_id="03ab5ccd7caaaaaa",
                    command="POWER_ON",
                    device_type=1,
                )

        assert mock_request.await_count == 1
        assert throttle.await_count == 1
        sleep.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_send_group_command_busy_retry_exhausted_raises(self):
        """Busy retries should stop after the configured max attempts."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        with (
            patch.object(
                client, "_iot_request", new_callable=AsyncMock
            ) as mock_request,
            patch.object(
                client, "_throttle_change_state", new_callable=AsyncMock
            ) as throttle,
            patch(
                "custom_components.lipro.core.api.asyncio.sleep", new_callable=AsyncMock
            ) as sleep,
        ):
            mock_request.side_effect = LiproApiError("设备繁忙，请稍候操作", "250001")

            with pytest.raises(LiproApiError, match="设备繁忙"):
                await client.send_group_command(
                    group_id="mesh_group_10001",
                    command="CHANGE_STATE",
                    device_type=1,
                    properties=[{"key": "brightness", "value": "80"}],
                )

        # Initial try + 3 retries
        assert mock_request.await_count == 4
        assert throttle.await_count == 4
        assert sleep.await_count == 3

    @pytest.mark.asyncio
    async def test_throttle_change_state_waits_for_same_target(self):
        """CHANGE_STATE should pace repeated sends to the same target."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client._last_change_state_at["mesh_group_10001"] = 100.0

        with (
            patch(
                "custom_components.lipro.core.api.time.monotonic",
                side_effect=[100.05, 100.25],
            ),
            patch(
                "custom_components.lipro.core.api.asyncio.sleep", new_callable=AsyncMock
            ) as sleep,
        ):
            await client._throttle_change_state("mesh_group_10001", "CHANGE_STATE")

        sleep.assert_awaited_once()
        wait_time = sleep.await_args.args[0]
        assert 0 < wait_time <= 0.2
        assert client._last_change_state_at["mesh_group_10001"] == 100.25

    @pytest.mark.asyncio
    async def test_throttle_change_state_skips_non_change_state(self):
        """Non-CHANGE_STATE commands should not be rate-limited."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client._last_change_state_at["mesh_group_10001"] = 100.0

        with patch(
            "custom_components.lipro.core.api.asyncio.sleep", new_callable=AsyncMock
        ) as sleep:
            await client._throttle_change_state("mesh_group_10001", "POWER_ON")

        sleep.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_record_change_state_busy_increases_adaptive_interval(self):
        """Busy responses should increase per-target CHANGE_STATE interval."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        interval1, count1 = await client._record_change_state_busy(
            "mesh_group_10001", "CHANGE_STATE"
        )
        interval2, count2 = await client._record_change_state_busy(
            "mesh_group_10001", "CHANGE_STATE"
        )

        assert interval1 > 0.2
        assert interval2 > interval1
        assert count1 == 1
        assert count2 == 2
        assert client._change_state_busy_count["mesh_group_10001"] == 2

    @pytest.mark.asyncio
    async def test_record_change_state_success_recovers_adaptive_interval(self):
        """Successful CHANGE_STATE should recover interval and clear busy count."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        await client._record_change_state_busy("mesh_group_10001", "CHANGE_STATE")
        busy_interval = client._change_state_min_interval["mesh_group_10001"]

        await client._record_change_state_success("mesh_group_10001", "CHANGE_STATE")
        recovered_interval = client._change_state_min_interval["mesh_group_10001"]

        assert recovered_interval >= 0.2
        assert recovered_interval < busy_interval
        assert "mesh_group_10001" not in client._change_state_busy_count

    @pytest.mark.asyncio
    async def test_record_change_state_busy_skips_non_change_state(self):
        """Non-CHANGE_STATE command should not alter adaptive pacing caches."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        interval, count = await client._record_change_state_busy(
            "mesh_group_10001", "POWER_ON"
        )

        assert interval == 0.2
        assert count == 0
        assert client._change_state_min_interval == {}
        assert client._change_state_busy_count == {}


class TestLiproClientIotRequest:
    """Tests for IoT API request handling."""

    @pytest.mark.asyncio
    async def test_iot_request_no_access_token(self):
        """Test IoT request fails without access token."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        # No tokens set

        with pytest.raises(LiproAuthError, match="No access token"):
            await client._iot_request("/test", {})

    @pytest.mark.asyncio
    async def test_iot_request_auth_error_codes(self):
        """Test IoT request handles various auth error codes."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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


class TestLiproClientSchedules:
    """Tests for schedule API response parsing."""

    @pytest.mark.asyncio
    async def test_get_device_schedules_mesh_uses_ble_endpoint_and_parses_schedule_json(
        self,
    ):
        """Mesh schedule GET should use BLE endpoint and normalize scheduleJson."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
    async def test_get_device_schedules_mesh_parses_rich_schedule_json_variant(self):
        """Mesh GET should tolerate app-style rich scheduleJson payload."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        gateway_id = "03ab0000000000a1"
        row = {
            "id": 1,
            "active": True,
            "scheduleJson": (
                '{"type":"daily","time":"08:30","weekDays":[1,2],'
                '"action":{"command":"power","properties":[{"key":"power","value":0}]}}'
            ),
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

        assert result[0]["schedule"] == {"days": [1, 2], "time": [30600], "evt": [1]}

    @pytest.mark.asyncio
    async def test_add_device_schedule_mesh_uses_ble_endpoint(self):
        """Mesh schedule ADD should call BLE endpoint with scheduleJson payload."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        gateway_id = "03ab0000000000a1"
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
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
        assert len(mock_request.await_args_list) == 2
        add_call = mock_request.await_args_list[0]
        assert add_call.args[0] == PATH_BLE_SCHEDULE_ADD
        assert add_call.args[1]["deviceId"] == gateway_id
        assert add_call.args[1]["id"] == 0
        assert add_call.args[1]["active"] is True
        assert json.loads(add_call.args[1]["scheduleJson"]) == {
            "days": [1, 2, 3],
            "time": [28800, 61200],
            "evt": [0, 1],
        }
        assert mock_request.await_args_list[1].args == (
            PATH_BLE_SCHEDULE_GET,
            {"deviceId": gateway_id, "deviceType": "mesh"},
        )

    @pytest.mark.asyncio
    async def test_delete_device_schedules_mesh_uses_ble_endpoint(self):
        """Mesh schedule DELETE should call BLE delete endpoint."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
    async def test_get_device_schedules_accepts_list_response(self):
        """Schedule GET should accept list payload returned by real API."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        rows = [{"id": 1, "active": True, "schedule": {"days": [1], "time": [3600]}}]
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = rows

            result = await client.get_device_schedules("mesh_group_10001", 9)

        mock_request.assert_awaited_once_with(
            PATH_SCHEDULE_GET,
            {
                "deviceId": "mesh_group_10001",
                "deviceType": client._to_device_type_hex(9),
            },
        )
        assert result == rows

    @pytest.mark.asyncio
    async def test_get_device_schedules_accepts_dict_timings_response(self):
        """Schedule GET should also support wrapped timings payload."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        rows = [{"id": 2, "active": False, "schedule": {"days": [2], "time": [7200]}}]
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"timings": rows}

            result = await client.get_device_schedules("mesh_group_10001", 9)

        assert result == rows

    @pytest.mark.asyncio
    async def test_add_device_schedule_accepts_list_response(self):
        """Schedule ADD should accept list payload variants."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        rows = [{"id": 3, "active": True, "schedule": {"days": [3], "time": [10800]}}]
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = rows

            result = await client.add_device_schedule(
                "mesh_group_10001",
                9,
                [1, 2, 3],
                [3600],
                [0],
            )

        assert result == rows

    @pytest.mark.asyncio
    async def test_delete_device_schedules_accepts_data_wrapper(self):
        """Schedule DELETE should accept data-wrapped rows."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        rows = [{"id": 4, "active": True, "schedule": {"days": [1], "time": [0]}}]
        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"data": rows}

            result = await client.delete_device_schedules(
                "mesh_group_10001",
                9,
                [4],
            )

        assert result == rows

    @pytest.mark.asyncio
    async def test_get_device_schedules_invalid_payload_returns_empty(self):
        """Unexpected schedule payload should degrade to empty list."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"status": "ok"}

            result = await client.get_device_schedules("mesh_group_10001", 9)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_device_schedules_prefers_ble_for_non_mesh_device(self):
        """Non-mesh schedule GET should prefer BLE endpoint when IoT ID is valid."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"timings": []}

            await client.get_device_schedules("03ab5ccd7caaaaaa", 1)

        mock_request.assert_awaited_once_with(
            PATH_BLE_SCHEDULE_GET,
            {"deviceId": "03ab5ccd7caaaaaa", "deviceType": "mesh"},
        )

    @pytest.mark.asyncio
    async def test_get_device_schedules_ble_invalid_param_falls_back_to_standard(self):
        """When BLE GET returns invalid-param, client should fallback to standard GET."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                LiproApiError("invalid", "100000"),
                {"timings": []},
            ]

            result = await client.get_device_schedules("03ab5ccd7caaaaaa", 1)

        assert result == []
        assert mock_request.await_args_list[0].args == (
            PATH_BLE_SCHEDULE_GET,
            {"deviceId": "03ab5ccd7caaaaaa", "deviceType": "mesh"},
        )
        assert mock_request.await_args_list[1].args == (
            PATH_SCHEDULE_GET,
            {
                "deviceId": "03ab5ccd7caaaaaa",
                "deviceType": client._to_device_type_hex(1),
            },
        )

    @pytest.mark.asyncio
    async def test_add_delete_schedule_ble_invalid_param_falls_back_to_standard(self):
        """ADD/DELETE should fallback to standard endpoints when BLE path is rejected."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                LiproApiError("invalid", "100000"),
                {"timings": []},
                LiproApiError("invalid", "100000"),
                {"timings": []},
            ]

            add_result = await client.add_device_schedule(
                "03ab5ccd7caaaaaa",
                1,
                [1],
                [3600],
                [0],
            )
            delete_result = await client.delete_device_schedules(
                "03ab5ccd7caaaaaa",
                1,
                [1],
            )

        assert add_result == []
        assert delete_result == []
        assert mock_request.await_args_list[1].args[0] == PATH_SCHEDULE_ADD
        assert mock_request.await_args_list[3].args[0] == PATH_SCHEDULE_DELETE


class TestLiproClientBizId:
    """Tests for biz_id handling."""

    def test_biz_id_stored(self):
        """Test that biz_id is stored when setting tokens."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens(
            access_token="access",
            refresh_token="refresh",
            user_id=123,
            biz_id="lip_biz001",
        )

        assert client._biz_id == "lip_biz001"

    def test_biz_id_default(self):
        """Test that biz_id defaults to None."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        assert client._biz_id is None


class TestExtractDataList:
    """Tests for _extract_data_list static method."""

    def test_list_input(self):
        """Test with list input returns as-is."""
        data = [{"deviceId": "abc"}, {"deviceId": "def"}]
        assert LiproClient._extract_data_list(data) == data

    def test_dict_with_data_key(self):
        """Test with dict containing 'data' key."""
        data = {"data": [{"deviceId": "abc"}]}
        assert LiproClient._extract_data_list(data) == [{"deviceId": "abc"}]

    def test_dict_with_non_list_data_key(self):
        """Test with non-list 'data' key returns empty list."""
        data = {"data": {"deviceId": "abc"}}
        assert LiproClient._extract_data_list(data) == []

    def test_dict_without_data_key(self):
        """Test with dict missing 'data' key returns empty list."""
        assert LiproClient._extract_data_list({"status": "ok"}) == []

    def test_none_input(self):
        """Test with None returns empty list."""
        assert LiproClient._extract_data_list(None) == []

    def test_string_input(self):
        """Test with string returns empty list."""
        assert LiproClient._extract_data_list("unexpected") == []


class TestIsRetriableDeviceError:
    """Tests for _is_retriable_device_error static method."""

    def test_error_140003_int(self):
        """Test error code 140003 (int) is retriable."""
        assert LiproClient._is_retriable_device_error(LiproApiError("offline", 140003))

    def test_error_140003_str(self):
        """Test error code '140003' (str) is retriable."""
        assert LiproClient._is_retriable_device_error(
            LiproApiError("offline", "140003")
        )

    def test_error_140003_str_with_spaces(self):
        """Test space-padded retriable code is recognized."""
        assert LiproClient._is_retriable_device_error(
            LiproApiError("offline", " 140003 ")
        )

    def test_error_140101_int(self):
        """Test error code 140101 (int) is retriable."""
        assert LiproClient._is_retriable_device_error(
            LiproApiError("no permission", 140101)
        )

    def test_error_140101_str(self):
        """Test error code '140101' (str) is retriable."""
        assert LiproClient._is_retriable_device_error(
            LiproApiError("no permission", "140101")
        )

    def test_error_140101_str_with_spaces(self):
        """Test space-padded permission code is recognized."""
        assert LiproClient._is_retriable_device_error(
            LiproApiError("no permission", " 140101 ")
        )

    def test_error_140004_int(self):
        """Test error code 140004 (int) is retriable."""
        assert LiproClient._is_retriable_device_error(
            LiproApiError("device not connected", 140004)
        )

    def test_error_140004_str(self):
        """Test error code '140004' (str) is retriable."""
        assert LiproClient._is_retriable_device_error(
            LiproApiError("device not connected", "140004")
        )

    def test_error_140004_str_with_spaces(self):
        """Test space-padded 140004 code is recognized."""
        assert LiproClient._is_retriable_device_error(
            LiproApiError("device not connected", " 140004 ")
        )

    def test_error_140013_int(self):
        """Test error code 140013 (not found) is retriable."""
        assert LiproClient._is_retriable_device_error(
            LiproApiError("not found", 140013)
        )

    def test_error_140014_int(self):
        """Test error code 140014 (updating) is retriable."""
        assert LiproClient._is_retriable_device_error(
            LiproApiError("device updating", 140014)
        )

    def test_error_500_not_retriable(self):
        """Test error code 500 is not retriable."""
        assert not LiproClient._is_retriable_device_error(
            LiproApiError("server error", 500)
        )

    def test_error_none_not_retriable(self):
        """Test error with no code is not retriable."""
        assert not LiproClient._is_retriable_device_error(LiproApiError("unknown"))


class TestDeviceStatusFallback140101:
    """Tests for 140101 (no permission) fallback in device/group queries."""

    @pytest.mark.asyncio
    async def test_query_device_status_140101_fallback(self):
        """Test fallback to individual queries when batch fails with 140101."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        call_count = 0

        async def mock_request(path, body):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise LiproApiError("No permission", 140101)
            device_id = body["deviceIdList"][0]
            return [{"deviceId": device_id, "powerState": "1"}]

        with patch.object(client, "_iot_request", side_effect=mock_request):
            result = await client.query_device_status(
                ["03ab5ccd7cxxxxxx", "03ab5ccd7cyyyyyy"]
            )

            assert len(result) == 2
            assert call_count == 3

    @pytest.mark.asyncio
    async def test_query_mesh_group_status_140101_fallback(self):
        """Test fallback to individual queries when group batch fails with 140101."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        call_count = 0

        async def mock_request(path, body):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise LiproApiError("No permission", 140101)
            group_id = body["groupIdList"][0]
            return [{"groupId": group_id, "powerState": "1"}]

        with patch.object(client, "_iot_request", side_effect=mock_request):
            result = await client.query_mesh_group_status(
                ["mesh_group_10001", "mesh_group_10002"]
            )

            assert len(result) == 2
            assert call_count == 3


class TestDeviceStatusFallback140004:
    """Tests for 140004 (device not connected) fallback in queries."""

    @pytest.mark.asyncio
    async def test_query_device_status_140004_fallback(self):
        """Test fallback to individual queries when batch fails with 140004."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        call_count = 0

        async def mock_request(path, body):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise LiproApiError("Device not connected", 140004)
            device_id = body["deviceIdList"][0]
            return [{"deviceId": device_id, "powerState": "1"}]

        with patch.object(client, "_iot_request", side_effect=mock_request):
            result = await client.query_device_status(
                ["03ab5ccd7cxxxxxx", "03ab5ccd7cyyyyyy"]
            )

            assert len(result) == 2
            assert call_count == 3

    @pytest.mark.asyncio
    async def test_query_mesh_group_status_140004_fallback(self):
        """Test fallback to individual queries when group batch fails with 140004."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        call_count = 0

        async def mock_request(path, body):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise LiproApiError("Device not connected", 140004)
            group_id = body["groupIdList"][0]
            return [{"groupId": group_id, "powerState": "1"}]

        with patch.object(client, "_iot_request", side_effect=mock_request):
            result = await client.query_mesh_group_status(
                ["mesh_group_10001", "mesh_group_10002"]
            )

            assert len(result) == 2
            assert call_count == 3


class TestRetryAfterCap:
    """Tests for retry-after value capping."""

    def test_retry_after_capped_to_max(self):
        """Test that extremely large Retry-After values are capped."""
        from custom_components.lipro.const.api import MAX_RETRY_AFTER

        # Simulate the capping logic used in _smart_home_request / _iot_request
        retry_after = 999999.0
        wait_time = min(MAX_RETRY_AFTER, max(0.1, retry_after))
        assert wait_time == MAX_RETRY_AFTER
        assert wait_time == 60

    def test_retry_after_normal_value_not_capped(self):
        """Test that normal Retry-After values pass through."""
        from custom_components.lipro.const.api import MAX_RETRY_AFTER

        retry_after = 5.0
        wait_time = min(MAX_RETRY_AFTER, max(0.1, retry_after))
        assert wait_time == 5.0

    def test_retry_after_none_uses_exponential_backoff(self):
        """Test that None retry_after falls back to exponential backoff."""
        from custom_components.lipro.const.api import MAX_RETRY_AFTER

        for retry_count in range(3):
            wait_time = min(MAX_RETRY_AFTER, max(0.1, None or (2**retry_count)))
            assert wait_time == 2**retry_count

    def test_retry_after_negative_clamped_to_minimum(self):
        """Test that negative Retry-After is clamped to 0.1."""
        from custom_components.lipro.const.api import MAX_RETRY_AFTER

        retry_after = -10.0
        wait_time = min(MAX_RETRY_AFTER, max(0.1, retry_after))
        assert wait_time == 0.1

    @pytest.mark.asyncio
    async def test_429_with_huge_retry_after_is_capped(self):
        """Test that 429 with huge Retry-After doesn't hang (integration test)."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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


class TestLiproClientAdditionalBranchCoverage:
    """Additional branch-focused tests for API client helpers and edge paths."""

    def test_normalize_iot_device_id_non_string(self):
        """Non-string IDs should be rejected by IoT ID normalizer."""
        from custom_components.lipro.core.api import _normalize_iot_device_id

        assert _normalize_iot_device_id(123) is None

    def test_normalize_response_code_edge_variants(self):
        """Response-code normalization should handle bool/float/empty/string-edge values."""
        from custom_components.lipro.core.api import _normalize_response_code

        class _CodeObject:
            def __str__(self) -> str:
                return "  custom_code  "

        assert _normalize_response_code(True) == 1
        assert _normalize_response_code(2.0) == 2
        assert _normalize_response_code(2.5) == "2.5"
        assert _normalize_response_code("   ") is None
        assert _normalize_response_code("+-1") == "+-1"
        assert _normalize_response_code(_CodeObject()) == "custom_code"

    @pytest.mark.asyncio
    async def test_get_session_without_injected_session_raises(self):
        """Session access should fail fast when no aiohttp session is injected."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with pytest.raises(LiproConnectionError, match="No aiohttp session"):
            await client._get_session()

    def test_resolve_error_code_returns_none_for_empty_values(self):
        """Empty/zero code fields should normalize to None."""
        assert LiproClient._resolve_error_code(None, 0) is None

    def test_is_command_busy_error_false_for_empty_message(self):
        """Empty error message with non-busy code should not be treated as busy."""
        assert LiproClient._is_command_busy_error(LiproApiError("", 500)) is False

    def test_enforce_command_pacing_cache_limit_drops_oldest_targets(self):
        """Pacing cache should stay bounded by evicting oldest tracked targets."""
        from custom_components.lipro.core import api as api_module

        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        total = api_module._COMMAND_PACING_CACHE_MAX_SIZE + 2
        for idx in range(total):
            key = f"target_{idx}"
            client._last_change_state_at[key] = float(idx)
            client._change_state_min_interval[key] = 0.2
            client._change_state_busy_count[key] = 1

        client._enforce_command_pacing_cache_limit()

        assert (
            len(client._last_change_state_at)
            == api_module._COMMAND_PACING_CACHE_MAX_SIZE
        )
        assert (
            len(client._change_state_min_interval)
            == api_module._COMMAND_PACING_CACHE_MAX_SIZE
        )
        assert (
            len(client._change_state_busy_count)
            == api_module._COMMAND_PACING_CACHE_MAX_SIZE
        )
        assert "target_0" not in client._last_change_state_at
        assert "target_1" not in client._last_change_state_at

    @pytest.mark.asyncio
    async def test_record_change_state_busy_ignores_blank_target(self):
        """Blank target IDs should not mutate pacing state."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        interval, count = await client._record_change_state_busy("   ", "CHANGE_STATE")

        assert interval == 0.2
        assert count == 0
        assert client._change_state_min_interval == {}

    @pytest.mark.asyncio
    async def test_record_change_state_success_ignores_blank_target(self):
        """Blank target IDs should skip recovery logic safely."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client._change_state_min_interval["target"] = 0.6
        client._change_state_busy_count["target"] = 2

        await client._record_change_state_success("   ", "CHANGE_STATE")

        assert client._change_state_min_interval["target"] == 0.6
        assert client._change_state_busy_count["target"] == 2

    @pytest.mark.asyncio
    async def test_iot_request_with_busy_retry_non_mapping_success_returns_empty(self):
        """Busy-retry helper should normalize non-dict success payloads to empty dict."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = "ok"
            result = await client._iot_request_with_busy_retry(
                "/test",
                {},
                target_id="03ab5ccd7caaaaaa",
                command="POWER_ON",
            )

        assert result == {}

    @pytest.mark.asyncio
    async def test_throttle_change_state_ignores_blank_target(self):
        """Throttle should no-op when target is blank after normalization."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with patch(
            "custom_components.lipro.core.api.asyncio.sleep", new_callable=AsyncMock
        ) as sleep:
            await client._throttle_change_state("   ", "CHANGE_STATE")

        sleep.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_smart_home_request_requires_access_token_when_auth_enabled(self):
        """Authenticated smart-home requests should fail without access token."""
        session = MagicMock()
        session.closed = False
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000", session)

        with pytest.raises(LiproAuthError, match="No access token available"):
            await client._smart_home_request("/test", {"k": "v"}, require_auth=True)

    @pytest.mark.asyncio
    async def test_smart_home_request_typed_value_paths(self):
        """typedValue response should be unwrapped, including None fallback."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with (
            patch.object(
                client, "_execute_request", new_callable=AsyncMock
            ) as mock_exec,
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
            patch(
                "custom_components.lipro.core.api.asyncio.sleep", new_callable=AsyncMock
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        assert LiproClient._unwrap_iot_success_payload(payload) == payload

    @pytest.mark.asyncio
    async def test_handle_401_without_refresh_callback_returns_false(self):
        """Without callback, 401 handler should indicate no retry possible."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        assert await client._handle_401_with_refresh("access") is False

    @pytest.mark.asyncio
    async def test_handle_401_refresh_token_expired_bubbles(self):
        """Refresh-token-expired errors should propagate for reauth handling."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")
        client.set_token_refresh_callback(
            AsyncMock(side_effect=LiproRefreshTokenExpiredError("expired"))
        )

        with pytest.raises(LiproRefreshTokenExpiredError, match="expired"):
            await client._handle_401_with_refresh("access")

    @pytest.mark.asyncio
    async def test_handle_401_refresh_auth_error_returns_false(self):
        """Authentication errors during refresh should disable retry."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")
        client.set_token_refresh_callback(
            AsyncMock(side_effect=LiproAuthError("invalid"))
        )

        assert await client._handle_401_with_refresh("access") is False

    @pytest.mark.asyncio
    async def test_login_with_prehashed_password_keeps_hash(self):
        """login(password_is_hashed=True) should pass hash through unchanged."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_smart_home_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"access_token": "a_only"}
            with pytest.raises(
                LiproAuthError, match="missing access_token or refresh_token"
            ):
                await client.login("13800000000", "password")

    @pytest.mark.asyncio
    async def test_login_with_hash_delegates_to_login(self):
        """login_with_hash should delegate to login with hashed-password flag."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(client, "login", new_callable=AsyncMock) as mock_login:
            mock_login.return_value = {"access_token": "a"}
            await client.login_with_hash("13800000000", "hashed")

        mock_login.assert_awaited_once_with(
            "13800000000",
            "hashed",
            password_is_hashed=True,
        )

    @pytest.mark.asyncio
    async def test_refresh_access_token_missing_tokens_raises_auth_error(self):
        """Refresh endpoint response without token pair should raise auth error."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

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
    async def test_query_with_fallback_skips_failed_single_item_and_keeps_others(self):
        """Fallback query should continue after one single-item failure."""
        mock_request = AsyncMock()
        mock_request.side_effect = [
            LiproApiError("offline", 140003),
            LiproApiError("single fail", 500),
            {"data": [{"deviceId": "03ab5ccd7cbbbbbb"}]},
        ]

        result = await query_with_fallback_service(
            path="/query",
            body_key="deviceIdList",
            ids=["03ab5ccd7caaaaaa", "03ab5ccd7cbbbbbb"],
            item_name="device",
            iot_request=mock_request,
            extract_data_list=LiproClient._extract_data_list,
            is_retriable_device_error=lambda _: True,
            lipro_api_error=LiproApiError,
            normalize_response_code=lambda code: code,
            expected_offline_codes=(140003, "140003", 140004, "140004"),
            logger=MagicMock(),
        )

        assert result == [{"deviceId": "03ab5ccd7cbbbbbb"}]

    @pytest.mark.asyncio
    async def test_query_with_fallback_logs_summary_when_all_single_queries_fail(self):
        """When fallback yields no rows due to all single failures, emit one summary warning."""
        mock_request = AsyncMock()
        mock_request.side_effect = [
            LiproApiError("offline", 140003),
            LiproApiError("single fail", 500),
            LiproApiError("single fail", 500),
        ]
        mock_logger = MagicMock()

        result = await query_with_fallback_service(
            path="/query",
            body_key="deviceIdList",
            ids=["03ab5ccd7caaaaaa", "03ab5ccd7cbbbbbb"],
            item_name="device",
            iot_request=mock_request,
            extract_data_list=LiproClient._extract_data_list,
            is_retriable_device_error=lambda _: True,
            lipro_api_error=LiproApiError,
            normalize_response_code=lambda code: code,
            expected_offline_codes=(140003, "140003", 140004, "140004"),
            logger=mock_logger,
        )

        assert result == []
        assert any(
            "fallback returned no data" in str(call.args[0])
            and call.args[1] == "device"
            and call.args[2] == 2
            and call.args[3] == 2
            and call.args[4] == 140003
            for call in mock_logger.warning.call_args_list
        )

    @pytest.mark.asyncio
    async def test_query_connect_status_empty_input_returns_empty_dict(self):
        """Empty connect-status request should short-circuit."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        assert await client.query_connect_status([]) == {}

    @pytest.mark.asyncio
    async def test_query_connect_status_wrapped_non_dict_data_returns_empty(self):
        """Wrapped payload with non-dict data should degrade to empty result."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"code": "0000", "data": []}
            result = await client.query_connect_status(["03ab5ccd7caaaaaa"])

        assert result == {}

    @pytest.mark.asyncio
    async def test_query_connect_status_api_error_returns_empty(self):
        """Connect-status API errors should be converted to empty results."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = LiproApiError("down", 500)
            result = await client.query_connect_status(["03ab5ccd7caaaaaa"])

        assert result == {}

    @pytest.mark.asyncio
    async def test_get_mqtt_config_429_retries_then_succeeds(self):
        """MQTT config endpoint should retry once on 429."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with (
            patch.object(
                client, "_execute_request", new_callable=AsyncMock
            ) as mock_exec,
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
            patch(
                "custom_components.lipro.core.api.asyncio.sleep", new_callable=AsyncMock
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
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

    def test_coerce_int_list_skips_bool_and_invalid_numeric_string(self):
        """Integer-list coercion should ignore bool and malformed signed numbers."""
        result = LiproClient._coerce_int_list([True, 1, 2.0, 2.5, " 3 ", "+-1", "abc"])
        assert result == [1, 2, 3]

    def test_parse_mesh_schedule_json_edge_cases(self):
        """Mesh schedule parser should handle blank/invalid/wrapped/mismatched payloads."""
        empty = {"days": [], "time": [], "evt": []}
        assert LiproClient._parse_mesh_schedule_json("   ") == empty
        assert LiproClient._parse_mesh_schedule_json("{bad-json}") == empty
        assert LiproClient._parse_mesh_schedule_json(123) == empty

        wrapped = LiproClient._parse_mesh_schedule_json(
            {"schedule": {"days": [1], "time": [3600], "evt": [0]}}
        )
        assert wrapped == {"days": [1], "time": [3600], "evt": [0]}

        action_payload = LiproClient._parse_mesh_schedule_json(
            {
                "weekDays": [1],
                "time": "08:30",
                "action": {
                    "command": "power",
                    "properties": [1, {"key": "power", "value": 1}],
                },
            }
        )
        assert action_payload == {"days": [1], "time": [30600], "evt": [0]}

        mismatch_payload = LiproClient._parse_mesh_schedule_json(
            {"days": [1], "time": [3600], "evt": []}
        )
        assert mismatch_payload == {"days": [1], "time": [], "evt": []}

        truncate_payload = LiproClient._parse_mesh_schedule_json(
            {"days": [1], "time": [3600, 7200], "evt": [1]}
        )
        assert truncate_payload == {"days": [1], "time": [3600], "evt": [1]}

    def test_normalize_mesh_timing_rows_skips_non_mapping_rows(self):
        """Row normalizer should skip non-dict rows while normalizing valid entries."""
        normalized = LiproClient._normalize_mesh_timing_rows(
            [
                1,
                {
                    "id": 1,
                    "active": 1,
                    "scheduleJson": '{"days":[1],"time":[3600],"evt":[0]}',
                },
            ],
            fallback_device_id="03ab0000000000a1",
        )

        assert len(normalized) == 1
        assert normalized[0]["deviceId"] == "03ab0000000000a1"
        assert normalized[0]["schedule"] == {"days": [1], "time": [3600], "evt": [0]}

    @pytest.mark.asyncio
    async def test_get_mesh_schedules_by_candidates_empty_returns_empty(self):
        """Mesh schedule helper should return empty list for empty candidates."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        assert await client._get_mesh_schedules_by_candidates([]) == []

    @pytest.mark.asyncio
    async def test_get_mesh_schedules_by_candidates_auth_error_bubbles(self):
        """Mesh schedule helper should re-raise auth errors immediately."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = LiproAuthError("auth")
            with pytest.raises(LiproAuthError, match="auth"):
                await client._get_mesh_schedules_by_candidates(["03ab0000000000a1"])

    @pytest.mark.asyncio
    async def test_get_mesh_schedules_by_candidates_total_failure_behaviors(self):
        """Mesh schedule helper should raise or return [] based on total-failure flag."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                LiproApiError("bad1", 500),
                LiproApiError("bad2", 501),
            ]
            with pytest.raises(LiproApiError, match="bad2"):
                await client._get_mesh_schedules_by_candidates(
                    ["03ab0000000000a1", "03ab0000000000a2"],
                    raise_on_total_failure=True,
                )

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                LiproApiError("bad1", 500),
                LiproApiError("bad2", 501),
            ]
            result = await client._get_mesh_schedules_by_candidates(
                ["03ab0000000000a1", "03ab0000000000a2"],
                raise_on_total_failure=False,
            )
        assert result == []

    @pytest.mark.asyncio
    async def test_add_device_schedule_validates_times_events_length(self):
        """Schedule add should reject mismatched times/events arrays."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with pytest.raises(ValueError, match="same length"):
            await client.add_device_schedule("03ab5ccd7caaaaaa", 1, [1], [3600], [0, 1])

    @pytest.mark.asyncio
    async def test_add_device_schedule_mesh_error_paths(self):
        """Mesh schedule add should re-raise auth and last API error."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = LiproAuthError("reauth")
            with pytest.raises(LiproAuthError, match="reauth"):
                await client.add_device_schedule(
                    "mesh_group_10001",
                    9,
                    [1],
                    [3600],
                    [0],
                    mesh_gateway_id="03ab0000000000a1",
                )

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                LiproApiError("bad1", 500),
                LiproApiError("bad2", 501),
            ]
            with pytest.raises(LiproApiError, match="bad2"):
                await client.add_device_schedule(
                    "mesh_group_10001",
                    9,
                    [1],
                    [3600],
                    [0],
                    mesh_gateway_id="03ab0000000000a1",
                    mesh_member_ids=["03ab0000000000a2"],
                )

    @pytest.mark.asyncio
    async def test_delete_device_schedule_mesh_error_paths(self):
        """Mesh schedule delete should re-raise auth and last API error when all fail."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = LiproAuthError("reauth")
            with pytest.raises(LiproAuthError, match="reauth"):
                await client.delete_device_schedules(
                    "mesh_group_10001",
                    9,
                    [1],
                    mesh_gateway_id="03ab0000000000a1",
                )

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                LiproApiError("bad1", 500),
                LiproApiError("bad2", 501),
            ]
            with pytest.raises(LiproApiError, match="bad2"):
                await client.delete_device_schedules(
                    "mesh_group_10001",
                    9,
                    [1],
                    mesh_gateway_id="03ab0000000000a1",
                    mesh_member_ids=["03ab0000000000a2"],
                )

    def test_resolve_mesh_schedule_candidates_for_group_non_mesh_returns_none(self):
        """Mesh candidate resolver should skip non-mesh device IDs."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        assert (
            client._resolve_mesh_schedule_candidates_for_group("03ab5ccd7caaaaaa")
            is None
        )

    def test_resolve_mesh_schedule_candidates_for_group_mesh_returns_candidates(self):
        """Mesh candidate resolver should return ordered gateway/member IDs."""
        client = LiproClient("550e8400-e29b-41d4-a716-446655440000")
        assert client._resolve_mesh_schedule_candidates_for_group(
            "mesh_group_10001",
            mesh_gateway_id="03ab0000000000a1",
            mesh_member_ids=["03ab0000000000a2"],
        ) == ["03ab0000000000a1", "03ab0000000000a2"]
