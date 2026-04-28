"""Mesh-group status API surface regressions."""

from __future__ import annotations

from .conftest import AsyncMock, LiproApiError, LiproRestFacade, patch, pytest


class TestLiproRestFacadeMeshGroupStatus:
    """Tests for mesh group status queries."""

    @pytest.mark.asyncio
    async def test_query_mesh_group_status_empty(self):
        """Test querying status with empty group list."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        result = await client.query_mesh_group_status([])

        assert result == []

    @pytest.mark.asyncio
    async def test_query_mesh_group_status_success(self):
        """Test querying mesh group status successfully."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
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
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
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
