"""Tests for Lipro API client."""

from __future__ import annotations

import hashlib
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproClient,
    LiproConnectionError,
    _mask_sensitive_data,
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

        refresh_callback = AsyncMock()
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
