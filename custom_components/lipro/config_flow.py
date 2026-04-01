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
from .flow.submission import (
    UserFlowSubmission,
    build_reauth_description_placeholders as _build_reauth_description_placeholders,
    resolve_entry_remember_password_hash as _resolve_entry_remember_password_hash,
    resolve_reauth_expected_user_id as _resolve_reauth_expected_user_id,
    validate_reauth_submission as _validate_reauth_submission,
    validate_reconfigure_submission as _validate_reconfigure_submission,
    validate_user_submission as _validate_user_submission,
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

    async def async_step_user(
        self,
        user_input: dict[str, object] | None = None,
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is None:
            return self._show_user_form(errors)

        submission, errors = _validate_user_submission(
            user_input,
            logger=_LOGGER,
        )
        if submission is None:
            return self._show_user_form(errors)

        phone_id = self._ensure_user_flow_phone_id()
        auth_session = await self._async_try_login(
            submission.phone,
            submission.password_hash,
            phone_id,
            errors,
            "login",
        )
        if auth_session is None:
            return self._show_user_form(errors)

        try:
            return await self._async_create_user_entry(
                submission,
                phone_id=phone_id,
                auth_session=auth_session,
            )
        except ValueError as err:
            self._set_invalid_auth_session_error(
                errors,
                context_name="user entry projection",
                err=err,
            )
            return self._show_user_form(errors)

    async def async_step_reauth(self, entry_data: dict[str, object]) -> ConfigFlowResult:
        """Handle reauthorization."""
        del entry_data
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, object] | None = None,
    ) -> ConfigFlowResult:
        """Handle reauthorization confirmation."""
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()
        if user_input is None:
            return self._show_reauth_form(reauth_entry, errors)

        submission, errors = _validate_reauth_submission(
            reauth_entry,
            user_input,
            logger=_LOGGER,
        )
        if submission is None:
            return self._show_reauth_form(reauth_entry, errors)

        auth_session = await self._async_try_login(
            submission.phone,
            submission.password_hash,
            submission.phone_id,
            errors,
            "reauth",
        )
        if auth_session is None:
            return self._show_reauth_form(reauth_entry, errors)

        try:
            entry_login, entry_data = self._entry_data_from_auth_session(
                auth_session,
                phone=submission.phone,
                password_hash=submission.password_hash,
                phone_id=submission.phone_id,
                remember_password_hash=submission.remember_password_hash,
            )
        except ValueError as err:
            self._set_invalid_auth_session_error(
                errors,
                context_name="reauth entry projection",
                err=err,
            )
            return self._show_reauth_form(reauth_entry, errors)
        expected_user_id = _resolve_reauth_expected_user_id(reauth_entry)
        if expected_user_id is not None and expected_user_id != entry_login.user_id:
            errors["base"] = "reauth_user_mismatch"
            return self._show_reauth_form(reauth_entry, errors)

        return self.async_update_reload_and_abort(
            reauth_entry,
            data=entry_data,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, object] | None = None,
    ) -> ConfigFlowResult:
        """Handle reconfiguration."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()
        if user_input is None:
            return self._show_reconfigure_form(reconfigure_entry, errors)

        submission, errors = _validate_reconfigure_submission(
            reconfigure_entry,
            user_input,
            logger=_LOGGER,
        )
        if submission is None:
            return self._show_reconfigure_form(reconfigure_entry, errors)

        auth_session = await self._async_try_login(
            submission.phone,
            submission.password_hash,
            submission.phone_id,
            errors,
            "reconfigure",
        )
        if auth_session is None:
            return self._show_reconfigure_form(reconfigure_entry, errors)

        try:
            entry_login, entry_data = self._entry_data_from_auth_session(
                auth_session,
                phone=submission.phone,
                password_hash=submission.password_hash,
                phone_id=submission.phone_id,
                remember_password_hash=submission.remember_password_hash,
            )
        except ValueError as err:
            self._set_invalid_auth_session_error(
                errors,
                context_name="reconfigure entry projection",
                err=err,
            )
            return self._show_reconfigure_form(reconfigure_entry, errors)
        await self.async_set_unique_id(f"lipro_{entry_login.user_id}")
        self._abort_if_unique_id_mismatch()
        return self.async_update_reload_and_abort(
            reconfigure_entry,
            data=entry_data,
        )
