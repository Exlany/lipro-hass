"""Options flow for Lipro."""

from __future__ import annotations

from collections.abc import Mapping

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
    MAX_POWER_QUERY_INTERVAL,
    MAX_REQUEST_TIMEOUT,
    MAX_SCAN_INTERVAL,
    MIN_POWER_QUERY_INTERVAL,
    MIN_REQUEST_TIMEOUT,
    MIN_SCAN_INTERVAL,
)
from ..core.device_filter_codec import (
    coerce_device_filter_list_text,
    normalize_device_filter_mode,
    split_device_filter_text,
)
from .schemas import text_selector

# Options flow key for toggling advanced settings step
_CONF_SHOW_ADVANCED = "show_advanced"

_DEVICE_FILTER_MODE_VALUES: tuple[str, str, str] = (
    DEVICE_FILTER_MODE_OFF,
    DEVICE_FILTER_MODE_INCLUDE,
    DEVICE_FILTER_MODE_EXCLUDE,
)
_BOOLEAN_OPTION_KEYS: tuple[str, ...] = (
    CONF_MQTT_ENABLED,
    CONF_ENABLE_POWER_MONITORING,
    CONF_ANONYMOUS_SHARE_ENABLED,
    CONF_ANONYMOUS_SHARE_ERRORS,
    CONF_DEBUG_MODE,
    CONF_LIGHT_TURN_ON_ON_ADJUST,
    CONF_ROOM_AREA_SYNC_FORCE,
    CONF_COMMAND_RESULT_VERIFY,
)
_INTEGER_OPTION_KEYS: tuple[str, ...] = (
    CONF_SCAN_INTERVAL,
    CONF_POWER_QUERY_INTERVAL,
    CONF_REQUEST_TIMEOUT,
)
_DEVICE_FILTER_MODE_KEYS: tuple[str, ...] = (
    CONF_DEVICE_FILTER_HOME_MODE,
    CONF_DEVICE_FILTER_MODEL_MODE,
    CONF_DEVICE_FILTER_SSID_MODE,
    CONF_DEVICE_FILTER_DID_MODE,
)
_DEVICE_FILTER_LIST_KEYS: tuple[str, ...] = (
    CONF_DEVICE_FILTER_HOME_LIST,
    CONF_DEVICE_FILTER_MODEL_LIST,
    CONF_DEVICE_FILTER_SSID_LIST,
    CONF_DEVICE_FILTER_DID_LIST,
)
_INIT_INT_OPTION_SPECS: tuple[tuple[str, int, int, int], ...] = (
    (CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, MIN_SCAN_INTERVAL, MAX_SCAN_INTERVAL),
)
_INIT_BOOL_OPTION_SPECS: tuple[tuple[str, bool], ...] = (
    (CONF_MQTT_ENABLED, DEFAULT_MQTT_ENABLED),
    (CONF_ENABLE_POWER_MONITORING, DEFAULT_ENABLE_POWER_MONITORING),
    (CONF_ANONYMOUS_SHARE_ENABLED, DEFAULT_ANONYMOUS_SHARE_ENABLED),
    (CONF_ANONYMOUS_SHARE_ERRORS, DEFAULT_ANONYMOUS_SHARE_ERRORS),
)
_ADVANCED_INT_OPTION_SPECS: tuple[tuple[str, int, int, int], ...] = (
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
)
_ADVANCED_BOOL_OPTION_SPECS: tuple[tuple[str, bool], ...] = (
    (CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE),
    (CONF_LIGHT_TURN_ON_ON_ADJUST, DEFAULT_LIGHT_TURN_ON_ON_ADJUST),
    (CONF_ROOM_AREA_SYNC_FORCE, DEFAULT_ROOM_AREA_SYNC_FORCE),
    (CONF_COMMAND_RESULT_VERIFY, DEFAULT_COMMAND_RESULT_VERIFY),
)
_DEVICE_FILTER_OPTION_PAIRS: tuple[tuple[str, str], ...] = (
    (CONF_DEVICE_FILTER_HOME_MODE, CONF_DEVICE_FILTER_HOME_LIST),
    (CONF_DEVICE_FILTER_MODEL_MODE, CONF_DEVICE_FILTER_MODEL_LIST),
    (CONF_DEVICE_FILTER_SSID_MODE, CONF_DEVICE_FILTER_SSID_LIST),
    (CONF_DEVICE_FILTER_DID_MODE, CONF_DEVICE_FILTER_DID_LIST),
)

type PersistedOptionValue = bool | int | str
type PersistedOptions = dict[str, PersistedOptionValue]
type OptionsMapping = Mapping[str, object]
type OptionsSchema = dict[vol.Marker, object]


def _split_device_filter_text(value: str) -> list[str]:
    """Split raw filter text into canonical tokens."""
    return split_device_filter_text(value)


def _resolve_bool_option_default(
    options: OptionsMapping,
    key: str,
    default: bool,
) -> bool:
    """Return one safe boolean default from persisted options."""
    value = options.get(key, default)
    return value if isinstance(value, bool) else default


def _resolve_int_option_default(
    options: OptionsMapping,
    key: str,
    default: int,
) -> int:
    """Return one safe integer default from persisted options."""
    value = options.get(key, default)
    return value if isinstance(value, int) and not isinstance(value, bool) else default


def _build_bool_option_field(
    options: OptionsMapping,
    key: str,
    default: bool,
) -> tuple[vol.Marker, type[bool]]:
    """Build a required boolean option field for options schema."""
    return (
        vol.Required(
            key,
            default=_resolve_bool_option_default(options, key, default),
        ),
        bool,
    )


def _build_int_option_field(
    options: OptionsMapping,
    key: str,
    default: int,
    min_value: int,
    max_value: int,
) -> tuple[vol.Marker, vol.All]:
    """Build a required bounded integer option field for options schema."""
    return (
        vol.Required(
            key,
            default=_resolve_int_option_default(options, key, default),
        ),
        vol.All(
            vol.Coerce(int),
            vol.Range(min=min_value, max=max_value),
        ),
    )


def _coerce_device_filter_list_option(value: object) -> str:
    """Coerce stored filter-list option to canonical, form-friendly text."""
    return coerce_device_filter_list_text(value)


def _normalize_device_filter_mode_option(value: object) -> str:
    """Normalize raw mode option to one canonical device filter mode."""
    return normalize_device_filter_mode(value)


def _add_int_option_fields(
    schema: OptionsSchema,
    options: OptionsMapping,
    specs: tuple[tuple[str, int, int, int], ...],
) -> None:
    """Append bounded integer option fields to one schema mapping."""
    for key, default, min_value, max_value in specs:
        int_field, int_validator = _build_int_option_field(
            options,
            key,
            default,
            min_value,
            max_value,
        )
        schema[int_field] = int_validator


def _add_bool_option_fields(
    schema: OptionsSchema,
    options: OptionsMapping,
    specs: tuple[tuple[str, bool], ...],
) -> None:
    """Append boolean option fields to one schema mapping."""
    for key, default in specs:
        bool_field, bool_validator = _build_bool_option_field(options, key, default)
        schema[bool_field] = bool_validator


def _add_device_filter_option_fields(
    schema: OptionsSchema,
    options: OptionsMapping,
) -> None:
    """Append device-filter mode and list fields to one schema mapping."""
    for mode_key, list_key in _DEVICE_FILTER_OPTION_PAIRS:
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
                default=_coerce_device_filter_list_option(options.get(list_key, "")),
            )
        ] = text_selector()


def _extract_persisted_options(user_input: OptionsMapping) -> PersistedOptions:
    """Extract the supported persisted options from one validated form payload."""
    extracted: PersistedOptions = {}

    for key in _BOOLEAN_OPTION_KEYS:
        value = user_input.get(key)
        if isinstance(value, bool):
            extracted[key] = value

    for key in _INTEGER_OPTION_KEYS:
        value = user_input.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            extracted[key] = value

    for key in _DEVICE_FILTER_MODE_KEYS:
        if key in user_input:
            extracted[key] = _normalize_device_filter_mode_option(user_input.get(key))

    for key in _DEVICE_FILTER_LIST_KEYS:
        if key in user_input:
            value = user_input.get(key)
            extracted[key] = (
                value
                if isinstance(value, str)
                else _coerce_device_filter_list_option(value)
            )

    return extracted


class LiproOptionsFlow(OptionsFlow):
    """Handle Lipro options."""

    def __init__(self) -> None:
        """Initialize options flow."""
        super().__init__()
        self._options: PersistedOptions = {}

    async def async_step_init(
        self,
        user_input: dict[str, object] | None = None,
    ) -> ConfigFlowResult:
        """Manage basic options."""
        if user_input is not None:
            show_advanced = _resolve_bool_option_default(
                user_input,
                _CONF_SHOW_ADVANCED,
                False,
            )
            self._options.update(_extract_persisted_options(user_input))

            if show_advanced:
                return await self.async_step_advanced()

            return self._save_options()

        return self.async_show_form(
            step_id="init",
            data_schema=self._build_init_schema(),
        )

    async def async_step_advanced(
        self,
        user_input: dict[str, object] | None = None,
    ) -> ConfigFlowResult:
        """Manage advanced options."""
        if user_input is not None:
            self._options.update(_extract_persisted_options(user_input))
            return self._save_options()

        return self.async_show_form(
            step_id="advanced",
            data_schema=self._build_advanced_schema(),
        )

    def _save_options(self) -> ConfigFlowResult:
        """Save options, merging with existing advanced options if not visited."""
        merged = dict(self.config_entry.options)
        merged.update(self._options)

        for mode_key in _DEVICE_FILTER_MODE_KEYS:
            if mode_key in merged:
                merged[mode_key] = _normalize_device_filter_mode_option(
                    merged.get(mode_key)
                )

        for list_key in _DEVICE_FILTER_LIST_KEYS:
            if list_key in merged:
                merged[list_key] = _coerce_device_filter_list_option(
                    merged.get(list_key)
                )

        return self.async_create_entry(title="", data=merged)

    def _build_init_schema(self) -> vol.Schema:
        """Build the basic options schema."""
        options = self.config_entry.options
        schema: OptionsSchema = {}
        _add_int_option_fields(schema, options, _INIT_INT_OPTION_SPECS)
        _add_bool_option_fields(schema, options, _INIT_BOOL_OPTION_SPECS)
        schema[vol.Optional(_CONF_SHOW_ADVANCED, default=False)] = bool
        return vol.Schema(schema)

    def _build_advanced_schema(self) -> vol.Schema:
        """Build the advanced options schema."""
        options = self.config_entry.options
        schema: OptionsSchema = {}
        _add_int_option_fields(schema, options, _ADVANCED_INT_OPTION_SPECS)
        _add_bool_option_fields(schema, options, _ADVANCED_BOOL_OPTION_SPECS)
        _add_device_filter_option_fields(schema, options)
        return vol.Schema(schema)
