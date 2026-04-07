"""Transport-boundary API regressions."""
from __future__ import annotations

from .conftest import AsyncMock, LiproRestFacade, patch, pytest


class TestLiproRestFacadeTransportBoundary:
    """Transport-boundary regressions for the public REST child façade."""

    @pytest.mark.asyncio
    async def test_execute_mapping_request_with_rate_limit_public_wrapper_uses_executor_boundary(self):
        """Public transport wrapper should preserve executor ownership and retry state."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        send_request = AsyncMock(return_value=(200, {"ok": True}, {}, "token"))
        expected = (200, {"ok": True}, "token")

        with patch.object(
            client, "_execute_mapping_request_with_rate_limit", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = expected
            result = await client.execute_mapping_request_with_rate_limit(
                path="/v2/test",
                retry_count=2,
                send_request=send_request,
            )

        assert result == expected
        mock_execute.assert_awaited_once_with(
            path="/v2/test",
            retry_count=2,
            send_request=send_request,
        )
