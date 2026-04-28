"""MQTT-config API regressions."""

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
