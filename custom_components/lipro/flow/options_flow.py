"""Options flow for Lipro."""

from __future__ import annotations

from collections.abc import Mapping
import re
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlowResult, OptionsFlow

from ..const.config import (
    CONF_ANONYMOUS_SHARE_ENABLED,
    CONF_ANONYMOUS_SHARE_ERRORS,
    CONF_COMMAND_RESULT_VERIFY,
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
    CONF_POWER_QUERY_INTERVAL,
    CONF_REQUEST_TIMEOUT,
    CONF_ROOM_AREA_SYNC_FORCE,
    CONF_SCAN_INTERVAL,
    DEFAULT_ANONYMOUS_SHARE_ENABLED,
    DEFAULT_ANONYMOUS_SHARE_ERRORS,
    DEFAULT_COMMAND_RESULT_VERIFY,
    DEFAULT_DEBUG_MODE,
    DEFAULT_DEVICE_FILTER_MODE,
    DEFAULT_ENABLE_POWER_MONITORING,
    DEFAULT_LIGHT_TURN_ON_ON_ADJUST,
    DEFAULT_MQTT_ENABLED,
    DEFAULT_POWER_QUERY_INTERVAL,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_ROOM_AREA_SYNC_FORCE,
    DEFAULT_SCAN_INTERVAL,
    DEVICE_FILTER_MODE_EXCLUDE,
    DEVICE_FILTER_MODE_INCLUDE,
    DEVICE_FILTER_MODE_OFF,
    MAX_DEVICE_FILTER_LIST_CHARS,
    MAX_DEVICE_FILTER_LIST_ITEMS,
    MAX_POWER_QUERY_INTERVAL,
    MAX_REQUEST_TIMEOUT,
    MAX_SCAN_INTERVAL,
    MIN_POWER_QUERY_INTERVAL,
    MIN_REQUEST_TIMEOUT,
    MIN_SCAN_INTERVAL,
)
from .schemas import text_selector

# Options flow key for toggling advanced settings step
_CONF_SHOW_ADVANCED = "show_advanced"

_DEVICE_FILTER_MODE_VALUES: tuple[str, str, str] = (
    DEVICE_FILTER_MODE_OFF,
    DEVICE_FILTER_MODE_INCLUDE,
    DEVICE_FILTER_MODE_EXCLUDE,
)
_DEVICE_FILTER_LIST_SPLIT_RE = re.compile(r"[\r\n,;]+")


def _split_device_filter_text(value: str) -> list[str]:
    """Split raw filter text into canonical tokens."""
    normalized = (
        value[:MAX_DEVICE_FILTER_LIST_CHARS].replace("\r\n", "\n").replace("\r", "\n")
    )
    tokens: list[str] = []
    for token in _DEVICE_FILTER_LIST_SPLIT_RE.split(normalized):
        stripped = token.strip()
        if not stripped:
            continue
        tokens.append(stripped)
        if len(tokens) >= MAX_DEVICE_FILTER_LIST_ITEMS:
            break
    return tokens


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
    """Coerce stored filter-list option to canonical, form-friendly text."""
    if isinstance(value, str):
        separator = ", "
        if "," in value and not any(marker in value for marker in ("\r", "\n", ";")):
            separator = ","
        return separator.join(_split_device_filter_text(value))[:MAX_DEVICE_FILTER_LIST_CHARS]
    if isinstance(value, (list, tuple, set, frozenset)):
        parts: list[str] = []
        for item in value:
            for token in _split_device_filter_text(str(item)):
                parts.append(token)
                if len(parts) >= MAX_DEVICE_FILTER_LIST_ITEMS:
                    break
            if len(parts) >= MAX_DEVICE_FILTER_LIST_ITEMS:
                break
        return ", ".join(parts)[:MAX_DEVICE_FILTER_LIST_CHARS]
    return ""


def _normalize_device_filter_mode_option(value: Any) -> str:
    """Normalize raw mode option to one canonical device filter mode."""
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in _DEVICE_FILTER_MODE_VALUES:
            return normalized
    return DEFAULT_DEVICE_FILTER_MODE


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

        for mode_key in (
            CONF_DEVICE_FILTER_HOME_MODE,
            CONF_DEVICE_FILTER_MODEL_MODE,
            CONF_DEVICE_FILTER_SSID_MODE,
            CONF_DEVICE_FILTER_DID_MODE,
        ):
            if mode_key in merged:
                merged[mode_key] = _normalize_device_filter_mode_option(
                    merged.get(mode_key)
                )

        for list_key in (
            CONF_DEVICE_FILTER_HOME_LIST,
            CONF_DEVICE_FILTER_MODEL_LIST,
            CONF_DEVICE_FILTER_SSID_LIST,
            CONF_DEVICE_FILTER_DID_LIST,
        ):
            if list_key in merged:
                merged[list_key] = _coerce_device_filter_list_option(
                    merged.get(list_key)
                )

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
            bool_field, bool_validator = _build_bool_option_field(options, key, default)
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

        for key, default in (
            (CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE),
            (CONF_LIGHT_TURN_ON_ON_ADJUST, DEFAULT_LIGHT_TURN_ON_ON_ADJUST),
            (CONF_ROOM_AREA_SYNC_FORCE, DEFAULT_ROOM_AREA_SYNC_FORCE),
            (CONF_COMMAND_RESULT_VERIFY, DEFAULT_COMMAND_RESULT_VERIFY),
        ):
            bool_field, bool_validator = _build_bool_option_field(options, key, default)
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
                    default=_normalize_device_filter_mode_option(
                        options.get(mode_key, DEFAULT_DEVICE_FILTER_MODE),
                    ),
                )
            ] = vol.In(_DEVICE_FILTER_MODE_VALUES)
            schema[
                vol.Optional(
                    list_key,
                    default=_coerce_device_filter_list_option(
                        options.get(list_key, "")
                    ),
                )
            ] = text_selector()

        return vol.Schema(schema)
