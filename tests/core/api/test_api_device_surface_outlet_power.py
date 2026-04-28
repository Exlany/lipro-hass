"""Outlet-power API surface regressions."""

from __future__ import annotations

from .conftest import (
    PATH_QUERY_OUTLET_POWER,
    AsyncMock,
    LiproApiError,
    LiproRestFacade,
    patch,
    pytest,
)


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
