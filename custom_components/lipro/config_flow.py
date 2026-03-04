"""Config flow for Lipro integration."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import logging
import re
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
    CONF_DEVICE_FILTER_DID_LIST,
    CONF_DEVICE_FILTER_DID_MODE,
    CONF_DEVICE_FILTER_HOME_LIST,
    CONF_DEVICE_FILTER_HOME_MODE,
    CONF_DEVICE_FILTER_MODEL_LIST,
    CONF_DEVICE_FILTER_MODEL_MODE,
    CONF_DEVICE_FILTER_SSID_LIST,
    CONF_DEVICE_FILTER_SSID_MODE,
    CONF_ENABLE_POWER_MONITORING,
    CONF_LIGHT_TURN_ON_ON_ADJUST,
    CONF_MQTT_ENABLED,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_POWER_QUERY_INTERVAL,
    CONF_REFRESH_TOKEN,
    CONF_REMEMBER_PASSWORD_HASH,
    CONF_REQUEST_TIMEOUT,
    CONF_ROOM_AREA_SYNC_FORCE,
    CONF_SCAN_INTERVAL,
    CONF_USER_ID,
    DEFAULT_ANONYMOUS_SHARE_ENABLED,
    DEFAULT_ANONYMOUS_SHARE_ERRORS,
    DEFAULT_DEBUG_MODE,
    DEFAULT_DEVICE_FILTER_MODE,
    DEFAULT_ENABLE_POWER_MONITORING,
    DEFAULT_LIGHT_TURN_ON_ON_ADJUST,
    DEFAULT_MQTT_ENABLED,
    DEFAULT_POWER_QUERY_INTERVAL,
    DEFAULT_REMEMBER_PASSWORD_HASH,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_ROOM_AREA_SYNC_FORCE,
    DEFAULT_SCAN_INTERVAL,
    DEVICE_FILTER_MODE_EXCLUDE,
    DEVICE_FILTER_MODE_INCLUDE,
    DEVICE_FILTER_MODE_OFF,
    DOMAIN,
    MAX_POWER_QUERY_INTERVAL,
    MAX_REQUEST_TIMEOUT,
    MAX_SCAN_INTERVAL,
    MIN_POWER_QUERY_INTERVAL,
    MIN_REQUEST_TIMEOUT,
    MIN_SCAN_INTERVAL,
)
from .const.config import CONF_COMMAND_RESULT_VERIFY, DEFAULT_COMMAND_RESULT_VERIFY
from .core.api import LiproApiError, LiproAuthError, LiproClient, LiproConnectionError

_LOGGER = logging.getLogger(__name__)

# Options flow key for toggling advanced settings step
_CONF_SHOW_ADVANCED = "show_advanced"

_PHONE_INPUT_PATTERN = re.compile(r"^\+?\d{6,20}$")
_MAX_PASSWORD_LEN: int = 128
_DEVICE_FILTER_MODE_VALUES: tuple[str, str, str] = (
    DEVICE_FILTER_MODE_OFF,
    DEVICE_FILTER_MODE_INCLUDE,
    DEVICE_FILTER_MODE_EXCLUDE,
)


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


def _normalize_phone(phone: Any) -> str:
    """Normalize and validate user-provided phone value."""
    if not isinstance(phone, str):
        msg = "phone must be a string"
        raise vol.Invalid(msg)

    normalized = phone.strip()
    if not _PHONE_INPUT_PATTERN.fullmatch(normalized):
        msg = "phone must be 6-20 digits, optionally prefixed with +"
        raise vol.Invalid(msg)
    return normalized


def _mask_phone_for_title(phone: str) -> str:
    """Mask a normalized phone number for config-entry titles."""
    normalized = phone.strip()
    if not normalized:
        return "***"

    prefix = "+" if normalized.startswith("+") else ""
    digits = normalized.lstrip("+")

    if len(digits) <= 4:
        return f"{prefix}***"
    if len(digits) <= 8:
        return f"{prefix}{digits[:2]}***{digits[-2:]}"
    return f"{prefix}{digits[:3]}****{digits[-4:]}"


def _validate_password(password: Any) -> str:
    """Validate user-provided password value."""
    if not isinstance(password, str):
        msg = "password must be a string"
        raise vol.Invalid(msg)
    if not password or len(password) > _MAX_PASSWORD_LEN:
        msg = f"password length must be 1-{_MAX_PASSWORD_LEN}"
        raise vol.Invalid(msg)
    return password


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
        *,
        remember_password_hash: bool,
    ) -> dict[str, Any]:
        """Convert to config entry data dict."""
        entry_data: dict[str, Any] = {
            CONF_PHONE: phone,
            CONF_PHONE_ID: phone_id,
            CONF_ACCESS_TOKEN: self.access_token,
            CONF_REFRESH_TOKEN: self.refresh_token,
            CONF_USER_ID: self.user_id,
            CONF_BIZ_ID: self.biz_id,
            CONF_REMEMBER_PASSWORD_HASH: remember_password_hash,
        }
        if remember_password_hash:
            entry_data[CONF_PASSWORD_HASH] = password_hash
        return entry_data


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PHONE): _text_selector(),
        vol.Required(CONF_PASSWORD): _password_selector(),
        vol.Optional(
            CONF_REMEMBER_PASSWORD_HASH,
            default=DEFAULT_REMEMBER_PASSWORD_HASH,
        ): bool,
    },
)
STEP_REAUTH_DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_PASSWORD): _password_selector()}
)


def _build_reconfigure_data_schema(
    default_phone: str,
    *,
    default_remember_password_hash: bool,
) -> vol.Schema:
    """Build schema for the reconfigure step."""
    return vol.Schema(
        {
            vol.Required(CONF_PHONE, default=default_phone): _text_selector(),
            vol.Required(CONF_PASSWORD): _password_selector(),
            vol.Optional(
                CONF_REMEMBER_PASSWORD_HASH,
                default=default_remember_password_hash,
            ): bool,
        },
    )


def _build_bool_option_field(
    options: Mapping[str, Any],
    key: str,
    default: bool,
) -> tuple[vol.Marker, type[bool]]:
    """Build a required boolean option field for options schema."""
    return (
        vol.Required(
            key,
            default=options.get(key, default),
        ),
        bool,
    )


def _build_int_option_field(
    options: Mapping[str, Any],
    key: str,
    default: int,
    min_value: int,
    max_value: int,
) -> tuple[vol.Marker, vol.All]:
    """Build a required bounded integer option field for options schema."""
    return (
        vol.Required(
            key,
            default=options.get(key, default),
        ),
        vol.All(
            vol.Coerce(int),
            vol.Range(min=min_value, max=max_value),
        ),
    )


def _coerce_device_filter_list_option(value: Any) -> str:
    """Coerce stored filter-list option to form-friendly text."""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple, set, frozenset)):
        parts = []
        for item in value:
            normalized = str(item).strip()
            if normalized:
                parts.append(normalized)
        return ", ".join(parts)
    return ""


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
        result = await client.login(phone, password_hash, password_is_hashed=True)

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
        except asyncio.CancelledError:
            raise
        except AbortFlow:
            raise
        except (KeyError, TypeError, ValueError):
            _LOGGER.exception("Malformed login response during %s", context_name)
            errors["base"] = "unknown"
        except Exception as err:
            _LOGGER.exception(
                "Unexpected error during %s (%s)",
                context_name,
                type(err).__name__,
            )
            errors["base"] = "unknown"
        return None

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                phone = _normalize_phone(user_input[CONF_PHONE])
                password = _validate_password(user_input[CONF_PASSWORD])
            except vol.Invalid:
                errors["base"] = "invalid_auth"
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
            phone_id = str(uuid.uuid4())

            login_result = await self._async_try_login(
                phone, password_hash, phone_id, errors, "login"
            )
            if login_result is not None:
                await self.async_set_unique_id(f"lipro_{login_result.user_id}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Lipro ({_mask_phone_for_title(phone)})",
                    data=login_result.to_entry_data(
                        phone,
                        password_hash,
                        phone_id,
                        remember_password_hash=remember_password_hash,
                    ),
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
            remember_password_hash = bool(
                reauth_entry.data.get(
                    CONF_REMEMBER_PASSWORD_HASH,
                    CONF_PASSWORD_HASH in reauth_entry.data,
                )
            )
            try:
                phone = _normalize_phone(phone)
                password = _validate_password(user_input[CONF_PASSWORD])
            except vol.Invalid:
                errors["base"] = "invalid_auth"
                return self._show_reauth_form(reauth_entry, errors)

            password_hash = _hash_password(password)

            login_result = await self._async_try_login(
                phone, password_hash, phone_id, errors, "reauth"
            )
            if login_result is not None:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data=login_result.to_entry_data(
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
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle reconfiguration."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()

        if user_input is not None:
            try:
                phone = _normalize_phone(user_input[CONF_PHONE])
                password = _validate_password(user_input[CONF_PASSWORD])
            except vol.Invalid:
                errors["base"] = "invalid_auth"
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

            login_result = await self._async_try_login(
                phone, password_hash, phone_id, errors, "reconfigure"
            )
            if login_result is not None:
                # Verify unique_id matches when switching accounts
                await self.async_set_unique_id(f"lipro_{login_result.user_id}")
                self._abort_if_unique_id_mismatch()

                return self.async_update_reload_and_abort(
                    reconfigure_entry,
                    data=login_result.to_entry_data(
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
        schema: dict[vol.Marker, Any] = {}

        int_fields = (
            (
                CONF_SCAN_INTERVAL,
                DEFAULT_SCAN_INTERVAL,
                MIN_SCAN_INTERVAL,
                MAX_SCAN_INTERVAL,
            ),
        )
        for key, default, min_value, max_value in int_fields:
            int_field, int_validator = _build_int_option_field(
                options,
                key,
                default,
                min_value,
                max_value,
            )
            schema[int_field] = int_validator

        for key, default in (
            (CONF_MQTT_ENABLED, DEFAULT_MQTT_ENABLED),
            (CONF_ENABLE_POWER_MONITORING, DEFAULT_ENABLE_POWER_MONITORING),
            (CONF_ANONYMOUS_SHARE_ENABLED, DEFAULT_ANONYMOUS_SHARE_ENABLED),
            (CONF_ANONYMOUS_SHARE_ERRORS, DEFAULT_ANONYMOUS_SHARE_ERRORS),
        ):
            bool_field, bool_validator = _build_bool_option_field(
                options,
                key,
                default,
            )
            schema[bool_field] = bool_validator

        schema[vol.Optional(_CONF_SHOW_ADVANCED, default=False)] = bool
        return vol.Schema(schema)

    def _build_advanced_schema(self) -> vol.Schema:
        """Build the advanced options schema."""
        options = self.config_entry.options
        schema: dict[vol.Marker, Any] = {}

        for key, default, min_value, max_value in (
            (
                CONF_POWER_QUERY_INTERVAL,
                DEFAULT_POWER_QUERY_INTERVAL,
                MIN_POWER_QUERY_INTERVAL,
                MAX_POWER_QUERY_INTERVAL,
            ),
            (
                CONF_REQUEST_TIMEOUT,
                DEFAULT_REQUEST_TIMEOUT,
                MIN_REQUEST_TIMEOUT,
                MAX_REQUEST_TIMEOUT,
            ),
        ):
            int_field, int_validator = _build_int_option_field(
                options,
                key,
                default,
                min_value,
                max_value,
            )
            schema[int_field] = int_validator

        bool_field, bool_validator = _build_bool_option_field(
            options,
            CONF_DEBUG_MODE,
            DEFAULT_DEBUG_MODE,
        )
        schema[bool_field] = bool_validator

        bool_field, bool_validator = _build_bool_option_field(
            options,
            CONF_LIGHT_TURN_ON_ON_ADJUST,
            DEFAULT_LIGHT_TURN_ON_ON_ADJUST,
        )
        schema[bool_field] = bool_validator

        bool_field, bool_validator = _build_bool_option_field(
            options,
            CONF_ROOM_AREA_SYNC_FORCE,
            DEFAULT_ROOM_AREA_SYNC_FORCE,
        )
        schema[bool_field] = bool_validator

        bool_field, bool_validator = _build_bool_option_field(
            options,
            CONF_COMMAND_RESULT_VERIFY,
            DEFAULT_COMMAND_RESULT_VERIFY,
        )
        schema[bool_field] = bool_validator

        for mode_key, list_key in (
            (CONF_DEVICE_FILTER_HOME_MODE, CONF_DEVICE_FILTER_HOME_LIST),
            (CONF_DEVICE_FILTER_MODEL_MODE, CONF_DEVICE_FILTER_MODEL_LIST),
            (CONF_DEVICE_FILTER_SSID_MODE, CONF_DEVICE_FILTER_SSID_LIST),
            (CONF_DEVICE_FILTER_DID_MODE, CONF_DEVICE_FILTER_DID_LIST),
        ):
            schema[
                vol.Required(
                    mode_key,
                    default=options.get(mode_key, DEFAULT_DEVICE_FILTER_MODE),
                )
            ] = vol.In(_DEVICE_FILTER_MODE_VALUES)
            schema[
                vol.Optional(
                    list_key,
                    default=_coerce_device_filter_list_option(
                        options.get(list_key, "")
                    ),
                )
            ] = _text_selector()

        return vol.Schema(schema)
