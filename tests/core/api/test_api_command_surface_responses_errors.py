"""Error-handling command-surface response assertions."""

from __future__ import annotations

from .conftest import (
    AsyncMock,
    LiproApiError,
    LiproConnectionError,
    LiproRestFacade,
    MagicMock,
    aiohttp,
    patch,
    pytest,
)


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
