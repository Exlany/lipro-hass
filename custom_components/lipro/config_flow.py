"""Config flow for Lipro integration."""

from __future__ import annotations

import asyncio
import logging
import uuid

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.data_entry_flow import AbortFlow
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const.base import DOMAIN
from .const.config import (
    CONF_COMMAND_RESULT_VERIFY,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REMEMBER_PASSWORD_HASH,
    CONF_USER_ID,
    DEFAULT_COMMAND_RESULT_VERIFY,
    DEFAULT_REMEMBER_PASSWORD_HASH,
)
from .core import LiproAuthManager, LiproProtocolFacade
from .core.api import LiproApiError
from .core.auth import AuthSessionSnapshot
from .core.utils.log_safety import safe_error_placeholder
from .flow.credentials import (
    mask_phone_for_title as _mask_phone_for_title,
    normalize_phone as _normalize_phone,
    validate_password as _validate_password,
)
from .flow.login import (
    ConfigEntryLoginProjection,
    hash_password as _hash_password,
    map_login_error as _map_login_error,
)
from .flow.options_flow import LiproOptionsFlow
from .flow.schemas import (
    STEP_REAUTH_DATA_SCHEMA,
    STEP_USER_DATA_SCHEMA,
    build_reconfigure_data_schema as _build_reconfigure_data_schema,
)
from .headless.boot import (
    build_headless_boot_context,
    build_password_boot_seed as _build_password_boot_seed,
)

_LOGGER = logging.getLogger(__name__)


class LiproConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lipro."""

    VERSION = 1
    MINOR_VERSION = 1

    _user_flow_phone_id: str | None = None

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
    ) -> AuthSessionSnapshot:
        """Perform login and return result.

        Args:
            phone: Phone number.
            password_hash: MD5 hashed password.
            phone_id: Device UUID.

        Returns:
            Formal auth/session snapshot with tokens and user info.

        Raises:
            LiproApiError: If login fails.

        """
        session = async_get_clientsession(self.hass)
        boot_context = build_headless_boot_context(
            _build_password_boot_seed(phone, password_hash, phone_id),
            session,
            client_factory=LiproProtocolFacade,
            auth_manager_factory=LiproAuthManager,
        )
        return await boot_context.async_login_with_password_hash()

    async def _async_try_login(
        self,
        phone: str,
        password_hash: str,
        phone_id: str,
        errors: dict[str, str],
        context_name: str,
    ) -> AuthSessionSnapshot | None:
        """Attempt login and populate errors dict on failure.

        Args:
            phone: Phone number.
            password_hash: MD5 hashed password.
            phone_id: Device UUID.
            errors: Dict to populate with error keys on failure.
            context_name: Name for logging (e.g. "login", "reauth").

        Returns:
            Formal auth/session snapshot on success, None on failure.

        """
        try:
            return await self._async_do_login(phone, password_hash, phone_id)
        except LiproApiError as err:
            errors["base"] = _map_login_error(err)
        except asyncio.CancelledError:
            raise
        except AbortFlow:
            raise
        except (KeyError, TypeError, ValueError) as err:
            _LOGGER.error(
                "Malformed login response during %s (%s)",
                context_name,
                safe_error_placeholder(err),
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            errors["base"] = "unknown"
        except (AttributeError, RuntimeError) as err:
            _LOGGER.error(
                "Unexpected login failure during %s (%s)",
                context_name,
                safe_error_placeholder(err),
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            errors["base"] = "unknown"
        return None

    async def async_step_user(
        self,
        user_input: dict[str, object] | None = None,
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                phone = _normalize_phone(user_input[CONF_PHONE])
            except vol.Invalid as err:
                _LOGGER.debug("Phone validation failed: %s", err)
                errors[CONF_PHONE] = "invalid_phone"

            try:
                password = _validate_password(user_input[CONF_PASSWORD])
            except vol.Invalid as err:
                _LOGGER.debug("Password validation failed: %s", err)
                errors[CONF_PASSWORD] = "invalid_password"

            if errors:
                return self.async_show_form(
                    step_id="user",
                    data_schema=STEP_USER_DATA_SCHEMA,
                    errors=errors,
                )

            password_hash = _hash_password(password)
            remember_password_hash = bool(
                user_input.get(
                    CONF_REMEMBER_PASSWORD_HASH,
                    DEFAULT_REMEMBER_PASSWORD_HASH,
                )
            )
            if not self._user_flow_phone_id:
                self._user_flow_phone_id = str(uuid.uuid4())
            phone_id = self._user_flow_phone_id

            auth_session = await self._async_try_login(
                phone, password_hash, phone_id, errors, "login"
            )
            if auth_session is not None:
                entry_login = ConfigEntryLoginProjection.from_auth_session(auth_session)
                await self.async_set_unique_id(f"lipro_{entry_login.user_id}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Lipro ({_mask_phone_for_title(phone)})",
                    data=entry_login.to_entry_data(
                        phone,
                        password_hash,
                        phone_id,
                        remember_password_hash=remember_password_hash,
                    ),
                    options={
                        CONF_COMMAND_RESULT_VERIFY: DEFAULT_COMMAND_RESULT_VERIFY,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, object]) -> ConfigFlowResult:
        """Handle reauthorization."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, object] | None = None,
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
            remember_password_hash = bool(
                reauth_entry.data.get(
                    CONF_REMEMBER_PASSWORD_HASH,
                    CONF_PASSWORD_HASH in reauth_entry.data,
                )
            )
            try:
                phone = _normalize_phone(phone)
                password = _validate_password(user_input[CONF_PASSWORD])
            except vol.Invalid as err:
                _LOGGER.debug("Validation failed during reauth: %s", err)
                errors[CONF_PASSWORD] = "invalid_password"
                return self._show_reauth_form(reauth_entry, errors)

            password_hash = _hash_password(password)

            auth_session = await self._async_try_login(
                phone, password_hash, phone_id, errors, "reauth"
            )
            if auth_session is not None:
                entry_login = ConfigEntryLoginProjection.from_auth_session(auth_session)
                expected_user_id: int | None = None
                raw_user_id = reauth_entry.data.get(CONF_USER_ID)
                if isinstance(raw_user_id, int) and not isinstance(raw_user_id, bool):
                    expected_user_id = raw_user_id
                elif isinstance(reauth_entry.unique_id, str) and reauth_entry.unique_id:
                    unique_id = reauth_entry.unique_id.strip()
                    if unique_id.startswith("lipro_"):
                        suffix = unique_id.removeprefix("lipro_").strip()
                        if suffix.isdecimal():
                            expected_user_id = int(suffix)

                if (
                    expected_user_id is not None
                    and expected_user_id != entry_login.user_id
                ):
                    errors["base"] = "reauth_user_mismatch"
                    return self._show_reauth_form(reauth_entry, errors)

                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data=entry_login.to_entry_data(
                        phone,
                        password_hash,
                        phone_id,
                        remember_password_hash=remember_password_hash,
                    ),
                )

        return self._show_reauth_form(reauth_entry, errors)

    def _show_reauth_form(
        self,
        reauth_entry: ConfigEntry,
        errors: dict[str, str],
    ) -> ConfigFlowResult:
        """Show the reauth confirmation form."""
        raw_phone = reauth_entry.data.get(CONF_PHONE, "")
        masked_phone = (
            _mask_phone_for_title(raw_phone) if isinstance(raw_phone, str) else "***"
        )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_REAUTH_DATA_SCHEMA,
            errors=errors,
            description_placeholders={"phone": masked_phone},
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, object] | None = None,
    ) -> ConfigFlowResult:
        """Handle reconfiguration."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()

        if user_input is not None:
            try:
                phone = _normalize_phone(user_input[CONF_PHONE])
            except vol.Invalid as err:
                _LOGGER.debug("Phone validation failed during reconfigure: %s", err)
                errors[CONF_PHONE] = "invalid_phone"

            try:
                password = _validate_password(user_input[CONF_PASSWORD])
            except vol.Invalid as err:
                _LOGGER.debug("Password validation failed during reconfigure: %s", err)
                errors[CONF_PASSWORD] = "invalid_password"

            if errors:
                return self._show_reconfigure_form(reconfigure_entry, errors)

            password_hash = _hash_password(password)
            remember_password_hash = bool(
                user_input.get(
                    CONF_REMEMBER_PASSWORD_HASH,
                    reconfigure_entry.data.get(
                        CONF_REMEMBER_PASSWORD_HASH,
                        CONF_PASSWORD_HASH in reconfigure_entry.data,
                    ),
                )
            )
            phone_id = reconfigure_entry.data.get(CONF_PHONE_ID, "")
            if not phone_id:
                _LOGGER.error(
                    "Missing phone_id in reconfigure entry, "
                    "please remove and re-add the integration"
                )
                errors["base"] = "unknown"
                return self._show_reconfigure_form(reconfigure_entry, errors)

            auth_session = await self._async_try_login(
                phone, password_hash, phone_id, errors, "reconfigure"
            )
            if auth_session is not None:
                entry_login = ConfigEntryLoginProjection.from_auth_session(auth_session)
                # Verify unique_id matches when switching accounts
                await self.async_set_unique_id(f"lipro_{entry_login.user_id}")
                self._abort_if_unique_id_mismatch()

                return self.async_update_reload_and_abort(
                    reconfigure_entry,
                    data=entry_login.to_entry_data(
                        phone,
                        password_hash,
                        phone_id,
                        remember_password_hash=remember_password_hash,
                    ),
                )

        return self._show_reconfigure_form(reconfigure_entry, errors)

    def _show_reconfigure_form(
        self,
        reconfigure_entry: ConfigEntry,
        errors: dict[str, str],
    ) -> ConfigFlowResult:
        """Show the reconfigure form."""
        default_remember_password_hash = bool(
            reconfigure_entry.data.get(
                CONF_REMEMBER_PASSWORD_HASH,
                CONF_PASSWORD_HASH in reconfigure_entry.data,
            )
        )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_build_reconfigure_data_schema(
                reconfigure_entry.data.get(CONF_PHONE, ""),
                default_remember_password_hash=default_remember_password_hash,
            ),
            errors=errors,
        )
