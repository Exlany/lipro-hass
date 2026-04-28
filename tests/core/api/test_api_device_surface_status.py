"""Device-status API surface regressions."""

from __future__ import annotations

from .conftest import AsyncMock, LiproApiError, LiproRestFacade, patch, pytest


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
                "custom_components.lipro.core.api.endpoints.status._LOGGER.warning"
            ) as mock_warning,
            patch(
                "custom_components.lipro.core.api.endpoints.status._LOGGER.debug"
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
                "custom_components.lipro.core.api.endpoints.status._LOGGER.warning"
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
