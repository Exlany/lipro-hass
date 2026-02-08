"""Config flow for Lipro integration."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import logging
from typing import Any
import uuid

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_ANONYMOUS_SHARE_ENABLED,
    CONF_ANONYMOUS_SHARE_ERRORS,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_ANONYMOUS_SHARE_ENABLED,
    DEFAULT_ANONYMOUS_SHARE_ERRORS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .core.api import LiproApiError, LiproAuthError, LiproClient, LiproConnectionError

_LOGGER = logging.getLogger(__name__)

# Key for storing password MD5 hash instead of plain password
# This improves security as the API accepts MD5 hash directly
CONF_PASSWORD_HASH = "password_hash"


def _hash_password(password: str) -> str:
    """Hash password using MD5 (as required by Lipro API)."""
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def _map_login_error(err: LiproApiError) -> str:
    """Map login exception to error key for UI display."""
    if isinstance(err, LiproAuthError):
        _LOGGER.warning("Authentication failed: %s", err)
        return "invalid_auth"
    if isinstance(err, LiproConnectionError):
        _LOGGER.warning("Connection failed: %s", err)
        return "cannot_connect"
    _LOGGER.warning("API error: %s", err)
    return "unknown"


@dataclass
class LoginResult:
    """Result of a successful login."""

    access_token: str
    refresh_token: str
    user_id: int
    biz_id: str | None

    def to_entry_data(
        self,
        phone: str,
        password_hash: str,
        phone_id: str,
    ) -> dict[str, Any]:
        """Convert to config entry data dict."""
        return {
            CONF_PHONE: phone,
            CONF_PASSWORD_HASH: password_hash,
            CONF_PHONE_ID: phone_id,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "user_id": self.user_id,
            "biz_id": self.biz_id,
        }


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PHONE): str,
        vol.Required(CONF_PASSWORD): str,
    },
)


class LiproConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lipro."""

    VERSION = 1
    MINOR_VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> LiproOptionsFlow:
        """Get the options flow for this handler."""
        return LiproOptionsFlow(config_entry)

    async def _async_do_login(
        self,
        phone: str,
        password_hash: str,
        phone_id: str,
    ) -> LoginResult:
        """Perform login and return result.

        Args:
            phone: Phone number.
            password_hash: MD5 hashed password.
            phone_id: Device UUID.

        Returns:
            LoginResult with tokens and user info.

        Raises:
            LiproApiError: If login fails.

        """
        session = async_get_clientsession(self.hass)
        client = LiproClient(phone_id, session)
        result = await client.login_with_hash(phone, password_hash)

        return LoginResult(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            user_id=result["user_id"],
            biz_id=result.get("biz_id"),
        )

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            phone = user_input[CONF_PHONE]
            password_hash = _hash_password(user_input[CONF_PASSWORD])
            phone_id = str(uuid.uuid4())

            try:
                login_result = await self._async_do_login(
                    phone, password_hash, phone_id
                )

                await self.async_set_unique_id(f"lipro_{login_result.user_id}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Lipro ({phone})",
                    data=login_result.to_entry_data(phone, password_hash, phone_id),
                )

            except LiproApiError as err:
                errors["base"] = _map_login_error(err)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        """Handle reauthorization."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle reauthorization confirmation."""
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()

        if user_input is not None:
            phone = reauth_entry.data.get(CONF_PHONE, "")
            phone_id = reauth_entry.data.get(CONF_PHONE_ID, "")
            password_hash = _hash_password(user_input[CONF_PASSWORD])

            try:
                login_result = await self._async_do_login(
                    phone, password_hash, phone_id
                )

                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data=login_result.to_entry_data(phone, password_hash, phone_id),
                )

            except LiproApiError as err:
                errors["base"] = _map_login_error(err)

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            errors=errors,
            description_placeholders={"phone": reauth_entry.data.get(CONF_PHONE, "")},
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle reconfiguration."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()

        if user_input is not None:
            phone = user_input[CONF_PHONE]
            password_hash = _hash_password(user_input[CONF_PASSWORD])
            phone_id = reconfigure_entry.data.get(CONF_PHONE_ID, "")

            try:
                login_result = await self._async_do_login(
                    phone, password_hash, phone_id
                )

                # Check unique_id if switching to different account
                new_unique_id = f"lipro_{login_result.user_id}"
                if reconfigure_entry.unique_id != new_unique_id:
                    await self.async_set_unique_id(new_unique_id)
                    self._abort_if_unique_id_configured()

                return self.async_update_reload_and_abort(
                    reconfigure_entry,
                    data=login_result.to_entry_data(phone, password_hash, phone_id),
                )

            except LiproApiError as err:
                errors["base"] = _map_login_error(err)

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PHONE,
                        default=reconfigure_entry.data.get(CONF_PHONE, ""),
                    ): str,
                    vol.Required(CONF_PASSWORD): str,
                },
            ),
            errors=errors,
        )


class LiproOptionsFlow(OptionsFlow):
    """Handle Lipro options."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )
        current_anonymous_share = self.config_entry.options.get(
            CONF_ANONYMOUS_SHARE_ENABLED,
            DEFAULT_ANONYMOUS_SHARE_ENABLED,
        )
        current_anonymous_share_errors = self.config_entry.options.get(
            CONF_ANONYMOUS_SHARE_ERRORS,
            DEFAULT_ANONYMOUS_SHARE_ERRORS,
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=current_interval,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    ),
                    vol.Required(
                        CONF_ANONYMOUS_SHARE_ENABLED,
                        default=current_anonymous_share,
                    ): bool,
                    vol.Required(
                        CONF_ANONYMOUS_SHARE_ERRORS,
                        default=current_anonymous_share_errors,
                    ): bool,
                },
            ),
        )
