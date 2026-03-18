# ruff: noqa: F401
"""Tests for Lipro API client."""

from __future__ import annotations

import hashlib
import json
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.lipro.const.api import (
    PATH_BLE_SCHEDULE_ADD,
    PATH_BLE_SCHEDULE_DELETE,
    PATH_BLE_SCHEDULE_GET,
    PATH_FETCH_BODY_SENSOR_HISTORY,
    PATH_FETCH_DOOR_SENSOR_HISTORY,
    PATH_GET_CITY,
    PATH_QUERY_COMMAND_RESULT,
    PATH_QUERY_CONNECT_STATUS,
    PATH_QUERY_CONTROLLER_OTA,
    PATH_QUERY_OTA_INFO,
    PATH_QUERY_OTA_INFO_V2,
    PATH_QUERY_OUTLET_POWER,
    PATH_QUERY_USER_CLOUD,
    PATH_SCHEDULE_ADD,
    PATH_SCHEDULE_DELETE,
    PATH_SCHEDULE_GET,
)
from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRestFacade,
)


class TestLiproRestFacadeInit:
    """Tests for LiproRestFacade initialization."""

    def test_init_with_session(self):
        """Test initialization with provided session."""
        session = MagicMock(spec=aiohttp.ClientSession)
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000", session)

        assert client.phone_id == "550e8400-e29b-41d4-a716-446655440000"
        assert client.access_token is None
        assert client.refresh_token is None
        assert client.user_id is None

    def test_init_without_session(self):
        """Test initialization without session."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        assert client.phone_id == "550e8400-e29b-41d4-a716-446655440000"
        assert client._session is None


class TestLiproRestFacadeTokens:
    """Tests for token management."""

    def test_set_tokens(self):
        """Test setting tokens."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens(
            access_token="access123",
            refresh_token="refresh456",
            user_id=10001,
            biz_id="lip_biz001",
        )

        assert client.access_token == "access123"
        assert client.refresh_token == "refresh456"
        assert client.user_id == 10001

    def test_set_token_refresh_callback(self):
        """Test setting token refresh callback."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        callback = AsyncMock()
        client.set_token_refresh_callback(callback)

        assert client._on_token_refresh is callback


class TestLiproRestFacadeSignature:
    """Tests for API signature generation."""

    def test_smart_home_sign(self):
        """Test Smart Home API signature generation."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        sign = client._smart_home_sign()

        # Verify it's a valid MD5 hash (32 hex chars)
        assert len(sign) == 32
        assert all(c in "0123456789abcdef" for c in sign)

    def test_iot_sign(self):
        """Test IoT API signature generation."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("access_token_123", "refresh_token")

        sign = client._iot_sign(1234567890, '{"test": "body"}')

        # Verify it's a valid MD5 hash
        assert len(sign) == 32
        assert all(c in "0123456789abcdef" for c in sign)


class TestLiproRestFacadeLogin:
    """Tests for login functionality."""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Test successful login."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        mock_response = {
            "code": 0,
            "value": {
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "userId": 10001,
                "bizId": "lip_biz001",
                "phone": "13800000000",
                "userName": "Test User",
            },
        }

        with patch.object(
            client, "_smart_home_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response["value"]

            result = await client.login("13800000000", "password123")

            assert result["access_token"] == "new_access_token"
            assert result["refresh_token"] == "new_refresh_token"
            assert result["user_id"] == 10001
            assert client.access_token == "new_access_token"
            assert client.refresh_token == "new_refresh_token"

    @pytest.mark.asyncio
    async def test_login_password_hashed(self):
        """Test that password is MD5 hashed before sending."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        captured_data = {}

        async def capture_request(path, data, require_auth=True):
            captured_data.update(data)
            return {
                "access_token": "token",
                "refresh_token": "refresh",
                "userId": 1,
            }

        with patch.object(client, "_smart_home_request", side_effect=capture_request):
            await client.login("13800000000", "mypassword")

            # Verify password was MD5 hashed
            expected_hash = hashlib.md5(b"mypassword").hexdigest()
            assert captured_data.get("password") == expected_hash


class TestLiproRestFacadeRefreshToken:
    """Tests for token refresh functionality."""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self):
        """Test successful token refresh."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")
        client.set_tokens("old_access", "old_refresh")

        with patch.object(
            client, "_smart_home_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "userId": 10001,
            }

            result = await client.refresh_access_token()

            assert result["access_token"] == "new_access_token"
            assert client.access_token == "new_access_token"

    @pytest.mark.asyncio
    async def test_refresh_token_no_token(self):
        """Test refresh fails without refresh token."""
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000")

        with pytest.raises(LiproAuthError, match="No refresh token"):
            await client.refresh_access_token()
