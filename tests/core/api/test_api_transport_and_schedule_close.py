"""Client-close API regressions."""

from __future__ import annotations

from .conftest import LiproRestFacade, MagicMock, aiohttp, pytest


class TestLiproRestFacadeClose:
    """Tests for client cleanup."""

    @pytest.mark.asyncio
    async def test_close_clears_session(self):
        """Test close clears session reference."""
        session = MagicMock(spec=aiohttp.ClientSession)
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000", session)

        await client.close()

        # Session reference should be cleared (HA manages session lifecycle)
        assert client.session is None

    @pytest.mark.asyncio
    async def test_close_external_session(self):
        """Test close does not close HA-managed session."""
        session = MagicMock(spec=aiohttp.ClientSession)
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000", session)

        await client.close()

        # External session should not be closed by client
        session.close.assert_not_called()
