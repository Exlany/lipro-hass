"""Topicized API regression coverage extracted from `tests/core/api/test_api.py` (test_api_command_surface)."""

from __future__ import annotations

from .test_api import (
    AsyncMock,
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRestFacade,
    MagicMock,
    aiohttp,
    patch,
    pytest,
)


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

        assert client.biz_id == "lip_biz001"

    def test_biz_id_default(self):
        """Test that biz_id defaults to None."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        assert client.biz_id is None

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

    @pytest.mark.asyncio
    async def test_request_iot_mapping_public_wrapper_preserves_retry_context(self):
        """Public request_iot_mapping should forward retry context unchanged."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        expected = ({"ok": True}, "access_token")

        with patch.object(
            client, "_request_iot_mapping", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = expected
            result = await client.request_iot_mapping(
                "/iot",
                {"deviceId": "03ab5ccd7caaaaaa"},
                is_retry=True,
                retry_count=2,
            )

        assert result == expected
        mock_request.assert_awaited_once_with(
            "/iot",
            {"deviceId": "03ab5ccd7caaaaaa"},
            is_retry=True,
            retry_count=2,
        )

    @pytest.mark.asyncio
    async def test_request_iot_mapping_raw_public_wrapper_preserves_retry_context(self):
        """Public request_iot_mapping_raw should forward raw body and retry state."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        expected = ({"ok": True}, "access_token")

        with patch.object(
            client, "_request_iot_mapping_raw", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = expected
            result = await client.request_iot_mapping_raw(
                "/iot",
                '{"deviceId":"03ab5ccd7caaaaaa"}',
                is_retry=True,
                retry_count=1,
            )

        assert result == expected
        mock_request.assert_awaited_once_with(
            "/iot",
            '{"deviceId":"03ab5ccd7caaaaaa"}',
            is_retry=True,
            retry_count=1,
        )

    @pytest.mark.asyncio
    async def test_smart_home_request_public_wrapper_preserves_require_auth_false(self):
        """Public smart_home_request should preserve opt-out auth semantics."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with patch.object(
            client, "_smart_home_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"ok": True}
            result = await client.smart_home_request(
                "/test",
                {"scope": "all"},
                require_auth=False,
            )

        assert result == {"ok": True}
        mock_request.assert_awaited_once_with(
            "/test",
            {"scope": "all"},
            require_auth=False,
        )

    @pytest.mark.asyncio
    async def test_smart_home_request_public_wrapper_routes_through_request_gateway(self):
        """Public smart_home_request should route retry semantics via request gateway."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        expected = {"ok": True}

        with patch.object(
            client._request_gateway,
            "dispatch_retry_aware_call",
            new=AsyncMock(return_value=expected),
        ) as dispatch:
            result = await client.smart_home_request(
                "/test",
                {"scope": "all"},
                require_auth=False,
                is_retry=True,
                retry_count=3,
            )

        assert result == expected
        dispatch.assert_awaited_once_with(
            client._smart_home_request,
            "/test",
            {"scope": "all"},
            require_auth=False,
            is_retry=True,
            retry_count=3,
        )

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
