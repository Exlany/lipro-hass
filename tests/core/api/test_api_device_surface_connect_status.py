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
        requested_ids = [
            "03ab5ccd7caaa001",
            "03ab5ccd7caaa002",
            "03ab5ccd7caaa003",
            "03ab5ccd7caaa004",
            "03ab5ccd7caaa005",
            "03ab5ccd7caaa006",
            "03ab5ccd7caaa007",
            "03ab5ccd7caaa008",
            "03ab5ccd7caaa009",
            "03ab5ccd7caaa00a",
        ]

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {
                requested_ids[0]: True,
                requested_ids[1]: False,
                requested_ids[2]: 1,
                requested_ids[3]: 0,
                requested_ids[4]: "1",
                requested_ids[5]: "0",
                requested_ids[6]: "true",
                requested_ids[7]: "false",
                requested_ids[8]: "yes",
                requested_ids[9]: "off",
                "03ab5ccd7cfffffe": True,
            }

            result = await client.query_connect_status(requested_ids)

        assert result == {
            requested_ids[0]: True,
            requested_ids[1]: False,
            requested_ids[2]: True,
            requested_ids[3]: False,
            requested_ids[4]: True,
            requested_ids[5]: False,
            requested_ids[6]: True,
            requested_ids[7]: False,
            requested_ids[8]: True,
            requested_ids[9]: False,
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
        requested_ids = [
            "03ab5ccd7cbbb001",
            "03ab5ccd7cbbb002",
            "03ab5ccd7cbbb003",
        ]

        with patch.object(
            client, "_iot_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {
                requested_ids[0]: "offline",
                requested_ids[1]: {"status": "up"},
                requested_ids[2]: None,
                "03ab5ccd7cfffffd": "1",
            }

            result = await client.query_connect_status(requested_ids)

        assert result == {
            requested_ids[0]: False,
            requested_ids[1]: False,
            requested_ids[2]: False,
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
