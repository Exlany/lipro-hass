"""Tests for Lipro authentication manager."""

from __future__ import annotations

import asyncio
import logging
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api import (
    LiproAuthError,
    LiproRefreshTokenExpiredError,
)
from custom_components.lipro.core.auth import LiproAuthManager
from custom_components.lipro.core.protocol import LiproProtocolFacade


class TestLiproAuthManagerInit:
    """Tests for LiproAuthManager initialization."""

    def test_init(self):
        """Test initialization."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.access_token = None  # Explicitly set to None
        manager = LiproAuthManager(client)

        assert manager._client is client
        assert manager._token_expires_at == 0
        assert manager._phone is None
        assert manager._password is None
        assert manager.is_authenticated is False

    def test_init_registers_callback(self):
        """Test that init registers token refresh callback."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.access_token = None

        LiproAuthManager(client)

        client.set_token_refresh_callback.assert_called_once()

    def test_notify_tokens_updated_callback_failure_is_suppressed(self, caplog):
        """Token-updated callback failures should not raise."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.access_token = None
        manager = LiproAuthManager(client)

        def _callback() -> None:
            raise RuntimeError("boom")

        manager.set_tokens_updated_callback(_callback)

        with caplog.at_level(logging.DEBUG):
            manager._notify_tokens_updated()

        assert "Token-updated callback failed" in caplog.text


class TestLiproAuthManagerCredentials:
    """Tests for credential management."""

    def test_set_credentials(self):
        """Test setting credentials always stores MD5 hash."""
        client = MagicMock(spec=LiproProtocolFacade)
        manager = LiproAuthManager(client)

        manager.set_credentials("13800000000", "password123")

        assert manager._phone == "13800000000"
        # Password should be stored as MD5 hash, not plaintext
        import hashlib

        expected_hash = hashlib.md5(b"password123", usedforsecurity=False).hexdigest()
        assert manager._password == expected_hash
        assert manager._password_is_hashed is True

    def test_set_tokens(self):
        """Test setting tokens."""
        client = MagicMock(spec=LiproProtocolFacade)
        manager = LiproAuthManager(client)

        manager.set_tokens(
            access_token="access123",
            refresh_token="refresh456",
            user_id=10001,
            expires_at=1234567890.0,
        )

        client.set_tokens.assert_called_once_with(
            "access123", "refresh456", 10001, None
        )
        assert manager._token_expires_at == 1234567890.0

    def test_set_tokens_auto_expiry(self):
        """Test setting tokens with auto-calculated expiry."""
        client = MagicMock(spec=LiproProtocolFacade)
        manager = LiproAuthManager(client)

        before = time.time()
        manager.set_tokens("access", "refresh")
        after = time.time()

        # Expiry should be set to current time + default expiry
        assert manager._token_expires_at >= before
        assert manager._token_expires_at <= after + manager._current_expiry_seconds

    def test_set_tokens_does_not_mark_recent_refresh(self):
        """Restored tokens should not suppress first runtime 401 refresh."""
        client = MagicMock(spec=LiproProtocolFacade)
        manager = LiproAuthManager(client)

        manager.set_tokens("access", "refresh")

        assert manager._last_refresh_time == 0.0


class TestLiproAuthManagerLogin:
    """Tests for login functionality."""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Test successful login."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.login = AsyncMock(
            return_value={
                "access_token": "new_access",
                "refresh_token": "new_refresh",
                "user_id": 10001,
            }
        )

        manager = LiproAuthManager(client)

        result = await manager.login("13800000000", "password")

        assert result.access_token == "new_access"
        assert result.refresh_token == "new_refresh"
        assert result.expires_at is not None
        assert manager._phone == "13800000000"
        assert manager._password_is_hashed is True

    @pytest.mark.asyncio
    async def test_login_resets_expiry(self):
        """Test that login resets adaptive expiry."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.login = AsyncMock(
            return_value={
                "access_token": "token",
                "refresh_token": "refresh",
                "user_id": 1,
            }
        )

        manager = LiproAuthManager(client)
        manager._current_expiry_seconds = 100  # Reduced from previous 401s

        await manager.login("phone", "password")

        # Should be reset to default
        from custom_components.lipro.const.api import ACCESS_TOKEN_EXPIRY_SECONDS

        assert manager._current_expiry_seconds == ACCESS_TOKEN_EXPIRY_SECONDS


class TestLiproAuthManagerRefresh:
    """Tests for token refresh functionality."""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self):
        """Test successful token refresh."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.refresh_access_token = AsyncMock(
            return_value={
                "access_token": "new_access",
                "refresh_token": "new_refresh",
                "user_id": 10001,
            }
        )

        manager = LiproAuthManager(client)

        result = await manager.refresh_token()

        assert result.access_token == "new_access"
        assert result.expires_at is not None

    @pytest.mark.asyncio
    async def test_refresh_token_expired_with_credentials(self):
        """Test refresh token expired triggers re-login."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.refresh_access_token = AsyncMock(
            side_effect=LiproAuthError("Token expired", 20002)
        )
        client.login = AsyncMock(
            return_value={
                "access_token": "new_access",
                "refresh_token": "new_refresh",
                "user_id": 10001,
            }
        )

        manager = LiproAuthManager(client)
        manager.set_credentials("phone", "password")

        result = await manager.refresh_token()

        # set_credentials hashes the password, so login is called with hash
        client.login.assert_called_once()
        call_args = client.login.call_args
        assert call_args[0][0] == "phone"
        assert call_args[1]["password_is_hashed"] is True
        assert result.access_token == "new_access"

    @pytest.mark.asyncio
    async def test_refresh_token_expired_no_credentials(self):
        """Test refresh token expired without credentials raises error."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.refresh_access_token = AsyncMock(
            side_effect=LiproAuthError("Token expired", 20002)
        )

        manager = LiproAuthManager(client)
        # No credentials set

        with pytest.raises(LiproRefreshTokenExpiredError):
            await manager.refresh_token()

    @pytest.mark.asyncio
    async def test_relogin_fails_with_invalid_credentials(self):
        """Test behavior when re-login fails due to invalid credentials (e.g., password changed)."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.refresh_access_token = AsyncMock(
            side_effect=LiproAuthError("Token expired", 20002)
        )
        # Re-login also fails (password was changed)
        client.login = AsyncMock(side_effect=LiproAuthError("Invalid credentials", 401))

        manager = LiproAuthManager(client)
        manager.set_credentials("phone", "old_password_hash", password_is_hashed=True)

        # Should propagate the login error
        with pytest.raises(LiproAuthError) as exc_info:
            await manager.refresh_token()

        assert exc_info.value.code == 401
        client.login.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_other_auth_error_with_credentials(self):
        """Test other auth errors trigger re-login."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.refresh_access_token = AsyncMock(
            side_effect=LiproAuthError("Some error", 999)
        )
        client.login = AsyncMock(
            return_value={
                "access_token": "new_access",
                "refresh_token": "new_refresh",
                "user_id": 10001,
            }
        )

        manager = LiproAuthManager(client)
        manager.set_credentials("phone", "password")

        result = await manager.refresh_token()

        client.login.assert_called_once()
        assert result.access_token == "new_access"


class TestLiproAuthManagerEnsureValidToken:
    """Tests for ensure_valid_token functionality."""

    @pytest.mark.asyncio
    async def test_ensure_valid_token_not_authenticated(self):
        """Test ensure_valid_token when not authenticated."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.access_token = None
        client.login = AsyncMock(
            return_value={
                "access_token": "token",
                "refresh_token": "refresh",
                "user_id": 1,
            }
        )

        manager = LiproAuthManager(client)
        manager.set_credentials("phone", "password")

        await manager.ensure_valid_token()
        client.login.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_valid_token_no_credentials(self):
        """Test ensure_valid_token without credentials raises error."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.access_token = None

        manager = LiproAuthManager(client)

        with pytest.raises(LiproAuthError, match="Not authenticated"):
            await manager.ensure_valid_token()

    @pytest.mark.asyncio
    async def test_ensure_valid_token_not_expired(self):
        """Test ensure_valid_token when token is still valid."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.access_token = "valid_token"

        manager = LiproAuthManager(client)
        manager._token_expires_at = time.time() + 3600  # Expires in 1 hour

        await manager.ensure_valid_token()
        # No refresh should be called
        client.refresh_access_token.assert_not_called()

    @pytest.mark.asyncio
    async def test_ensure_valid_token_expiring_soon(self):
        """Test ensure_valid_token refreshes when expiring soon."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.access_token = "expiring_token"
        client.refresh_access_token = AsyncMock(
            return_value={
                "access_token": "new_token",
                "refresh_token": "new_refresh",
                "user_id": 1,
            }
        )

        manager = LiproAuthManager(client)
        # Token expires in 30 seconds (within buffer)
        manager._token_expires_at = time.time() + 30

        await manager.ensure_valid_token()


class TestLiproAuthManagerAdaptiveExpiry:
    """Tests for adaptive token expiry."""

    def test_adjust_expiry_on_401(self):
        """Test expiry adjustment when 401 received."""
        client = MagicMock(spec=LiproProtocolFacade)
        manager = LiproAuthManager(client)

        # Simulate token was refreshed 100 seconds ago
        manager._last_refresh_time = time.time() - 100
        manager._current_expiry_seconds = 3600  # 1 hour

        manager._adjust_expiry_on_401()

        # Expiry should be reduced
        assert manager._current_expiry_seconds < 3600

    def test_adjust_expiry_minimum(self):
        """Test expiry doesn't go below minimum."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.access_token = None
        manager = LiproAuthManager(client)

        # Simulate 401 received very quickly after refresh
        # This would normally reduce expiry drastically
        manager._last_refresh_time = time.time() - 5  # 5 seconds ago
        manager._current_expiry_seconds = 3600  # Start with 1 hour

        manager._adjust_expiry_on_401()

        # Should be reduced but not below minimum
        from custom_components.lipro.const.api import TOKEN_EXPIRY_MIN

        assert manager._current_expiry_seconds >= TOKEN_EXPIRY_MIN
        assert manager._current_expiry_seconds < 3600  # Should be reduced


class TestLiproAuthManagerDoubleCheckedLocking:
    """Tests for double-checked locking pattern."""

    @pytest.mark.asyncio
    async def test_concurrent_refresh_only_once(self):
        """Test that concurrent 401s only trigger one refresh."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.access_token = "token"
        client.refresh_access_token = AsyncMock(
            return_value={
                "access_token": "new_token",
                "refresh_token": "new_refresh",
                "user_id": 1,
            }
        )

        manager = LiproAuthManager(client)
        manager._last_refresh_time = 0  # Allow refresh

        # Simulate multiple concurrent refresh requests
        tasks = [
            asyncio.create_task(manager._do_token_refresh()),
            asyncio.create_task(manager._do_token_refresh()),
            asyncio.create_task(manager._do_token_refresh()),
        ]

        await asyncio.gather(*tasks)

        # Refresh should only be called once
        assert client.refresh_access_token.call_count == 1

    @pytest.mark.asyncio
    async def test_skip_recent_refresh(self):
        """Test that refresh is skipped if done recently."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.access_token = "token"
        client.refresh_access_token = AsyncMock(
            return_value={
                "access_token": "new_token",
                "refresh_token": "new_refresh",
                "user_id": 1,
            }
        )

        manager = LiproAuthManager(client)
        manager._last_refresh_time = time.time()  # Just refreshed

        await manager._do_token_refresh()

        # Should skip refresh
        client.refresh_access_token.assert_not_called()


class TestLiproAuthManagerProperties:
    """Tests for auth manager properties."""

    def test_is_authenticated(self):
        """Test is_authenticated property."""
        client = MagicMock(spec=LiproProtocolFacade)

        manager = LiproAuthManager(client)

        # Not authenticated
        client.access_token = None
        assert manager.is_authenticated is False

        # Authenticated
        client.access_token = "token"
        assert manager.is_authenticated is True

    def test_token_expires_at(self):
        """Test token_expires_at property."""
        client = MagicMock(spec=LiproProtocolFacade)
        manager = LiproAuthManager(client)

        manager._token_expires_at = 1000167890.0

        assert manager.token_expires_at == 1000167890.0

    def test_current_expiry_seconds(self):
        """Test current_expiry_seconds property."""
        client = MagicMock(spec=LiproProtocolFacade)
        manager = LiproAuthManager(client)

        manager._current_expiry_seconds = 1800

        assert manager.current_expiry_seconds == 1800


class TestLiproAuthManagerEdgeCases:
    """Tests for auth manager edge cases."""

    def test_set_credentials_with_already_hashed_password(self):
        """Test set_credentials with pre-hashed password stores as-is."""
        client = MagicMock(spec=LiproProtocolFacade)
        manager = LiproAuthManager(client)

        hashed = "e10adc3949ba59abbe56e057f20f883e"
        manager.set_credentials("13800000000", hashed, password_is_hashed=True)

        assert manager._password == hashed
        assert manager._password_is_hashed is True

    @pytest.mark.asyncio
    async def test_refresh_other_auth_error_no_credentials_raises(self):
        """Test non-expired auth error without credentials re-raises."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.refresh_access_token = AsyncMock(
            side_effect=LiproAuthError("Some error", 999)
        )

        manager = LiproAuthManager(client)
        # No credentials set

        with pytest.raises(LiproAuthError):
            await manager.refresh_token()

    @pytest.mark.asyncio
    async def test_concurrent_ensure_valid_token_only_one_refresh(self):
        """Test concurrent ensure_valid_token calls only trigger one refresh."""
        client = MagicMock(spec=LiproProtocolFacade)
        client.access_token = "expiring_token"
        client.refresh_access_token = AsyncMock(
            return_value={
                "access_token": "new_token",
                "refresh_token": "new_refresh",
                "user_id": 1,
            }
        )

        manager = LiproAuthManager(client)
        # Token expires in 10 seconds (within buffer)
        manager._token_expires_at = time.time() + 10

        tasks = [
            asyncio.create_task(manager.ensure_valid_token()),
            asyncio.create_task(manager.ensure_valid_token()),
        ]

        await asyncio.gather(*tasks)

        # Only one refresh should happen due to double-checked locking
        assert client.refresh_access_token.call_count == 1

    def test_set_tokens_with_zero_expires_at_uses_default(self):
        """Test set_tokens with expires_at=0 calculates default expiry."""
        client = MagicMock(spec=LiproProtocolFacade)
        manager = LiproAuthManager(client)

        before = time.time()
        manager.set_tokens("access", "refresh", expires_at=0)

        # Should use default expiry, not 0
        assert manager._token_expires_at > before

    def test_set_tokens_with_none_expires_at_uses_default(self):
        """Test set_tokens with expires_at=None calculates default expiry."""
        client = MagicMock(spec=LiproProtocolFacade)
        manager = LiproAuthManager(client)

        before = time.time()
        manager.set_tokens("access", "refresh", expires_at=None)

        assert manager._token_expires_at > before

    def test_adjust_expiry_no_change_when_after_expected(self):
        """Test _adjust_expiry_on_401 doesn't change when 401 comes after expected expiry."""
        client = MagicMock(spec=LiproProtocolFacade)
        manager = LiproAuthManager(client)

        original_expiry = 3600
        manager._current_expiry_seconds = original_expiry
        # 401 came after expected expiry (4000 seconds since refresh)
        manager._last_refresh_time = time.time() - 4000

        manager._adjust_expiry_on_401()

        # Should not change
        assert manager._current_expiry_seconds == original_expiry
