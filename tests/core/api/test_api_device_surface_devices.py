"""Device-list API surface regressions."""
from __future__ import annotations

from .conftest import AsyncMock, LiproRestFacade, patch, pytest


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
