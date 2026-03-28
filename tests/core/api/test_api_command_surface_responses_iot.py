"""IoT-request command-surface response assertions."""

from __future__ import annotations

from .conftest import (
    AsyncMock,
    LiproAuthError,
    LiproRestFacade,
    MagicMock,
    patch,
    pytest,
)


class TestLiproRestFacadeIotRequest:
    """Tests for IoT API request handling."""

    @pytest.mark.asyncio
    async def test_iot_request_no_access_token(self):
        """Test IoT request fails without access token."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        # No tokens set

        with pytest.raises(LiproAuthError, match="No access token"):
            await client._iot_request("/test", {})

    @pytest.mark.asyncio
    async def test_iot_request_auth_error_codes(self):
        """Test IoT request handles various auth error codes."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        # Test different auth error codes
        for code in [401, "401", 2001, 2002]:
            with patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_get_session:
                mock_session = MagicMock()
                mock_response_obj = AsyncMock()
                mock_response_obj.status = 200
                mock_response_obj.headers = {}
                mock_response_obj.json = AsyncMock(
                    return_value={
                        "code": code,
                        "message": "Auth error",
                    }
                )
                mock_session.post = MagicMock(
                    return_value=AsyncMock(
                        __aenter__=AsyncMock(return_value=mock_response_obj)
                    )
                )
                mock_get_session.return_value = mock_session

                with pytest.raises(LiproAuthError):
                    await client._iot_request("/test", {})
