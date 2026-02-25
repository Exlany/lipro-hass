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
from homeassistant.data_entry_flow import AbortFlow
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_ACCESS_TOKEN,
    CONF_ANONYMOUS_SHARE_ENABLED,
    CONF_ANONYMOUS_SHARE_ERRORS,
    CONF_BIZ_ID,
    CONF_DEBUG_MODE,
    CONF_ENABLE_POWER_MONITORING,
    CONF_MQTT_ENABLED,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_POWER_QUERY_INTERVAL,
    CONF_REFRESH_TOKEN,
    CONF_REQUEST_TIMEOUT,
    CONF_SCAN_INTERVAL,
    CONF_USER_ID,
    DEFAULT_ANONYMOUS_SHARE_ENABLED,
    DEFAULT_ANONYMOUS_SHARE_ERRORS,
    DEFAULT_DEBUG_MODE,
    DEFAULT_ENABLE_POWER_MONITORING,
    DEFAULT_MQTT_ENABLED,
    DEFAULT_POWER_QUERY_INTERVAL,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_POWER_QUERY_INTERVAL,
    MAX_REQUEST_TIMEOUT,
    MAX_SCAN_INTERVAL,
    MIN_POWER_QUERY_INTERVAL,
    MIN_REQUEST_TIMEOUT,
    MIN_SCAN_INTERVAL,
)
from .core.api import LiproApiError, LiproAuthError, LiproClient, LiproConnectionError

_LOGGER = logging.getLogger(__name__)

# Options flow key for toggling advanced settings step
_CONF_SHOW_ADVANCED = "show_advanced"


def _text_selector() -> selector.TextSelector:
    """Create a plain text selector."""
    return selector.TextSelector(
        selector.TextSelectorConfig(
            type=selector.TextSelectorType.TEXT,
        )
    )


def _password_selector() -> selector.TextSelector:
    """Create a password selector."""
    return selector.TextSelector(
        selector.TextSelectorConfig(
            type=selector.TextSelectorType.PASSWORD,
        )
    )


def _hash_password(password: str) -> str:
    """Hash password using MD5 (as required by Lipro API)."""
    return hashlib.md5(password.encode("utf-8"), usedforsecurity=False).hexdigest()


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
            CONF_ACCESS_TOKEN: self.access_token,
            CONF_REFRESH_TOKEN: self.refresh_token,
            CONF_USER_ID: self.user_id,
            CONF_BIZ_ID: self.biz_id,
        }


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PHONE): _text_selector(),
        vol.Required(CONF_PASSWORD): _password_selector(),
    },
)
STEP_REAUTH_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PASSWORD): _password_selector()
    }
)


def _build_reconfigure_data_schema(default_phone: str) -> vol.Schema:
    """Build schema for the reconfigure step."""
    return vol.Schema(
        {
            vol.Required(CONF_PHONE, default=default_phone): _text_selector(),
            vol.Required(CONF_PASSWORD): _password_selector(),
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
        return LiproOptionsFlow()

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
            access_token=result[CONF_ACCESS_TOKEN],
            refresh_token=result[CONF_REFRESH_TOKEN],
            user_id=result[CONF_USER_ID],
            biz_id=result.get(CONF_BIZ_ID),
        )

    async def _async_try_login(
        self,
        phone: str,
        password_hash: str,
        phone_id: str,
        errors: dict[str, str],
        context_name: str,
    ) -> LoginResult | None:
        """Attempt login and populate errors dict on failure.

        Args:
            phone: Phone number.
            password_hash: MD5 hashed password.
            phone_id: Device UUID.
            errors: Dict to populate with error keys on failure.
            context_name: Name for logging (e.g. "login", "reauth").

        Returns:
            LoginResult on success, None on failure.

        """
        try:
            return await self._async_do_login(phone, password_hash, phone_id)
        except LiproApiError as err:
            errors["base"] = _map_login_error(err)
        except AbortFlow:
            raise
        except (KeyError, TypeError, ValueError):
            _LOGGER.exception("Malformed login response during %s", context_name)
            errors["base"] = "unknown"
        except Exception:
            _LOGGER.exception("Unexpected error during %s", context_name)
            errors["base"] = "unknown"
        return None

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

            login_result = await self._async_try_login(
                phone, password_hash, phone_id, errors, "login"
            )
            if login_result is not None:
                await self.async_set_unique_id(f"lipro_{login_result.user_id}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Lipro ({phone})",
                    data=login_result.to_entry_data(phone, password_hash, phone_id),
                )

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
            if not phone or not phone_id:
                _LOGGER.error(
                    "Missing phone or phone_id in reauth entry, "
                    "please remove and re-add the integration"
                )
                errors["base"] = "unknown"
                return self._show_reauth_form(reauth_entry, errors)
            password_hash = _hash_password(user_input[CONF_PASSWORD])

            login_result = await self._async_try_login(
                phone, password_hash, phone_id, errors, "reauth"
            )
            if login_result is not None:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data=login_result.to_entry_data(phone, password_hash, phone_id),
                )

        return self._show_reauth_form(reauth_entry, errors)

    def _show_reauth_form(
        self,
        reauth_entry: ConfigEntry,
        errors: dict[str, str],
    ) -> ConfigFlowResult:
        """Show the reauth confirmation form."""
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_REAUTH_DATA_SCHEMA,
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
            if not phone_id:
                _LOGGER.error(
                    "Missing phone_id in reconfigure entry, "
                    "please remove and re-add the integration"
                )
                errors["base"] = "unknown"
                return self._show_reconfigure_form(reconfigure_entry, errors)

            login_result = await self._async_try_login(
                phone, password_hash, phone_id, errors, "reconfigure"
            )
            if login_result is not None:
                # Verify unique_id matches when switching accounts
                await self.async_set_unique_id(f"lipro_{login_result.user_id}")
                self._abort_if_unique_id_mismatch()

                return self.async_update_reload_and_abort(
                    reconfigure_entry,
                    data=login_result.to_entry_data(phone, password_hash, phone_id),
                )

        return self._show_reconfigure_form(reconfigure_entry, errors)

    def _show_reconfigure_form(
        self,
        reconfigure_entry: ConfigEntry,
        errors: dict[str, str],
    ) -> ConfigFlowResult:
        """Show the reconfigure form."""
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_build_reconfigure_data_schema(
                reconfigure_entry.data.get(CONF_PHONE, "")
            ),
            errors=errors,
        )


class LiproOptionsFlow(OptionsFlow):
    """Handle Lipro options."""

    def __init__(self) -> None:
        """Initialize options flow."""
        super().__init__()
        self._options: dict[str, Any] = {}

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage basic options."""
        if user_input is not None:
            # Store basic options and check if user wants advanced settings
            show_advanced = user_input.pop(_CONF_SHOW_ADVANCED, False)
            self._options.update(user_input)

            if show_advanced:
                return await self.async_step_advanced()

            # Merge with existing advanced options (keep previous values)
            return self._save_options()

        return self.async_show_form(
            step_id="init",
            data_schema=self._build_init_schema(),
        )

    async def async_step_advanced(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage advanced options."""
        if user_input is not None:
            self._options.update(user_input)
            return self._save_options()

        return self.async_show_form(
            step_id="advanced",
            data_schema=self._build_advanced_schema(),
        )

    def _save_options(self) -> ConfigFlowResult:
        """Save options, merging with existing advanced options if not visited."""
        # Merge: start with existing options, overlay with new selections
        merged = dict(self.config_entry.options)
        merged.update(self._options)
        return self.async_create_entry(title="", data=merged)

    def _build_init_schema(self) -> vol.Schema:
        """Build the basic options schema."""
        options = self.config_entry.options
        return vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                ),
                vol.Required(
                    CONF_MQTT_ENABLED,
                    default=options.get(CONF_MQTT_ENABLED, DEFAULT_MQTT_ENABLED),
                ): bool,
                vol.Required(
                    CONF_ENABLE_POWER_MONITORING,
                    default=options.get(
                        CONF_ENABLE_POWER_MONITORING,
                        DEFAULT_ENABLE_POWER_MONITORING,
                    ),
                ): bool,
                vol.Required(
                    CONF_ANONYMOUS_SHARE_ENABLED,
                    default=options.get(
                        CONF_ANONYMOUS_SHARE_ENABLED,
                        DEFAULT_ANONYMOUS_SHARE_ENABLED,
                    ),
                ): bool,
                vol.Required(
                    CONF_ANONYMOUS_SHARE_ERRORS,
                    default=options.get(
                        CONF_ANONYMOUS_SHARE_ERRORS,
                        DEFAULT_ANONYMOUS_SHARE_ERRORS,
                    ),
                ): bool,
                vol.Optional(
                    _CONF_SHOW_ADVANCED,
                    default=False,
                ): bool,
            },
        )

    def _build_advanced_schema(self) -> vol.Schema:
        """Build the advanced options schema."""
        options = self.config_entry.options
        return vol.Schema(
            {
                vol.Required(
                    CONF_POWER_QUERY_INTERVAL,
                    default=options.get(
                        CONF_POWER_QUERY_INTERVAL, DEFAULT_POWER_QUERY_INTERVAL
                    ),
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(
                        min=MIN_POWER_QUERY_INTERVAL, max=MAX_POWER_QUERY_INTERVAL
                    ),
                ),
                vol.Required(
                    CONF_REQUEST_TIMEOUT,
                    default=options.get(CONF_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT),
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_REQUEST_TIMEOUT, max=MAX_REQUEST_TIMEOUT),
                ),
                vol.Required(
                    CONF_DEBUG_MODE,
                    default=options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE),
                ): bool,
            },
        )
