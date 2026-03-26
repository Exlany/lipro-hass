"""Connect-status API surface regressions."""
from __future__ import annotations

from .conftest import (
    PATH_QUERY_CONNECT_STATUS,
    AsyncMock,
    LiproRestFacade,
    patch,
    pytest,
)


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
