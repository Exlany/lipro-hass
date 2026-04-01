"""Config flow for Lipro integration."""

from __future__ import annotations

import logging
import uuid

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const.base import DOMAIN
from .const.config import (
    CONF_COMMAND_RESULT_VERIFY,
    CONF_PHONE,
    DEFAULT_COMMAND_RESULT_VERIFY,
)
from .core import LiproAuthManager, LiproProtocolFacade
from .core.auth import AuthSessionSnapshot
from .core.utils.log_safety import safe_error_placeholder
from .flow.credentials import mask_phone_for_title as _mask_phone_for_title
from .flow.login import (
    ConfigEntryLoginProjection,
    async_do_hashed_login as _async_do_hashed_login,
    async_try_hashed_login as _async_try_hashed_login,
)
from .flow.options_flow import LiproOptionsFlow
from .flow.schemas import (
    STEP_REAUTH_DATA_SCHEMA,
    STEP_USER_DATA_SCHEMA,
    build_reconfigure_data_schema as _build_reconfigure_data_schema,
)
from .flow.step_handlers import (
    async_handle_reauth_confirm_step as _async_handle_reauth_confirm_step,
    async_handle_reconfigure_step as _async_handle_reconfigure_step,
    async_handle_user_step as _async_handle_user_step,
)
from .flow.submission import (
    UserFlowSubmission,
    build_reauth_description_placeholders as _build_reauth_description_placeholders,
    resolve_entry_remember_password_hash as _resolve_entry_remember_password_hash,
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

    def _ensure_user_flow_phone_id(self) -> str:
        """Return the sticky phone_id reused across user-step retries."""
        if not self._user_flow_phone_id:
            self._user_flow_phone_id = str(uuid.uuid4())
        return self._user_flow_phone_id

    @staticmethod
    def _entry_data_from_auth_session(
        auth_session: AuthSessionSnapshot,
        *,
        phone: str,
        password_hash: str,
        phone_id: str,
        remember_password_hash: bool,
    ) -> tuple[ConfigEntryLoginProjection, dict[str, object]]:
        """Project one auth session to config-entry data."""
        entry_login = ConfigEntryLoginProjection.from_auth_session(auth_session)
        return (
            entry_login,
            entry_login.to_entry_data(
                phone,
                password_hash,
                phone_id,
                remember_password_hash=remember_password_hash,
            ),
        )

    @staticmethod
    def _set_invalid_auth_session_error(
        errors: dict[str, str],
        *,
        context_name: str,
        err: ValueError,
    ) -> None:
        """Map malformed auth/session projections back to one flow error."""
        _LOGGER.error(
            "Malformed auth session during %s (%s)",
            context_name,
            safe_error_placeholder(err),
            exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
        )
        errors["base"] = "invalid_response"

    def _show_user_form(self, errors: dict[str, str]) -> ConfigFlowResult:
        """Show the initial user form."""
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def _async_create_user_entry(
        self,
        submission: UserFlowSubmission,
        *,
        phone_id: str,
        auth_session: AuthSessionSnapshot,
    ) -> ConfigFlowResult:
        """Create one new config entry from a successful user-step login."""
        entry_login, entry_data = self._entry_data_from_auth_session(
            auth_session,
            phone=submission.phone,
            password_hash=submission.password_hash,
            phone_id=phone_id,
            remember_password_hash=submission.remember_password_hash,
        )
        await self.async_set_unique_id(f"lipro_{entry_login.user_id}")
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=f"Lipro ({_mask_phone_for_title(submission.phone)})",
            data=entry_data,
            options={
                CONF_COMMAND_RESULT_VERIFY: DEFAULT_COMMAND_RESULT_VERIFY,
            },
        )

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
            description_placeholders=_build_reauth_description_placeholders(
                reauth_entry
            ),
        )

    def _show_reconfigure_form(
        self,
        reconfigure_entry: ConfigEntry,
        errors: dict[str, str],
    ) -> ConfigFlowResult:
        """Show the reconfigure form."""
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_build_reconfigure_data_schema(
                reconfigure_entry.data.get(CONF_PHONE, ""),
                default_remember_password_hash=_resolve_entry_remember_password_hash(
                    reconfigure_entry.data
                ),
            ),
            errors=errors,
        )

    async def _async_do_login(
        self,
        phone: str,
        password_hash: str,
        phone_id: str,
    ) -> AuthSessionSnapshot:
        """Perform login and return the formal auth/session snapshot."""
        return await _async_do_hashed_login(
            hass=self.hass,
            phone=phone,
            password_hash=password_hash,
            phone_id=phone_id,
            get_client_session=async_get_clientsession,
            build_boot_context=build_headless_boot_context,
            build_password_boot_seed=_build_password_boot_seed,
            protocol_factory=LiproProtocolFacade,
            auth_manager_factory=LiproAuthManager,
        )

    async def _async_try_login(
        self,
        phone: str,
        password_hash: str,
        phone_id: str,
        errors: dict[str, str],
        context_name: str,
    ) -> AuthSessionSnapshot | None:
        """Attempt login and populate errors dict on failure."""
        return await _async_try_hashed_login(
            phone=phone,
            password_hash=password_hash,
            phone_id=phone_id,
            errors=errors,
            context_name=context_name,
            do_login=self._async_do_login,
            logger=_LOGGER,
        )

    def show_user_form(self, errors: dict[str, str]) -> ConfigFlowResult:
        """Expose the user-form adapter to localized step handlers."""
        return self._show_user_form(errors)

    def ensure_user_flow_phone_id(self) -> str:
        """Expose the sticky phone-id helper to localized step handlers."""
        return self._ensure_user_flow_phone_id()

    @staticmethod
    def entry_data_from_auth_session(
        auth_session: AuthSessionSnapshot,
        *,
        phone: str,
        password_hash: str,
        phone_id: str,
        remember_password_hash: bool,
    ) -> tuple[ConfigEntryLoginProjection, dict[str, object]]:
        """Expose config-entry projection to localized step handlers."""
        return LiproConfigFlow._entry_data_from_auth_session(
            auth_session,
            phone=phone,
            password_hash=password_hash,
            phone_id=phone_id,
            remember_password_hash=remember_password_hash,
        )

    @staticmethod
    def set_invalid_auth_session_error(
        errors: dict[str, str],
        *,
        context_name: str,
        err: ValueError,
    ) -> None:
        """Expose malformed auth-session mapping to localized step handlers."""
        LiproConfigFlow._set_invalid_auth_session_error(
            errors,
            context_name=context_name,
            err=err,
        )

    async def async_create_user_entry(
        self,
        submission: UserFlowSubmission,
        *,
        phone_id: str,
        auth_session: AuthSessionSnapshot,
    ) -> ConfigFlowResult:
        """Expose user-entry creation to localized step handlers."""
        return await self._async_create_user_entry(
            submission,
            phone_id=phone_id,
            auth_session=auth_session,
        )

    def show_reauth_form(
        self,
        reauth_entry: ConfigEntry,
        errors: dict[str, str],
    ) -> ConfigFlowResult:
        """Expose the reauth form renderer to localized step handlers."""
        return self._show_reauth_form(reauth_entry, errors)

    def show_reconfigure_form(
        self,
        reconfigure_entry: ConfigEntry,
        errors: dict[str, str],
    ) -> ConfigFlowResult:
        """Expose the reconfigure form renderer to localized step handlers."""
        return self._show_reconfigure_form(reconfigure_entry, errors)

    async def async_try_login(
        self,
        phone: str,
        password_hash: str,
        phone_id: str,
        errors: dict[str, str],
        context_name: str,
    ) -> AuthSessionSnapshot | None:
        """Expose login attempts to localized step handlers."""
        return await self._async_try_login(
            phone,
            password_hash,
            phone_id,
            errors,
            context_name,
        )

    def get_reauth_entry(self) -> ConfigEntry:
        """Expose the active reauth entry to localized step handlers."""
        return self._get_reauth_entry()

    def get_reconfigure_entry(self) -> ConfigEntry:
        """Expose the active reconfigure entry to localized step handlers."""
        return self._get_reconfigure_entry()

    def abort_if_unique_id_mismatch(self) -> None:
        """Expose unique-id mismatch protection to localized step handlers."""
        self._abort_if_unique_id_mismatch()

    async def async_step_user(
        self,
        user_input: dict[str, object] | None = None,
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        return await _async_handle_user_step(self, user_input, logger=_LOGGER)

    async def async_step_reauth(self, entry_data: dict[str, object]) -> ConfigFlowResult:
        """Handle reauthorization."""
        del entry_data
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, object] | None = None,
    ) -> ConfigFlowResult:
        """Handle reauthorization confirmation."""
        return await _async_handle_reauth_confirm_step(
            self,
            user_input,
            logger=_LOGGER,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, object] | None = None,
    ) -> ConfigFlowResult:
        """Handle reconfiguration."""
        return await _async_handle_reconfigure_step(
            self,
            user_input,
            logger=_LOGGER,
        )
