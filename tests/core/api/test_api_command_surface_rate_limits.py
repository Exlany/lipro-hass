"""Topicized API regression coverage extracted from `tests/core/api/test_api.py` (test_api_command_surface)."""

from __future__ import annotations

from .test_api import AsyncMock, LiproRestFacade, MagicMock, patch, pytest


class TestLiproRestFacade429Handling:
    """Tests for 429 rate limit handling."""

    @pytest.mark.asyncio
    async def test_429_with_retry_after_seconds(self):
        """Test 429 handling with Retry-After header in seconds."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        call_count = 0

        async def mock_execute_request(request_ctx, path):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call returns 429
                return (
                    429,
                    {"code": 429, "message": "Too Many Requests"},
                    {"Retry-After": "0.01"},
                )
            # Second call succeeds (code 200 is RESPONSE_SUCCESS)
            return 200, {"code": 200, "value": {"devices": []}}, {}

        with (
            patch.object(client, "_execute_request", side_effect=mock_execute_request),
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
        ):
            mock_session.return_value = MagicMock()
            result = await client.get_devices()

        assert call_count == 2
        assert "devices" in result

    @pytest.mark.asyncio
    async def test_429_max_retries_exceeded(self):
        """Test 429 raises error after max retries."""
        from custom_components.lipro.core.api import LiproRateLimitError

        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        async def mock_execute_request(request_ctx, path):
            # Always return 429
            return (
                429,
                {"code": 429, "message": "Too Many Requests"},
                {"Retry-After": "0.01"},
            )

        with (
            patch.object(client, "_execute_request", side_effect=mock_execute_request),
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
        ):
            mock_session.return_value = MagicMock()
            with pytest.raises(
                LiproRateLimitError, match="Rate limited after 2 retries"
            ):
                await client.get_devices()


class TestLiproRestFacadeBizIdRateLimits:
    """Tests for biz_id handling."""

    @pytest.mark.asyncio
    async def test_429_with_huge_retry_after_is_capped(self):
        """Test that 429 with huge Retry-After doesn't hang (integration test)."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token", "refresh_token")

        call_count = 0

        async def mock_execute_request(request_ctx, path):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return (
                    429,
                    {"code": 429, "message": "Too Many Requests"},
                    {"Retry-After": "999999"},
                )
            return 200, {"code": 200, "value": {"devices": []}}, {}

        with (
            patch.object(client, "_execute_request", side_effect=mock_execute_request),
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
            patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
        ):
            mock_session.return_value = MagicMock()
            await client.get_devices()

        # Verify sleep was called with capped value (60), not 999999
        mock_sleep.assert_called_once()
        actual_wait = mock_sleep.call_args[0][0]
        assert actual_wait == 60.0


class TestLiproRestFacadeAdditionalRateLimitCoverage:
    """Additional branch-focused tests for API client helpers and edge paths."""

    @pytest.mark.asyncio
    async def test_iot_request_429_retries_then_succeeds(self):
        """IoT request should retry once on 429 and then return success payload."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with (
            patch.object(
                client, "_execute_request", new_callable=AsyncMock
            ) as mock_exec,
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
            patch(
                "custom_components.lipro.core.api.client_pacing.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            mock_session.return_value = MagicMock()
            mock_exec.side_effect = [
                (429, {"code": 429}, {"Retry-After": "0.01"}),
                (200, {"code": 200, "data": {"ok": True}}, {}),
            ]
            result = await client._iot_request("/iot", {"x": 1})

        assert result == {"ok": True}
        assert mock_exec.await_count == 2

    @pytest.mark.asyncio
    async def test_get_mqtt_config_429_retries_then_succeeds(self):
        """MQTT config endpoint should retry once on 429."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access", "refresh")

        with (
            patch.object(
                client, "_execute_request", new_callable=AsyncMock
            ) as mock_exec,
            patch.object(
                client, "_get_session", new_callable=AsyncMock
            ) as mock_session,
            patch(
                "custom_components.lipro.core.api.client_pacing.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            mock_session.return_value = MagicMock()
            mock_exec.side_effect = [
                (429, {"code": 429}, {"Retry-After": "0.01"}),
                (200, {"accessKey": "ak", "secretKey": "sk"}, {}),
            ]
            result = await client.get_mqtt_config()

        assert result == {"accessKey": "ak", "secretKey": "sk"}
        assert mock_exec.await_count == 2
