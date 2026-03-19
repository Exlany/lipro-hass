"""Tests for Lipro config flow.

These tests require pytest-homeassistant-custom-component to provide the 'hass' fixture.
Install with: pip install pytest-homeassistant-custom-component

Note: On Windows, this may require Microsoft C++ Build Tools.
"""

from __future__ import annotations

from pytest_homeassistant_custom_component.common import MockConfigEntry
import voluptuous as vol

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import (
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
    CONF_LIGHT_TURN_ON_ON_ADJUST,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_POWER_QUERY_INTERVAL,
    CONF_ROOM_AREA_SYNC_FORCE,
    DEFAULT_COMMAND_RESULT_VERIFY,
    DEFAULT_POWER_QUERY_INTERVAL,
    DEVICE_FILTER_MODE_EXCLUDE,
    DEVICE_FILTER_MODE_INCLUDE,
    DEVICE_FILTER_MODE_OFF,
    MAX_DEVICE_FILTER_LIST_CHARS,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .support import _get_schema_marker


async def test_options_flow(
    hass: HomeAssistant,
) -> None:
    """Test options flow."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "user_id": 10001,
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "scan_interval": 60,
            "anonymous_share_enabled": False,
            "anonymous_share_errors": True,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["scan_interval"] == 60
    assert CONF_LIGHT_TURN_ON_ON_ADJUST not in result["data"]

async def test_options_flow_normalizes_device_filter_modes_case_on_save(
    hass: HomeAssistant,
) -> None:
    """Options flow should normalize stored device-filter mode casing on save."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "user_id": 10001,
        },
        options={
            CONF_DEVICE_FILTER_HOME_MODE: "INCLUDE",
            CONF_DEVICE_FILTER_HOME_LIST: "Home A",
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "scan_interval": 60,
            "anonymous_share_enabled": False,
            "anonymous_share_errors": True,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_DEVICE_FILTER_HOME_MODE] == DEVICE_FILTER_MODE_INCLUDE

async def test_options_flow_advanced_schema_normalizes_mode_case(
    hass: HomeAssistant,
) -> None:
    """Advanced step should normalize stored mode casing for defaults."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "user_id": 10001,
        },
        options={
            CONF_DEVICE_FILTER_HOME_MODE: "INCLUDE",
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "scan_interval": 30,
            "mqtt_enabled": False,
            "enable_power_monitoring": False,
            "anonymous_share_enabled": True,
            "anonymous_share_errors": True,
            "show_advanced": True,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "advanced"

    data_schema = result["data_schema"]
    assert data_schema is not None
    marker = _get_schema_marker(data_schema, CONF_DEVICE_FILTER_HOME_MODE)
    assert isinstance(marker, vol.Required)
    default = marker.default() if callable(marker.default) else marker.default
    assert default == DEVICE_FILTER_MODE_INCLUDE
    command_result_verify_marker = _get_schema_marker(
        data_schema, CONF_COMMAND_RESULT_VERIFY
    )
    assert isinstance(command_result_verify_marker, vol.Required)
    command_result_verify_default = (
        command_result_verify_marker.default()
        if callable(command_result_verify_marker.default)
        else command_result_verify_marker.default
    )
    assert command_result_verify_default is DEFAULT_COMMAND_RESULT_VERIFY

    power_query_interval_marker = _get_schema_marker(
        data_schema, CONF_POWER_QUERY_INTERVAL
    )
    assert isinstance(power_query_interval_marker, vol.Required)
    power_query_interval_default = (
        power_query_interval_marker.default()
        if callable(power_query_interval_marker.default)
        else power_query_interval_marker.default
    )
    assert power_query_interval_default == DEFAULT_POWER_QUERY_INTERVAL

async def test_options_flow_advanced_step(
    hass: HomeAssistant,
) -> None:
    """Test options flow advanced step and merged save behavior."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "user_id": 10001,
        },
        options={
            "scan_interval": 45,
            "mqtt_enabled": True,
            "enable_power_monitoring": True,
            CONF_LIGHT_TURN_ON_ON_ADJUST: True,
            CONF_ROOM_AREA_SYNC_FORCE: False,
            CONF_COMMAND_RESULT_VERIFY: False,
            "anonymous_share_enabled": True,
            "anonymous_share_errors": False,
            "power_query_interval": 60,
            "request_timeout": 20,
            CONF_DEBUG_MODE: False,
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "scan_interval": 30,
            "mqtt_enabled": False,
            "enable_power_monitoring": False,
            "anonymous_share_enabled": True,
            "anonymous_share_errors": True,
            "show_advanced": True,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "advanced"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "power_query_interval": 120,
            "request_timeout": 45,
            CONF_DEBUG_MODE: True,
            CONF_LIGHT_TURN_ON_ON_ADJUST: False,
            CONF_ROOM_AREA_SYNC_FORCE: True,
            CONF_COMMAND_RESULT_VERIFY: True,
            CONF_DEVICE_FILTER_HOME_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_HOME_LIST: "My Home",
            CONF_DEVICE_FILTER_MODEL_MODE: DEVICE_FILTER_MODE_EXCLUDE,
            CONF_DEVICE_FILTER_MODEL_LIST: "gateway",
            CONF_DEVICE_FILTER_SSID_MODE: DEVICE_FILTER_MODE_OFF,
            CONF_DEVICE_FILTER_SSID_LIST: "",
            CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_DID_LIST: "03ab5ccd7c000001,03ab5ccd7c000002",
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["scan_interval"] == 30
    assert result["data"]["mqtt_enabled"] is False
    assert result["data"]["enable_power_monitoring"] is False
    assert result["data"][CONF_LIGHT_TURN_ON_ON_ADJUST] is False
    assert result["data"][CONF_ROOM_AREA_SYNC_FORCE] is True
    assert result["data"][CONF_COMMAND_RESULT_VERIFY] is True
    assert result["data"]["power_query_interval"] == 120
    assert result["data"]["request_timeout"] == 45
    assert result["data"][CONF_DEBUG_MODE] is True
    assert result["data"][CONF_DEVICE_FILTER_HOME_MODE] == DEVICE_FILTER_MODE_INCLUDE
    assert result["data"][CONF_DEVICE_FILTER_HOME_LIST] == "My Home"
    assert result["data"][CONF_DEVICE_FILTER_MODEL_MODE] == DEVICE_FILTER_MODE_EXCLUDE
    assert result["data"][CONF_DEVICE_FILTER_MODEL_LIST] == "gateway"
    assert result["data"][CONF_DEVICE_FILTER_SSID_MODE] == DEVICE_FILTER_MODE_OFF
    assert result["data"][CONF_DEVICE_FILTER_SSID_LIST] == ""
    assert result["data"][CONF_DEVICE_FILTER_DID_MODE] == DEVICE_FILTER_MODE_INCLUDE
    assert (
        result["data"][CONF_DEVICE_FILTER_DID_LIST]
        == "03ab5ccd7c000001,03ab5ccd7c000002"
    )

async def test_options_flow_preserves_device_filter_token_boundaries_on_save(
    hass: HomeAssistant,
) -> None:
    """Options flow should preserve newline/CRLF-separated filter tokens."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "user_id": 10001,
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "scan_interval": 30,
            "mqtt_enabled": False,
            "enable_power_monitoring": False,
            "anonymous_share_enabled": True,
            "anonymous_share_errors": True,
            "show_advanced": True,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "advanced"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "power_query_interval": 120,
            "request_timeout": 45,
            CONF_DEBUG_MODE: True,
            CONF_LIGHT_TURN_ON_ON_ADJUST: False,
            CONF_ROOM_AREA_SYNC_FORCE: True,
            CONF_COMMAND_RESULT_VERIFY: True,
            CONF_DEVICE_FILTER_HOME_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_HOME_LIST: "Main Home\r\nGuest Home",
            CONF_DEVICE_FILTER_MODEL_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_MODEL_LIST: "fanLight; Strip",
            CONF_DEVICE_FILTER_SSID_MODE: DEVICE_FILTER_MODE_OFF,
            CONF_DEVICE_FILTER_SSID_LIST: "",
            CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_DID_LIST: "03ab5ccd7c000001\n03ab5ccd7c000002",
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_DEVICE_FILTER_HOME_LIST] == "Main Home, Guest Home"
    assert result["data"][CONF_DEVICE_FILTER_MODEL_LIST] == "fanLight, Strip"
    assert (
        result["data"][CONF_DEVICE_FILTER_DID_LIST]
        == "03ab5ccd7c000001, 03ab5ccd7c000002"
    )

async def test_options_flow_truncates_device_filter_list_string_inputs(
    hass: HomeAssistant,
) -> None:
    """Options flow should hard-cap device-filter list field length."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "user_id": 10001,
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "scan_interval": 30,
            "mqtt_enabled": False,
            "enable_power_monitoring": False,
            "anonymous_share_enabled": True,
            "anonymous_share_errors": True,
            "show_advanced": True,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "advanced"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "power_query_interval": 120,
            "request_timeout": 45,
            CONF_DEBUG_MODE: True,
            CONF_LIGHT_TURN_ON_ON_ADJUST: False,
            CONF_ROOM_AREA_SYNC_FORCE: True,
            CONF_COMMAND_RESULT_VERIFY: True,
            CONF_DEVICE_FILTER_HOME_MODE: DEVICE_FILTER_MODE_OFF,
            CONF_DEVICE_FILTER_HOME_LIST: "",
            CONF_DEVICE_FILTER_MODEL_MODE: DEVICE_FILTER_MODE_OFF,
            CONF_DEVICE_FILTER_MODEL_LIST: "",
            CONF_DEVICE_FILTER_SSID_MODE: DEVICE_FILTER_MODE_OFF,
            CONF_DEVICE_FILTER_SSID_LIST: "",
            CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_DID_LIST: "x" * (MAX_DEVICE_FILTER_LIST_CHARS + 10),
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert (
        len(result["data"][CONF_DEVICE_FILTER_DID_LIST]) == MAX_DEVICE_FILTER_LIST_CHARS
    )

async def test_options_flow_coerces_non_string_device_filter_lists(
    hass: HomeAssistant,
) -> None:
    """Options flow should normalize non-string device-filter list values."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "user_id": 10001,
        },
        options={
            CONF_DEVICE_FILTER_DID_LIST: ["a", "b"],
            CONF_DEVICE_FILTER_MODEL_LIST: ["x" * (MAX_DEVICE_FILTER_LIST_CHARS + 10)],
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "scan_interval": 60,
            "anonymous_share_enabled": False,
            "anonymous_share_errors": True,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_DEVICE_FILTER_DID_LIST] == "a, b"
    assert (
        len(result["data"][CONF_DEVICE_FILTER_MODEL_LIST])
        == MAX_DEVICE_FILTER_LIST_CHARS
    )
