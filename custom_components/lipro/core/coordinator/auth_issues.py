"""Coordinator authentication issue handling and error mapping."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any, NoReturn

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.issue_registry import (
    IssueSeverity,
    async_create_issue,
    async_delete_issue,
)
from homeassistant.helpers.update_coordinator import UpdateFailed

from ...const import DOMAIN
from ..api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from ..utils.log_safety import safe_error_placeholder
from .properties import _CoordinatorPropertiesMixin

_LOGGER = logging.getLogger(__name__)


class _CoordinatorAuthIssuesMixin(_CoordinatorPropertiesMixin):
    """Mixin: reauth triggers, repair issues, update error mapping."""

    async def _trigger_reauth(self, key: str, **placeholders: str) -> None:
        """Show auth notification and trigger reauth flow."""
        sanitized = self._sanitize_auth_placeholders(placeholders)
        await self._async_show_auth_notification(key, **sanitized)
        if self.config_entry:
            self.config_entry.async_start_reauth(self.hass)

    @staticmethod
    def _sanitize_auth_placeholders(placeholders: Mapping[str, Any]) -> dict[str, str]:
        """Sanitize auth placeholders to avoid raw error message leakage."""
        sanitized: dict[str, str] = {}
        for key, value in placeholders.items():
            if isinstance(value, BaseException):
                sanitized[key] = safe_error_placeholder(value)
                continue

            text = str(value).strip()
            if not text:
                continue

            if key == "error":
                if (
                    text.isdigit() and len(text) <= 6
                ) or _CoordinatorAuthIssuesMixin._is_safe_error_marker(text):
                    sanitized[key] = text
                else:
                    sanitized[key] = "AuthError"
                continue

            sanitized[key] = text
        return sanitized

    @staticmethod
    def _is_safe_error_marker(text: str) -> bool:
        """Return True when marker matches safe_error_placeholder() structure."""
        candidate = str(text).strip()
        if not candidate:
            return False
        if any(ch.isspace() for ch in candidate):
            return False
        if not candidate[:1].isalpha():
            return False

        if "(" not in candidate or not candidate.endswith(")"):
            return False
        name, rest = candidate.split("(", 1)
        if not name or not name.replace("_", "").isalnum():
            return False
        inner = rest[:-1]
        if not inner.startswith("code="):
            return False
        code = inner.removeprefix("code=").strip()
        if not code or len(code) > 32:
            return False
        allowed = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:"
        )
        return all(ch in allowed for ch in code)

    async def _async_show_auth_notification(
        self,
        key: str,
        **placeholders: str,
    ) -> None:
        """Create a repair issue for authentication errors."""
        async_create_issue(
            self.hass,
            domain=DOMAIN,
            issue_id=key,
            is_fixable=True,
            severity=IssueSeverity.ERROR,
            translation_key=key,
            translation_placeholders=placeholders or None,
        )

    def _clear_auth_issues(self) -> None:
        """Clear auth-related repair issues once authentication is healthy."""
        async_delete_issue(self.hass, DOMAIN, "auth_expired")
        async_delete_issue(self.hass, DOMAIN, "auth_error")

    async def _async_ensure_authenticated(self) -> None:
        """Ensure a valid access token and clear stale auth issues."""
        await self.auth_manager.ensure_valid_token()
        self._clear_auth_issues()

    async def _raise_update_data_error(self, err: Exception) -> NoReturn:
        """Map API/auth exceptions to Home Assistant update errors."""
        marker = safe_error_placeholder(err)
        if isinstance(err, LiproRefreshTokenExpiredError):
            await self._trigger_reauth("auth_expired")
            msg = f"Refresh token expired, re-authentication required ({marker})"
            raise ConfigEntryAuthFailed(msg) from err
        if isinstance(err, LiproAuthError):
            await self._trigger_reauth("auth_error", error=marker)
            msg = f"Authentication error ({marker})"
            raise ConfigEntryAuthFailed(msg) from err
        if isinstance(err, LiproConnectionError):
            msg = f"Connection error ({marker})"
            raise UpdateFailed(msg) from err
        if isinstance(err, LiproApiError):
            msg = f"API error ({marker})"
            raise UpdateFailed(msg) from err

        raise err


__all__ = ["_CoordinatorAuthIssuesMixin"]
