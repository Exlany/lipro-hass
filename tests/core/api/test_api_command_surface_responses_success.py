"""Success-code command-surface response assertions."""

from __future__ import annotations

from .conftest import (
    AsyncMock,
    LiproApiError,
    LiproAuthError,
    LiproRestFacade,
    MagicMock,
    patch,
    pytest,
)


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
