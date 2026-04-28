"""Topicized API regression coverage extracted from `tests/core/api/test_api.py` (test_api_command_surface)."""

from __future__ import annotations

from custom_components.lipro.core.api.types import JsonObject

from .conftest import (
    AsyncMock,
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRestFacade,
    MagicMock,
    patch,
    pytest,
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

        assert client.biz_id == "lip_biz001"

    def test_biz_id_default(self):
        """Test that biz_id defaults to None."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        assert client.biz_id is None


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
    async def test_smart_home_request_public_wrapper_routes_through_request_gateway(
        self,
    ):
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
        payload: JsonObject = {"code": 200, "message": "ok"}
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
