"""Localized config-flow step orchestration helpers."""

from __future__ import annotations

import logging
from typing import Protocol

from homeassistant.config_entries import ConfigEntry, ConfigFlowResult

from ..core.auth import AuthSessionSnapshot
from .login import ConfigEntryLoginProjection
from .submission import (
    UserFlowSubmission,
    resolve_reauth_expected_user_id,
    validate_reauth_submission,
    validate_reconfigure_submission,
    validate_user_submission,
)

FlowErrors = dict[str, str]


class UserStepFlow(Protocol):
    """Config-flow surface required by the user step handler."""

    def show_user_form(self, errors: FlowErrors) -> ConfigFlowResult:
        """Render the user step form."""

    def ensure_user_flow_phone_id(self) -> str:
        """Return the sticky phone-id used across user retries."""

    async def async_try_login(
        self,
        phone: str,
        password_hash: str,
        phone_id: str,
        errors: FlowErrors,
        context_name: str,
    ) -> AuthSessionSnapshot | None:
        """Attempt one login and populate translated errors on failure."""

    async def async_create_user_entry(
        self,
        submission: UserFlowSubmission,
        *,
        phone_id: str,
        auth_session: AuthSessionSnapshot,
    ) -> ConfigFlowResult:
        """Create one config entry from a successful user-step login."""

    def set_invalid_auth_session_error(
        self,
        errors: FlowErrors,
        *,
        context_name: str,
        err: ValueError,
    ) -> None:
        """Project malformed auth/session payloads to flow errors."""


class ReauthStepFlow(Protocol):
    """Config-flow surface required by the reauth step handler."""

    def get_reauth_entry(self) -> ConfigEntry:
        """Return the entry currently being reauthorized."""

    def show_reauth_form(
        self,
        reauth_entry: ConfigEntry,
        errors: FlowErrors,
    ) -> ConfigFlowResult:
        """Render the reauth form."""

    async def async_try_login(
        self,
        phone: str,
        password_hash: str,
        phone_id: str,
        errors: FlowErrors,
        context_name: str,
    ) -> AuthSessionSnapshot | None:
        """Attempt one login and populate translated errors on failure."""

    def entry_data_from_auth_session(
        self,
        auth_session: AuthSessionSnapshot,
        *,
        phone: str,
        password_hash: str,
        phone_id: str,
        remember_password_hash: bool,
    ) -> tuple[ConfigEntryLoginProjection, dict[str, object]]:
        """Project one auth session into config-entry data."""

    def set_invalid_auth_session_error(
        self,
        errors: FlowErrors,
        *,
        context_name: str,
        err: ValueError,
    ) -> None:
        """Project malformed auth/session payloads to flow errors."""

    def async_update_reload_and_abort(
        self,
        reauth_entry: ConfigEntry,
        *,
        data: dict[str, object],
    ) -> ConfigFlowResult:
        """Persist one updated entry payload and abort successfully."""


class ReconfigureStepFlow(Protocol):
    """Config-flow surface required by the reconfigure step handler."""

    def get_reconfigure_entry(self) -> ConfigEntry:
        """Return the entry currently being reconfigured."""

    def show_reconfigure_form(
        self,
        reconfigure_entry: ConfigEntry,
        errors: FlowErrors,
    ) -> ConfigFlowResult:
        """Render the reconfigure form."""

    async def async_try_login(
        self,
        phone: str,
        password_hash: str,
        phone_id: str,
        errors: FlowErrors,
        context_name: str,
    ) -> AuthSessionSnapshot | None:
        """Attempt one login and populate translated errors on failure."""

    def entry_data_from_auth_session(
        self,
        auth_session: AuthSessionSnapshot,
        *,
        phone: str,
        password_hash: str,
        phone_id: str,
        remember_password_hash: bool,
    ) -> tuple[ConfigEntryLoginProjection, dict[str, object]]:
        """Project one auth session into config-entry data."""

    def set_invalid_auth_session_error(
        self,
        errors: FlowErrors,
        *,
        context_name: str,
        err: ValueError,
    ) -> None:
        """Project malformed auth/session payloads to flow errors."""

    async def async_set_unique_id(self, unique_id: str) -> None:
        """Pin the current config flow to one unique-id."""

    def abort_if_unique_id_mismatch(self) -> None:
        """Abort if the reconfigured account mismatches the targeted entry."""

    def async_update_reload_and_abort(
        self,
        reconfigure_entry: ConfigEntry,
        *,
        data: dict[str, object],
    ) -> ConfigFlowResult:
        """Persist one updated entry payload and abort successfully."""


async def async_handle_user_step(
    flow: UserStepFlow,
    user_input: dict[str, object] | None,
    *,
    logger: logging.Logger,
) -> ConfigFlowResult:
    """Handle the initial user step for one config flow."""
    errors: FlowErrors = {}
    if user_input is None:
        return flow.show_user_form(errors)

    submission, errors = validate_user_submission(user_input, logger=logger)
    if submission is None:
        return flow.show_user_form(errors)

    phone_id = flow.ensure_user_flow_phone_id()
    auth_session = await flow.async_try_login(
        submission.phone,
        submission.password_hash,
        phone_id,
        errors,
        'login',
    )
    if auth_session is None:
        return flow.show_user_form(errors)

    try:
        return await flow.async_create_user_entry(
            submission,
            phone_id=phone_id,
            auth_session=auth_session,
        )
    except ValueError as err:
        flow.set_invalid_auth_session_error(
            errors,
            context_name='user entry projection',
            err=err,
        )
        return flow.show_user_form(errors)


async def async_handle_reauth_confirm_step(
    flow: ReauthStepFlow,
    user_input: dict[str, object] | None,
    *,
    logger: logging.Logger,
) -> ConfigFlowResult:
    """Handle the reauth confirmation step for one config flow."""
    errors: FlowErrors = {}
    reauth_entry = flow.get_reauth_entry()
    if user_input is None:
        return flow.show_reauth_form(reauth_entry, errors)

    submission, errors = validate_reauth_submission(
        reauth_entry,
        user_input,
        logger=logger,
    )
    if submission is None:
        return flow.show_reauth_form(reauth_entry, errors)

    auth_session = await flow.async_try_login(
        submission.phone,
        submission.password_hash,
        submission.phone_id,
        errors,
        'reauth',
    )
    if auth_session is None:
        return flow.show_reauth_form(reauth_entry, errors)

    try:
        entry_login, entry_data = flow.entry_data_from_auth_session(
            auth_session,
            phone=submission.phone,
            password_hash=submission.password_hash,
            phone_id=submission.phone_id,
            remember_password_hash=submission.remember_password_hash,
        )
    except ValueError as err:
        flow.set_invalid_auth_session_error(
            errors,
            context_name='reauth entry projection',
            err=err,
        )
        return flow.show_reauth_form(reauth_entry, errors)

    expected_user_id = resolve_reauth_expected_user_id(reauth_entry)
    if expected_user_id is not None and expected_user_id != entry_login.user_id:
        errors['base'] = 'reauth_user_mismatch'
        return flow.show_reauth_form(reauth_entry, errors)

    return flow.async_update_reload_and_abort(reauth_entry, data=entry_data)


async def async_handle_reconfigure_step(
    flow: ReconfigureStepFlow,
    user_input: dict[str, object] | None,
    *,
    logger: logging.Logger,
) -> ConfigFlowResult:
    """Handle the reconfigure step for one config flow."""
    errors: FlowErrors = {}
    reconfigure_entry = flow.get_reconfigure_entry()
    if user_input is None:
        return flow.show_reconfigure_form(reconfigure_entry, errors)

    submission, errors = validate_reconfigure_submission(
        reconfigure_entry,
        user_input,
        logger=logger,
    )
    if submission is None:
        return flow.show_reconfigure_form(reconfigure_entry, errors)

    auth_session = await flow.async_try_login(
        submission.phone,
        submission.password_hash,
        submission.phone_id,
        errors,
        'reconfigure',
    )
    if auth_session is None:
        return flow.show_reconfigure_form(reconfigure_entry, errors)

    try:
        entry_login, entry_data = flow.entry_data_from_auth_session(
            auth_session,
            phone=submission.phone,
            password_hash=submission.password_hash,
            phone_id=submission.phone_id,
            remember_password_hash=submission.remember_password_hash,
        )
    except ValueError as err:
        flow.set_invalid_auth_session_error(
            errors,
            context_name='reconfigure entry projection',
            err=err,
        )
        return flow.show_reconfigure_form(reconfigure_entry, errors)

    await flow.async_set_unique_id(f'lipro_{entry_login.user_id}')
    flow.abort_if_unique_id_mismatch()
    return flow.async_update_reload_and_abort(reconfigure_entry, data=entry_data)
