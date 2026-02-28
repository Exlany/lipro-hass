"""Tests for Lipro integration __init__.py module.

Tests cover:
- PLATFORMS list completeness
- Service schema structure (keys, required/optional)
- Service constants definitions
- Attribute constants definitions
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
import voluptuous as vol

from custom_components.lipro import (
    ATTR_COMMAND,
    ATTR_DAYS,
    ATTR_DEVICE_ID,
    ATTR_EVENTS,
    ATTR_MESH_TYPE,
    ATTR_MSG_SN,
    ATTR_NOTE,
    ATTR_PROPERTIES,
    ATTR_SCHEDULE_IDS,
    ATTR_SENSOR_DEVICE_ID,
    ATTR_TIMES,
    PLATFORMS,
    SERVICE_ADD_SCHEDULE,
    SERVICE_ADD_SCHEDULE_SCHEMA,
    SERVICE_DELETE_SCHEDULES,
    SERVICE_DELETE_SCHEDULES_SCHEMA,
    SERVICE_FETCH_BODY_SENSOR_HISTORY,
    SERVICE_FETCH_DOOR_SENSOR_HISTORY,
    SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
    SERVICE_GET_ANONYMOUS_SHARE_REPORT,
    SERVICE_GET_CITY,
    SERVICE_GET_DEVELOPER_REPORT,
    SERVICE_GET_SCHEDULES,
    SERVICE_GET_SCHEDULES_SCHEMA,
    SERVICE_QUERY_COMMAND_RESULT,
    SERVICE_QUERY_COMMAND_RESULT_SCHEMA,
    SERVICE_SEND_COMMAND,
    SERVICE_SEND_COMMAND_SCHEMA,
    SERVICE_SUBMIT_ANONYMOUS_SHARE,
    SERVICE_SUBMIT_DEVELOPER_FEEDBACK,
    SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA,
    _async_handle_add_schedule,
    _async_handle_delete_schedules,
    _async_handle_fetch_body_sensor_history,
    _async_handle_fetch_door_sensor_history,
    _async_handle_get_anonymous_share_report,
    _async_handle_get_city,
    _async_handle_get_developer_report,
    _async_handle_get_schedules,
    _async_handle_query_command_result,
    _async_handle_send_command,
    _async_handle_submit_anonymous_share,
    _async_handle_submit_developer_feedback,
    _get_device_and_coordinator,
    _summarize_service_properties,
    async_setup,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.lipro.const import (
    CONF_ACCESS_TOKEN,
    CONF_EXPIRES_AT,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REFRESH_TOKEN,
    CONF_REQUEST_TIMEOUT,
    CONF_SCAN_INTERVAL,
    DEFAULT_REQUEST_TIMEOUT,
    DOMAIN,
    MAX_SCAN_INTERVAL,
)
from custom_components.lipro.core import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
)
from custom_components.lipro.core.device import LiproDevice
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    HomeAssistantError,
    ServiceValidationError,
)
from homeassistant.helpers import entity_registry as er


class TestPlatforms:
    """Tests for the PLATFORMS list."""

    def test_platforms_count(self):
        """Test PLATFORMS has exactly 9 entries."""
        assert len(PLATFORMS) == 9

    def test_platforms_is_list(self):
        """Test PLATFORMS is a list."""
        assert isinstance(PLATFORMS, list)

    def test_platforms_contains_light(self):
        """Test PLATFORMS includes Platform.LIGHT."""
        assert Platform.LIGHT in PLATFORMS

    def test_platforms_contains_cover(self):
        """Test PLATFORMS includes Platform.COVER."""
        assert Platform.COVER in PLATFORMS

    def test_platforms_contains_switch(self):
        """Test PLATFORMS includes Platform.SWITCH."""
        assert Platform.SWITCH in PLATFORMS

    def test_platforms_contains_fan(self):
        """Test PLATFORMS includes Platform.FAN."""
        assert Platform.FAN in PLATFORMS

    def test_platforms_contains_climate(self):
        """Test PLATFORMS includes Platform.CLIMATE."""
        assert Platform.CLIMATE in PLATFORMS

    def test_platforms_contains_binary_sensor(self):
        """Test PLATFORMS includes Platform.BINARY_SENSOR."""
        assert Platform.BINARY_SENSOR in PLATFORMS

    def test_platforms_contains_sensor(self):
        """Test PLATFORMS includes Platform.SENSOR."""
        assert Platform.SENSOR in PLATFORMS

    def test_platforms_contains_select(self):
        """Test PLATFORMS includes Platform.SELECT."""
        assert Platform.SELECT in PLATFORMS

    def test_platforms_contains_update(self):
        """Test PLATFORMS includes Platform.UPDATE."""
        assert Platform.UPDATE in PLATFORMS

    def test_platforms_no_duplicates(self):
        """Test PLATFORMS has no duplicate entries."""
        assert len(PLATFORMS) == len(set(PLATFORMS))


class TestServiceConstants:
    """Tests for service constant definitions."""

    def test_service_send_command(self):
        """Test SERVICE_SEND_COMMAND is defined correctly."""
        assert SERVICE_SEND_COMMAND == "send_command"

    def test_service_get_schedules(self):
        """Test SERVICE_GET_SCHEDULES is defined correctly."""
        assert SERVICE_GET_SCHEDULES == "get_schedules"

    def test_service_add_schedule(self):
        """Test SERVICE_ADD_SCHEDULE is defined correctly."""
        assert SERVICE_ADD_SCHEDULE == "add_schedule"

    def test_service_delete_schedules(self):
        """Test SERVICE_DELETE_SCHEDULES is defined correctly."""
        assert SERVICE_DELETE_SCHEDULES == "delete_schedules"

    def test_service_submit_anonymous_share(self):
        """Test SERVICE_SUBMIT_ANONYMOUS_SHARE is defined correctly."""
        assert SERVICE_SUBMIT_ANONYMOUS_SHARE == "submit_anonymous_share"

    def test_service_get_anonymous_share_report(self):
        """Test SERVICE_GET_ANONYMOUS_SHARE_REPORT is defined correctly."""
        assert SERVICE_GET_ANONYMOUS_SHARE_REPORT == "get_anonymous_share_report"

    def test_service_get_developer_report(self):
        """Test SERVICE_GET_DEVELOPER_REPORT is defined correctly."""
        assert SERVICE_GET_DEVELOPER_REPORT == "get_developer_report"

    def test_service_submit_developer_feedback(self):
        """Test SERVICE_SUBMIT_DEVELOPER_FEEDBACK is defined correctly."""
        assert SERVICE_SUBMIT_DEVELOPER_FEEDBACK == "submit_developer_feedback"

    def test_service_query_command_result(self):
        """Test SERVICE_QUERY_COMMAND_RESULT is defined correctly."""
        assert SERVICE_QUERY_COMMAND_RESULT == "query_command_result"

    def test_service_get_city(self):
        """Test SERVICE_GET_CITY is defined correctly."""
        assert SERVICE_GET_CITY == "get_city"

    def test_service_fetch_body_sensor_history(self):
        """Test SERVICE_FETCH_BODY_SENSOR_HISTORY is defined correctly."""
        assert SERVICE_FETCH_BODY_SENSOR_HISTORY == "fetch_body_sensor_history"

    def test_service_fetch_door_sensor_history(self):
        """Test SERVICE_FETCH_DOOR_SENSOR_HISTORY is defined correctly."""
        assert SERVICE_FETCH_DOOR_SENSOR_HISTORY == "fetch_door_sensor_history"

    def test_service_constants_are_strings(self):
        """Test all service constants are strings."""
        assert isinstance(SERVICE_SEND_COMMAND, str)
        assert isinstance(SERVICE_GET_SCHEDULES, str)
        assert isinstance(SERVICE_ADD_SCHEDULE, str)
        assert isinstance(SERVICE_DELETE_SCHEDULES, str)
        assert isinstance(SERVICE_SUBMIT_ANONYMOUS_SHARE, str)
        assert isinstance(SERVICE_GET_ANONYMOUS_SHARE_REPORT, str)
        assert isinstance(SERVICE_GET_DEVELOPER_REPORT, str)
        assert isinstance(SERVICE_SUBMIT_DEVELOPER_FEEDBACK, str)
        assert isinstance(SERVICE_QUERY_COMMAND_RESULT, str)
        assert isinstance(SERVICE_GET_CITY, str)
        assert isinstance(SERVICE_FETCH_BODY_SENSOR_HISTORY, str)
        assert isinstance(SERVICE_FETCH_DOOR_SENSOR_HISTORY, str)


class TestAttributeConstants:
    """Tests for attribute constant definitions."""

    def test_attr_device_id(self):
        """Test ATTR_DEVICE_ID value."""
        assert ATTR_DEVICE_ID == "device_id"

    def test_attr_command(self):
        """Test ATTR_COMMAND value."""
        assert ATTR_COMMAND == "command"

    def test_attr_properties(self):
        """Test ATTR_PROPERTIES value."""
        assert ATTR_PROPERTIES == "properties"

    def test_attr_days(self):
        """Test ATTR_DAYS value."""
        assert ATTR_DAYS == "days"

    def test_attr_times(self):
        """Test ATTR_TIMES value."""
        assert ATTR_TIMES == "times"

    def test_attr_events(self):
        """Test ATTR_EVENTS value."""
        assert ATTR_EVENTS == "events"

    def test_attr_schedule_ids(self):
        """Test ATTR_SCHEDULE_IDS value."""
        assert ATTR_SCHEDULE_IDS == "schedule_ids"

    def test_attribute_constants_are_strings(self):
        """Test all attribute constants are strings."""
        assert isinstance(ATTR_DEVICE_ID, str)
        assert isinstance(ATTR_COMMAND, str)
        assert isinstance(ATTR_PROPERTIES, str)
        assert isinstance(ATTR_DAYS, str)
        assert isinstance(ATTR_TIMES, str)
        assert isinstance(ATTR_EVENTS, str)
        assert isinstance(ATTR_SCHEDULE_IDS, str)

    def test_attr_msg_sn(self):
        """Test ATTR_MSG_SN value."""
        assert ATTR_MSG_SN == "msg_sn"

    def test_attr_sensor_device_id(self):
        """Test ATTR_SENSOR_DEVICE_ID value."""
        assert ATTR_SENSOR_DEVICE_ID == "sensor_device_id"

    def test_attr_mesh_type(self):
        """Test ATTR_MESH_TYPE value."""
        assert ATTR_MESH_TYPE == "mesh_type"


class TestSchemaStructure:
    """Tests for service schema structure (keys and required/optional).

    These tests inspect the schema objects directly without calling them,
    so they work in standalone mode without the full HA test environment.
    """

    @staticmethod
    def _get_schema_keys(schema: vol.Schema) -> dict[str, bool]:
        """Extract schema keys and whether they are required.

        Returns a dict of {key_name: is_required}.
        """
        result = {}
        for key in schema.schema:
            if isinstance(key, vol.Required):
                result[key.schema] = True
            elif isinstance(key, vol.Optional):
                result[key.schema] = False
            else:
                result[str(key)] = True
        return result

    def test_send_command_schema_is_vol_schema(self):
        """Test SERVICE_SEND_COMMAND_SCHEMA is a voluptuous Schema."""
        assert isinstance(SERVICE_SEND_COMMAND_SCHEMA, vol.Schema)

    def test_send_command_schema_keys(self):
        """Test SERVICE_SEND_COMMAND_SCHEMA has expected keys."""
        keys = self._get_schema_keys(SERVICE_SEND_COMMAND_SCHEMA)
        assert ATTR_COMMAND in keys
        assert keys[ATTR_COMMAND] is True  # required
        assert ATTR_DEVICE_ID in keys
        assert keys[ATTR_DEVICE_ID] is False  # optional
        assert ATTR_PROPERTIES in keys
        assert keys[ATTR_PROPERTIES] is False  # optional

    def test_get_schedules_schema_is_vol_schema(self):
        """Test SERVICE_GET_SCHEDULES_SCHEMA is a voluptuous Schema."""
        assert isinstance(SERVICE_GET_SCHEDULES_SCHEMA, vol.Schema)

    def test_get_schedules_schema_keys(self):
        """Test SERVICE_GET_SCHEDULES_SCHEMA has expected keys."""
        keys = self._get_schema_keys(SERVICE_GET_SCHEDULES_SCHEMA)
        assert ATTR_DEVICE_ID in keys
        assert keys[ATTR_DEVICE_ID] is False  # optional

    def test_add_schedule_schema_is_vol_schema(self):
        """Test SERVICE_ADD_SCHEDULE_SCHEMA is a voluptuous Schema."""
        assert isinstance(SERVICE_ADD_SCHEDULE_SCHEMA, vol.Schema)

    def test_add_schedule_schema_keys(self):
        """Test SERVICE_ADD_SCHEDULE_SCHEMA has expected keys."""
        keys = self._get_schema_keys(SERVICE_ADD_SCHEDULE_SCHEMA)
        assert ATTR_DEVICE_ID in keys
        assert keys[ATTR_DEVICE_ID] is False  # optional
        assert ATTR_DAYS in keys
        assert keys[ATTR_DAYS] is True  # required
        assert ATTR_TIMES in keys
        assert keys[ATTR_TIMES] is True  # required
        assert ATTR_EVENTS in keys
        assert keys[ATTR_EVENTS] is True  # required

    def test_delete_schedules_schema_is_vol_schema(self):
        """Test SERVICE_DELETE_SCHEDULES_SCHEMA is a voluptuous Schema."""
        assert isinstance(SERVICE_DELETE_SCHEDULES_SCHEMA, vol.Schema)

    def test_delete_schedules_schema_keys(self):
        """Test SERVICE_DELETE_SCHEDULES_SCHEMA has expected keys."""
        keys = self._get_schema_keys(SERVICE_DELETE_SCHEDULES_SCHEMA)
        assert ATTR_DEVICE_ID in keys
        assert keys[ATTR_DEVICE_ID] is False  # optional
        assert ATTR_SCHEDULE_IDS in keys
        assert keys[ATTR_SCHEDULE_IDS] is True  # required

    def test_submit_developer_feedback_schema_keys(self):
        """Test submit_developer_feedback schema has expected keys."""
        keys = self._get_schema_keys(SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA)
        assert ATTR_NOTE in keys
        assert keys[ATTR_NOTE] is False

    def test_query_command_result_schema_keys(self):
        """Test query_command_result schema has expected keys."""
        keys = self._get_schema_keys(SERVICE_QUERY_COMMAND_RESULT_SCHEMA)
        assert ATTR_DEVICE_ID in keys
        assert keys[ATTR_DEVICE_ID] is False
        assert ATTR_MSG_SN in keys
        assert keys[ATTR_MSG_SN] is True

    def test_fetch_sensor_history_schema_keys(self):
        """Test fetch sensor history schema has expected keys."""
        keys = self._get_schema_keys(SERVICE_FETCH_SENSOR_HISTORY_SCHEMA)
        assert ATTR_DEVICE_ID in keys
        assert keys[ATTR_DEVICE_ID] is False
        assert ATTR_SENSOR_DEVICE_ID in keys
        assert keys[ATTR_SENSOR_DEVICE_ID] is True
        assert ATTR_MESH_TYPE in keys
        assert keys[ATTR_MESH_TYPE] is False


class TestSchemaValidation:
    """Tests for service schema validation with actual data.

    These tests call the schemas with data, which requires cv.string and
    cv.ensure_list from homeassistant.helpers.config_validation to be real.
    """

    def test_send_command_valid_minimal(self):
        """Test send_command schema accepts minimal valid input."""
        result = SERVICE_SEND_COMMAND_SCHEMA({"command": "powerOn"})
        assert result["command"] == "powerOn"

    def test_send_command_valid_with_device_id(self):
        """Test send_command schema accepts input with device_id."""
        result = SERVICE_SEND_COMMAND_SCHEMA(
            {"device_id": "abc123", "command": "powerOn"}
        )
        assert result["device_id"] == "abc123"
        assert result["command"] == "powerOn"

    def test_send_command_valid_with_properties(self):
        """Test send_command schema accepts input with properties list."""
        result = SERVICE_SEND_COMMAND_SCHEMA(
            {
                "command": "changeState",
                "properties": [{"key": "brightness", "value": "100"}],
            }
        )
        assert result["command"] == "changeState"
        assert len(result["properties"]) == 1
        assert result["properties"][0]["key"] == "brightness"

    def test_send_command_missing_command_raises(self):
        """Test send_command schema rejects input without command."""
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_SEND_COMMAND_SCHEMA({"device_id": "abc123"})

    def test_send_command_empty_raises(self):
        """Test send_command schema rejects empty input."""
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_SEND_COMMAND_SCHEMA({})

    def test_send_command_properties_missing_key_raises(self):
        """Test send_command schema rejects properties without key."""
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_SEND_COMMAND_SCHEMA(
                {"command": "changeState", "properties": [{"value": "100"}]}
            )

    def test_send_command_properties_missing_value_raises(self):
        """Test send_command schema rejects properties without value."""
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_SEND_COMMAND_SCHEMA(
                {"command": "changeState", "properties": [{"key": "brightness"}]}
            )

    def test_get_schedules_valid_empty(self):
        """Test get_schedules schema accepts empty input."""
        result = SERVICE_GET_SCHEDULES_SCHEMA({})
        assert isinstance(result, dict)

    def test_get_schedules_valid_with_device_id(self):
        """Test get_schedules schema accepts input with device_id."""
        result = SERVICE_GET_SCHEDULES_SCHEMA({"device_id": "abc123"})
        assert result["device_id"] == "abc123"

    def test_add_schedule_valid_full(self):
        """Test add_schedule schema accepts valid full input."""
        result = SERVICE_ADD_SCHEDULE_SCHEMA(
            {"days": [1, 2, 3], "times": [3600, 7200], "events": [1, 0]}
        )
        assert result["days"] == [1, 2, 3]
        assert result["times"] == [3600, 7200]
        assert result["events"] == [1, 0]

    def test_add_schedule_missing_days_raises(self):
        """Test add_schedule schema rejects input without days."""
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_ADD_SCHEDULE_SCHEMA({"times": [3600], "events": [1]})

    def test_add_schedule_missing_times_raises(self):
        """Test add_schedule schema rejects input without times."""
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_ADD_SCHEDULE_SCHEMA({"days": [1], "events": [1]})

    def test_add_schedule_missing_events_raises(self):
        """Test add_schedule schema rejects input without events."""
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_ADD_SCHEDULE_SCHEMA({"days": [1], "times": [3600]})

    def test_add_schedule_days_out_of_range_raises(self):
        """Test add_schedule schema rejects days outside 1-7."""
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_ADD_SCHEDULE_SCHEMA({"days": [0], "times": [0], "events": [1]})
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_ADD_SCHEDULE_SCHEMA({"days": [8], "times": [0], "events": [1]})

    def test_add_schedule_times_out_of_range_raises(self):
        """Test add_schedule schema rejects times outside 0-86399."""
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_ADD_SCHEDULE_SCHEMA({"days": [1], "times": [86400], "events": [1]})

    def test_delete_schedules_valid(self):
        """Test delete_schedules schema accepts valid input."""
        result = SERVICE_DELETE_SCHEDULES_SCHEMA({"schedule_ids": [1, 2, 3]})
        assert result["schedule_ids"] == [1, 2, 3]

    def test_delete_schedules_missing_ids_raises(self):
        """Test delete_schedules schema rejects input without schedule_ids."""
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_DELETE_SCHEDULES_SCHEMA({})

    def test_delete_schedules_valid_with_device_id(self):
        """Test delete_schedules schema accepts input with device_id."""
        result = SERVICE_DELETE_SCHEDULES_SCHEMA(
            {"device_id": "abc123", "schedule_ids": [1]}
        )
        assert result["device_id"] == "abc123"
        assert result["schedule_ids"] == [1]

    def test_submit_developer_feedback_valid_empty(self):
        """Test submit_developer_feedback schema accepts empty input."""
        result = SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA({})
        assert isinstance(result, dict)

    def test_submit_developer_feedback_valid_with_note(self):
        """Test submit_developer_feedback schema accepts optional note."""
        result = SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA(
            {"note": "group command delayed in app"}
        )
        assert result["note"] == "group command delayed in app"

    def test_query_command_result_schema_validation(self):
        """Test query_command_result schema requires msg_sn."""
        result = SERVICE_QUERY_COMMAND_RESULT_SCHEMA({"msg_sn": "123"})
        assert result["msg_sn"] == "123"
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_QUERY_COMMAND_RESULT_SCHEMA({})

    def test_fetch_sensor_history_schema_validation(self):
        """Test fetch sensor history schema validates fields and defaults mesh_type."""
        result = SERVICE_FETCH_SENSOR_HISTORY_SCHEMA({"sensor_device_id": "03ab5ccd7caaaaaa"})
        assert result["sensor_device_id"] == "03ab5ccd7caaaaaa"
        assert result["mesh_type"] == "2"
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_FETCH_SENSOR_HISTORY_SCHEMA({})

    def test_summarize_service_properties_masks_values(self):
        """Service properties summary should expose keys/count, not raw values."""
        result = _summarize_service_properties(
            [
                {"key": "powerState", "value": "1"},
                {"key": "token", "value": "secret-token"},
                {"value": "ignored"},
                "invalid-item",
            ]
        )

        assert result == {"count": 4, "keys": ["powerState", "token"]}
        assert "secret-token" not in str(result)


class TestInitRuntimeBehavior:
    """Tests for __init__.py runtime behaviors."""

    @staticmethod
    def _create_device(serial: str = "03ab5ccd7c111111") -> LiproDevice:
        """Create a minimal LiproDevice for runtime tests."""
        return LiproDevice(
            device_number=1,
            serial=serial,
            name="Test Device",
            device_type=1,
            iot_name="lipro_led",
            physical_model="light",
        )

    async def test_async_setup_registers_services(self, hass) -> None:
        """Services are registered by async_setup and idempotent."""
        assert await async_setup(hass, {}) is True
        assert hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND)
        assert hass.services.has_service(DOMAIN, SERVICE_GET_SCHEDULES)
        assert hass.services.has_service(DOMAIN, SERVICE_ADD_SCHEDULE)
        assert hass.services.has_service(DOMAIN, SERVICE_DELETE_SCHEDULES)
        assert hass.services.has_service(DOMAIN, SERVICE_SUBMIT_ANONYMOUS_SHARE)
        assert hass.services.has_service(DOMAIN, SERVICE_GET_ANONYMOUS_SHARE_REPORT)
        assert hass.services.has_service(DOMAIN, SERVICE_GET_DEVELOPER_REPORT)
        assert hass.services.has_service(DOMAIN, SERVICE_SUBMIT_DEVELOPER_FEEDBACK)
        assert hass.services.has_service(DOMAIN, SERVICE_QUERY_COMMAND_RESULT)
        assert hass.services.has_service(DOMAIN, SERVICE_GET_CITY)
        assert hass.services.has_service(DOMAIN, SERVICE_FETCH_BODY_SENSOR_HISTORY)
        assert hass.services.has_service(DOMAIN, SERVICE_FETCH_DOOR_SENSOR_HISTORY)

        # Calling setup twice should keep registration stable.
        assert await async_setup(hass, {}) is True
        assert hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND)

    async def test_async_setup_entry_success_with_token_update(self, hass) -> None:
        """async_setup_entry builds coordinator and updates stored tokens when changed."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
                CONF_PASSWORD_HASH: "hashed-password",
                CONF_ACCESS_TOKEN: "old_access",
                CONF_REFRESH_TOKEN: "old_refresh",
            },
        )
        entry.add_to_hass(hass)
        entry.add_update_listener = MagicMock(return_value=MagicMock())
        entry.async_on_unload = MagicMock()

        mock_auth = MagicMock()
        mock_auth.set_tokens = MagicMock()
        mock_auth.set_credentials = MagicMock()
        mock_auth.ensure_valid_token = AsyncMock()
        mock_auth.get_auth_data.return_value = {
            CONF_ACCESS_TOKEN: "new_access",
            CONF_REFRESH_TOKEN: "new_refresh",
            CONF_EXPIRES_AT: 1234567890,
        }

        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch("custom_components.lipro.LiproClient", return_value=MagicMock()),
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            patch(
                "custom_components.lipro.LiproDataUpdateCoordinator",
                return_value=mock_coordinator,
            ),
            patch.object(
                hass.config_entries,
                "async_forward_entry_setups",
                AsyncMock(return_value=True),
            ) as mock_forward,
            patch.object(hass.config_entries, "async_update_entry") as mock_update,
        ):
            assert await async_setup_entry(hass, entry) is True

        mock_auth.set_tokens.assert_called_once()
        mock_auth.ensure_valid_token.assert_awaited_once()
        mock_coordinator.async_config_entry_first_refresh.assert_awaited_once()
        assert entry.runtime_data is mock_coordinator
        mock_forward.assert_awaited_once()
        mock_update.assert_called_once()
        entry.add_update_listener.assert_called_once()
        entry.async_on_unload.assert_called_once()

    async def test_async_setup_entry_auth_error_raises_config_entry_auth_failed(
        self, hass
    ) -> None:
        """Auth failures are surfaced as ConfigEntryAuthFailed."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
                CONF_PASSWORD_HASH: "hashed-password",
            },
        )
        entry.add_to_hass(hass)

        mock_auth = MagicMock()
        mock_auth.set_credentials = MagicMock()
        mock_auth.ensure_valid_token = AsyncMock(side_effect=LiproAuthError("bad auth"))

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch("custom_components.lipro.LiproClient", return_value=MagicMock()),
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            pytest.raises(ConfigEntryAuthFailed),
        ):
            await async_setup_entry(hass, entry)

    async def test_async_setup_entry_coerces_invalid_persisted_options(
        self, hass
    ) -> None:
        """Persisted non-schema options should be coerced/clamped safely."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
                CONF_PASSWORD_HASH: "hashed-password",
                CONF_ACCESS_TOKEN: "access",
                CONF_REFRESH_TOKEN: "refresh",
            },
            options={
                CONF_REQUEST_TIMEOUT: "not-an-int",
                CONF_SCAN_INTERVAL: 999999,
            },
        )
        entry.add_to_hass(hass)
        entry.add_update_listener = MagicMock(return_value=MagicMock())
        entry.async_on_unload = MagicMock()

        mock_auth = MagicMock()
        mock_auth.set_tokens = MagicMock()
        mock_auth.set_credentials = MagicMock()
        mock_auth.ensure_valid_token = AsyncMock()
        mock_auth.get_auth_data.return_value = {
            CONF_ACCESS_TOKEN: "access",
            CONF_REFRESH_TOKEN: "refresh",
            CONF_EXPIRES_AT: 1234567890,
        }

        mock_client = MagicMock()
        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.LiproClient", return_value=mock_client
            ) as pc,
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            patch(
                "custom_components.lipro.LiproDataUpdateCoordinator",
                return_value=mock_coordinator,
            ) as pcoord,
            patch.object(
                hass.config_entries,
                "async_forward_entry_setups",
                AsyncMock(return_value=True),
            ),
            patch.object(hass.config_entries, "async_update_entry"),
        ):
            assert await async_setup_entry(hass, entry) is True

        assert pc.call_args.kwargs["request_timeout"] == DEFAULT_REQUEST_TIMEOUT
        assert pcoord.call_args.kwargs["update_interval"] == MAX_SCAN_INTERVAL

    async def test_async_setup_entry_connection_error_raises_not_ready(
        self, hass
    ) -> None:
        """Connection failures are surfaced as ConfigEntryNotReady."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
                CONF_PASSWORD_HASH: "hashed-password",
            },
        )
        entry.add_to_hass(hass)

        mock_auth = MagicMock()
        mock_auth.set_credentials = MagicMock()
        mock_auth.ensure_valid_token = AsyncMock(
            side_effect=LiproConnectionError("offline")
        )

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch("custom_components.lipro.LiproClient", return_value=MagicMock()),
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            pytest.raises(ConfigEntryNotReady),
        ):
            await async_setup_entry(hass, entry)

    async def test_async_unload_entry_removes_services_on_last_entry(
        self, hass
    ) -> None:
        """Service registrations are removed when last entry unloads."""
        await async_setup(hass, {})
        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)

        with patch.object(
            hass.config_entries,
            "async_unload_platforms",
            AsyncMock(return_value=True),
        ):
            assert await async_unload_entry(hass, entry) is True

        assert not hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_SCHEDULES)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_DEVELOPER_REPORT)
        assert not hass.services.has_service(DOMAIN, SERVICE_SUBMIT_DEVELOPER_FEEDBACK)
        assert not hass.services.has_service(DOMAIN, SERVICE_QUERY_COMMAND_RESULT)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_CITY)

    async def test_async_unload_entry_shuts_down_runtime_data_coordinator(
        self, hass
    ) -> None:
        """Coordinator runtime data should be shut down on successful unload."""
        await async_setup(hass, {})
        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)

        coordinator = MagicMock()
        coordinator.async_shutdown = AsyncMock()
        entry.runtime_data = coordinator

        with patch.object(
            hass.config_entries,
            "async_unload_platforms",
            AsyncMock(return_value=True),
        ):
            assert await async_unload_entry(hass, entry) is True

        coordinator.async_shutdown.assert_awaited_once()

    async def test_async_unload_entry_does_not_shutdown_on_failed_unload(
        self, hass
    ) -> None:
        """Coordinator shutdown should not run when platform unload fails."""
        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)

        coordinator = MagicMock()
        coordinator.async_shutdown = AsyncMock()
        entry.runtime_data = coordinator

        with patch.object(
            hass.config_entries,
            "async_unload_platforms",
            AsyncMock(return_value=False),
        ):
            assert await async_unload_entry(hass, entry) is False

        coordinator.async_shutdown.assert_not_awaited()

    async def test_get_device_from_entity_target(self, hass) -> None:
        """Resolve target entity unique_id to device serial."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_id = (
            er.async_get(hass)
            .async_get_or_create(
                "light",
                DOMAIN,
                f"lipro_{device.serial}_light",
                suggested_object_id="lipro_test_device",
            )
            .entity_id
        )

        call = SimpleNamespace(data={ATTR_ENTITY_ID: [entity_id]})
        got_device, got_coordinator = await _get_device_and_coordinator(hass, call)

        assert got_device is device
        assert got_coordinator is coordinator

    async def test_get_device_falls_back_to_get_device_by_id(self, hass) -> None:
        """Fallback to coordinator alias lookup when serial lookup misses."""
        device = self._create_device(serial="mesh_group_10001")
        coordinator = MagicMock()
        coordinator.get_device.return_value = None
        coordinator.get_device_by_id.return_value = device

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        call = SimpleNamespace(data={ATTR_DEVICE_ID: "03AB5CCD7C716177"})
        got_device, got_coordinator = await _get_device_and_coordinator(hass, call)

        assert got_device is device
        assert got_coordinator is coordinator
        coordinator.get_device.assert_called_once_with("03AB5CCD7C716177")
        coordinator.get_device_by_id.assert_called_once_with("03AB5CCD7C716177")

    async def test_get_device_without_id_or_entity_raises(self, hass) -> None:
        """Missing device_id and entity target should raise validation error."""
        with pytest.raises(ServiceValidationError):
            await _get_device_and_coordinator(hass, SimpleNamespace(data={}))

    async def test_add_schedule_times_events_mismatch_raises(self, hass) -> None:
        """Mismatched lengths in add_schedule should fail validation."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        call = SimpleNamespace(
            data={
                ATTR_DEVICE_ID: device.serial,
                ATTR_DAYS: [1, 2],
                ATTR_TIMES: [3600],
                ATTR_EVENTS: [1, 0],
            }
        )

        with pytest.raises(ServiceValidationError):
            await _async_handle_add_schedule(hass, call)

    async def test_submit_anonymous_share_disabled_raises(self, hass) -> None:
        """submit_anonymous_share validates opt-in flag."""
        share_manager = MagicMock()
        share_manager.is_enabled = False

        with (
            patch(
                "custom_components.lipro.get_anonymous_share_manager",
                return_value=share_manager,
            ),
            pytest.raises(ServiceValidationError),
        ):
            await _async_handle_submit_anonymous_share(hass, SimpleNamespace(data={}))

    async def test_get_anonymous_share_report_returns_data(self, hass) -> None:
        """get_anonymous_share_report exposes pending report summary."""
        report = {
            "device_count": 1,
            "error_count": 2,
            "devices": ["a"],
            "errors": ["b"],
        }
        share_manager = MagicMock()
        share_manager.get_pending_report.return_value = report

        with patch(
            "custom_components.lipro.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            result = await _async_handle_get_anonymous_share_report(
                hass, SimpleNamespace(data={})
            )

        assert result == {
            "has_data": True,
            "device_count": 1,
            "error_count": 2,
            "devices": ["a"],
            "errors": ["b"],
        }

    async def test_get_developer_report_returns_entry_reports(self, hass) -> None:
        """get_developer_report returns sanitized diagnostics per config entry."""
        coordinator = MagicMock()
        coordinator.build_developer_report.return_value = {"debug_mode": True}

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_get_developer_report(
            hass, SimpleNamespace(data={})
        )

        assert result == {
            "entry_count": 1,
            "reports": [{"debug_mode": True}],
        }
        coordinator.build_developer_report.assert_called_once()

    async def test_query_command_result_service(self, hass) -> None:
        """query_command_result service should call client with device context."""
        device = self._create_device(serial="mesh_group_49155")
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.client.query_command_result = AsyncMock(return_value={"success": True})

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_query_command_result(
            hass,
            SimpleNamespace(data={ATTR_DEVICE_ID: device.serial, ATTR_MSG_SN: "682550445474"}),
        )

        assert result["serial"] == "mesh_group_49155"
        assert result["msg_sn"] == "682550445474"
        assert result["result"] == {"success": True}
        coordinator.client.query_command_result.assert_awaited_once_with(
            msg_sn="682550445474",
            device_id="mesh_group_49155",
            device_type=device.device_type,
        )

    async def test_get_city_service(self, hass) -> None:
        """get_city service should return first coordinator city result."""
        coordinator = MagicMock()
        coordinator.client.get_city = AsyncMock(
            return_value={"province": "广东省", "city": "江门市"}
        )

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_get_city(hass, SimpleNamespace(data={}))
        assert result == {"result": {"province": "广东省", "city": "江门市"}}

    async def test_fetch_body_sensor_history_service(self, hass) -> None:
        """fetch_body_sensor_history should pass sensor payload to client."""
        device = self._create_device(serial="mesh_group_49155")
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.client.fetch_body_sensor_history = AsyncMock(
            return_value={"humanSensorStateList": []}
        )

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_fetch_body_sensor_history(
            hass,
            SimpleNamespace(
                data={
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_SENSOR_DEVICE_ID: "03ab5ccd7c7167d8",
                    ATTR_MESH_TYPE: "2",
                }
            ),
        )

        assert result["serial"] == "mesh_group_49155"
        coordinator.client.fetch_body_sensor_history.assert_awaited_once_with(
            device_id="mesh_group_49155",
            device_type=device.device_type,
            sensor_device_id="03ab5ccd7c7167d8",
            mesh_type="2",
        )

    async def test_fetch_door_sensor_history_service(self, hass) -> None:
        """fetch_door_sensor_history should pass sensor payload to client."""
        device = self._create_device(serial="mesh_group_49155")
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.client.fetch_door_sensor_history = AsyncMock(
            return_value={"doorStateList": []}
        )

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_fetch_door_sensor_history(
            hass,
            SimpleNamespace(
                data={
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_SENSOR_DEVICE_ID: "03ab5ccd7c7167d8",
                    ATTR_MESH_TYPE: "2",
                }
            ),
        )

        assert result["serial"] == "mesh_group_49155"
        coordinator.client.fetch_door_sensor_history.assert_awaited_once_with(
            device_id="mesh_group_49155",
            device_type=device.device_type,
            sensor_device_id="03ab5ccd7c7167d8",
            mesh_type="2",
        )

    async def test_submit_developer_feedback_success(self, hass) -> None:
        """submit_developer_feedback uploads report to share worker."""
        coordinator = MagicMock()
        coordinator.build_developer_report.return_value = {"runtime": {"ok": True}}

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        share_manager = MagicMock()
        share_manager.submit_developer_feedback = AsyncMock(return_value=True)

        with (
            patch(
                "custom_components.lipro.get_anonymous_share_manager",
                return_value=share_manager,
            ),
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
        ):
            result = await _async_handle_submit_developer_feedback(
                hass, SimpleNamespace(data={"note": "manual validation run"})
            )

        assert result["success"] is True
        assert result["submitted_entries"] == 1
        share_manager.submit_developer_feedback.assert_awaited_once()

    async def test_submit_developer_feedback_failure_raises(self, hass) -> None:
        """submit_developer_feedback raises when upload fails."""
        coordinator = MagicMock()
        coordinator.build_developer_report.return_value = {"runtime": {"ok": True}}

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        share_manager = MagicMock()
        share_manager.submit_developer_feedback = AsyncMock(return_value=False)

        with (
            patch(
                "custom_components.lipro.get_anonymous_share_manager",
                return_value=share_manager,
            ),
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            pytest.raises(HomeAssistantError),
        ):
            await _async_handle_submit_developer_feedback(
                hass, SimpleNamespace(data={})
            )

    async def test_send_command_handler_success(self, hass) -> None:
        """send_command returns success payload on coordinator success."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.async_send_command = AsyncMock(return_value=True)

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_send_command(
            hass,
            SimpleNamespace(
                data={
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_COMMAND: "POWER_ON",
                    ATTR_PROPERTIES: [{"key": "powerState", "value": "1"}],
                }
            ),
        )
        assert result == {"success": True, "serial": device.serial}
        coordinator.async_send_command.assert_awaited_once_with(
            device,
            "POWER_ON",
            [{"key": "powerState", "value": "1"}],
            fallback_device_id=device.serial,
        )

    async def test_send_command_handler_alias_resolution_metadata(self, hass) -> None:
        """send_command response includes alias-resolution metadata when remapped."""
        requested_id = "03ab0000000000f1"
        group_device = self._create_device(serial="mesh_group_10001")
        group_device.is_group = True

        coordinator = MagicMock()
        coordinator.get_device.return_value = None
        coordinator.get_device_by_id.return_value = group_device
        coordinator.async_send_command = AsyncMock(return_value=True)

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_send_command(
            hass,
            SimpleNamespace(
                data={
                    ATTR_DEVICE_ID: requested_id,
                    ATTR_COMMAND: "POWER_ON",
                }
            ),
        )

        assert result == {
            "success": True,
            "serial": "mesh_group_10001",
            "requested_device_id": requested_id,
            "resolved_device_id": "mesh_group_10001",
        }
        coordinator.get_device.assert_called_once_with(requested_id)
        coordinator.get_device_by_id.assert_called_once_with(requested_id)
        coordinator.async_send_command.assert_awaited_once_with(
            group_device,
            "POWER_ON",
            None,
            fallback_device_id=requested_id,
        )

    async def test_send_command_handler_failure_raises(self, hass) -> None:
        """send_command raises HomeAssistantError when coordinator reports failure."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.async_send_command = AsyncMock(return_value=False)
        coordinator.last_command_failure = None

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError):
            await _async_handle_send_command(
                hass,
                SimpleNamespace(
                    data={ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"}
                ),
            )

    async def test_send_command_handler_push_failed_maps_translation(self, hass) -> None:
        """pushSuccess=false style failures should use push_failed translation key."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.async_send_command = AsyncMock(return_value=False)
        coordinator.last_command_failure = {"reason": "push_failed", "code": "push_failed"}

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await _async_handle_send_command(
                hass,
                SimpleNamespace(
                    data={ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"}
                ),
            )
        assert exc.value.translation_key == "command_push_failed"

    async def test_send_command_handler_offline_code_maps_translation(self, hass) -> None:
        """140004 failures should use device-not-connected translation key."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.async_send_command = AsyncMock(return_value=False)
        coordinator.last_command_failure = {"reason": "api_error", "code": "140004"}

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await _async_handle_send_command(
                hass,
                SimpleNamespace(
                    data={ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"}
                ),
            )
        assert exc.value.translation_key == "command_device_not_connected"

    async def test_send_command_handler_busy_code_maps_translation(self, hass) -> None:
        """250001 failures should use device-busy translation key."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.async_send_command = AsyncMock(return_value=False)
        coordinator.last_command_failure = {"reason": "api_error", "code": "250001"}

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await _async_handle_send_command(
                hass,
                SimpleNamespace(
                    data={ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"}
                ),
            )
        assert exc.value.translation_key == "command_device_busy"

    async def test_send_command_handler_api_error_raises(self, hass) -> None:
        """send_command maps API errors to HomeAssistantError."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.async_send_command = AsyncMock(side_effect=LiproApiError("boom"))

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError):
            await _async_handle_send_command(
                hass,
                SimpleNamespace(
                    data={ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"}
                ),
            )

    async def test_send_command_handler_api_error_code_maps_translation(self, hass) -> None:
        """API error 140003 should map to device-offline translation key."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.async_send_command = AsyncMock(
            side_effect=LiproApiError("offline", "140003")
        )

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await _async_handle_send_command(
                hass,
                SimpleNamespace(
                    data={ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"}
                ),
            )
        assert exc.value.translation_key == "command_device_offline"

    async def test_send_command_handler_api_busy_error_maps_translation(
        self, hass
    ) -> None:
        """API error 250001 should map to device-busy translation key."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.async_send_command = AsyncMock(
            side_effect=LiproApiError("busy", "250001")
        )

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await _async_handle_send_command(
                hass,
                SimpleNamespace(
                    data={ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"}
                ),
            )
        assert exc.value.translation_key == "command_device_busy"

    async def test_send_command_handler_not_found_code_maps_offline_translation(
        self, hass
    ) -> None:
        """API error 140013 should map to device-offline translation key."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.async_send_command = AsyncMock(
            side_effect=LiproApiError("not found", "140013")
        )

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await _async_handle_send_command(
                hass,
                SimpleNamespace(
                    data={ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"}
                ),
            )
        assert exc.value.translation_key == "command_device_offline"

    async def test_get_schedules_formats_response(self, hass) -> None:
        """get_schedules returns normalized response payload."""
        device = self._create_device()
        client = MagicMock()
        client.get_device_schedules = AsyncMock(
            return_value=[
                {
                    "id": 5,
                    "active": True,
                    "schedule": {"days": [1], "time": [3600, 3661], "evt": [1, 0]},
                }
            ]
        )
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.client = client

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_get_schedules(
            hass, SimpleNamespace(data={ATTR_DEVICE_ID: device.serial})
        )

        assert result == {
            "serial": device.serial,
            "schedules": [
                {
                    "id": 5,
                    "active": True,
                    "days": [1],
                    "times": ["01:00", "01:01"],
                    "events": [1, 0],
                }
            ],
        }

    async def test_get_schedules_resolves_device_from_entity_target(self, hass) -> None:
        """get_schedules should resolve target entity when device_id is omitted."""
        device = self._create_device()
        client = MagicMock()
        client.get_device_schedules = AsyncMock(return_value=[])
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.client = client

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_id = (
            er.async_get(hass)
            .async_get_or_create(
                "light",
                DOMAIN,
                f"lipro_{device.serial}_light",
                suggested_object_id="lipro_test_device",
            )
            .entity_id
        )

        result = await _async_handle_get_schedules(
            hass, SimpleNamespace(data={ATTR_ENTITY_ID: entity_id})
        )

        assert result == {"serial": device.serial, "schedules": []}
        coordinator.get_device.assert_called_once_with(device.serial)
        client.get_device_schedules.assert_awaited_once_with(
            device.iot_device_id,
            device.device_type_hex,
            mesh_gateway_id="",
            mesh_member_ids=[],
        )

    async def test_get_schedules_ignores_malformed_schedule_rows(self, hass) -> None:
        """Malformed schedule rows should be ignored instead of raising."""
        device = self._create_device()
        client = MagicMock()
        client.get_device_schedules = AsyncMock(
            return_value=[
                "invalid-row",
                {
                    "id": 9,
                    "active": True,
                    "schedule": {
                        "days": ["1", "x"],
                        "time": [3600, -1, 90000, "bad"],
                        "evt": [1, "0", "bad"],
                    },
                },
            ]
        )
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.client = client

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_get_schedules(
            hass, SimpleNamespace(data={ATTR_DEVICE_ID: device.serial})
        )

        assert result == {
            "serial": device.serial,
            "schedules": [
                {
                    "id": 9,
                    "active": True,
                    "days": [1],
                    "times": ["01:00"],
                    "events": [1, 0],
                }
            ],
        }

    async def test_get_schedules_passes_mesh_context(self, hass) -> None:
        """get_schedules should pass mesh gateway/member context to client."""
        device = self._create_device(serial="mesh_group_10001")
        device.extra_data["gateway_device_id"] = "03ab0000000000a1"
        device.extra_data["group_member_ids"] = ["03ab0000000000a2"]

        client = MagicMock()
        client.get_device_schedules = AsyncMock(return_value=[])
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.client = client

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        await _async_handle_get_schedules(
            hass, SimpleNamespace(data={ATTR_DEVICE_ID: device.serial})
        )

        client.get_device_schedules.assert_awaited_once_with(
            device.iot_device_id,
            device.device_type_hex,
            mesh_gateway_id="03ab0000000000a1",
            mesh_member_ids=["03ab0000000000a2"],
        )

    async def test_add_schedule_passes_mesh_context(self, hass) -> None:
        """add_schedule should pass mesh gateway/member context to client."""
        device = self._create_device(serial="mesh_group_10001")
        device.extra_data["gateway_device_id"] = "03ab0000000000a1"
        device.extra_data["group_member_ids"] = ["03ab0000000000a2"]

        client = MagicMock()
        client.add_device_schedule = AsyncMock(return_value=[{"id": 1}])
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.client = client

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_add_schedule(
            hass,
            SimpleNamespace(
                data={
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_DAYS: [1, 2, 3],
                    ATTR_TIMES: [3600],
                    ATTR_EVENTS: [0],
                }
            ),
        )

        assert result["schedule_count"] == 1
        client.add_device_schedule.assert_awaited_once_with(
            device.iot_device_id,
            device.device_type_hex,
            [1, 2, 3],
            [3600],
            [0],
            mesh_gateway_id="03ab0000000000a1",
            mesh_member_ids=["03ab0000000000a2"],
        )

    async def test_add_schedule_resolves_device_from_entity_target(self, hass) -> None:
        """add_schedule should resolve target entity when device_id is omitted."""
        device = self._create_device()
        client = MagicMock()
        client.add_device_schedule = AsyncMock(return_value=[{"id": 1}])
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.client = client

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_id = (
            er.async_get(hass)
            .async_get_or_create(
                "light",
                DOMAIN,
                f"lipro_{device.serial}_light",
                suggested_object_id="lipro_test_device",
            )
            .entity_id
        )

        result = await _async_handle_add_schedule(
            hass,
            SimpleNamespace(
                data={
                    ATTR_ENTITY_ID: [entity_id],
                    ATTR_DAYS: [1],
                    ATTR_TIMES: [3600],
                    ATTR_EVENTS: [1],
                }
            ),
        )

        assert result == {
            "success": True,
            "serial": device.serial,
            "schedule_count": 1,
        }
        coordinator.get_device.assert_called_once_with(device.serial)
        client.add_device_schedule.assert_awaited_once_with(
            device.iot_device_id,
            device.device_type_hex,
            [1],
            [3600],
            [1],
            mesh_gateway_id="",
            mesh_member_ids=[],
        )

    async def test_delete_schedules_returns_summary(self, hass) -> None:
        """delete_schedules returns remaining count on success."""
        device = self._create_device()
        client = MagicMock()
        client.delete_device_schedules = AsyncMock(return_value=[{"id": 2}, {"id": 3}])
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.client = client

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_delete_schedules(
            hass,
            SimpleNamespace(
                data={ATTR_DEVICE_ID: device.serial, ATTR_SCHEDULE_IDS: [1]}
            ),
        )
        assert result == {
            "success": True,
            "serial": device.serial,
            "remaining_count": 2,
        }

    async def test_delete_schedules_passes_mesh_context(self, hass) -> None:
        """delete_schedules should pass mesh gateway/member context to client."""
        device = self._create_device(serial="mesh_group_10001")
        device.extra_data["gateway_device_id"] = "03ab0000000000a1"
        device.extra_data["group_member_ids"] = ["03ab0000000000a2"]

        client = MagicMock()
        client.delete_device_schedules = AsyncMock(return_value=[])
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.client = client

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        await _async_handle_delete_schedules(
            hass,
            SimpleNamespace(
                data={ATTR_DEVICE_ID: device.serial, ATTR_SCHEDULE_IDS: [1, 2]}
            ),
        )

        client.delete_device_schedules.assert_awaited_once_with(
            device.iot_device_id,
            device.device_type_hex,
            [1, 2],
            mesh_gateway_id="03ab0000000000a1",
            mesh_member_ids=["03ab0000000000a2"],
        )

    async def test_delete_schedules_resolves_device_from_entity_target(
        self, hass
    ) -> None:
        """delete_schedules should resolve target entity when device_id is omitted."""
        device = self._create_device()
        client = MagicMock()
        client.delete_device_schedules = AsyncMock(return_value=[])
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.client = client

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_id = (
            er.async_get(hass)
            .async_get_or_create(
                "light",
                DOMAIN,
                f"lipro_{device.serial}_light",
                suggested_object_id="lipro_test_device",
            )
            .entity_id
        )

        result = await _async_handle_delete_schedules(
            hass,
            SimpleNamespace(
                data={ATTR_ENTITY_ID: entity_id, ATTR_SCHEDULE_IDS: [1, 2]}
            ),
        )

        assert result == {
            "success": True,
            "serial": device.serial,
            "remaining_count": 0,
        }
        coordinator.get_device.assert_called_once_with(device.serial)
        client.delete_device_schedules.assert_awaited_once_with(
            device.iot_device_id,
            device.device_type_hex,
            [1, 2],
            mesh_gateway_id="",
            mesh_member_ids=[],
        )

    async def test_submit_anonymous_share_no_data_returns_noop(self, hass) -> None:
        """submit_anonymous_share returns no-op when nothing pending."""
        share_manager = MagicMock()
        share_manager.is_enabled = True
        share_manager.pending_count = (0, 0)

        with patch(
            "custom_components.lipro.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            result = await _async_handle_submit_anonymous_share(
                hass, SimpleNamespace(data={})
            )

        assert result == {
            "success": True,
            "message": "No data to submit",
            "devices": 0,
            "errors": 0,
        }

    async def test_submit_anonymous_share_submit_failed_raises(self, hass) -> None:
        """submit_anonymous_share raises when upload fails."""
        share_manager = MagicMock()
        share_manager.is_enabled = True
        share_manager.pending_count = (1, 1)
        share_manager.submit_report = AsyncMock(return_value=False)

        with (
            patch(
                "custom_components.lipro.get_anonymous_share_manager",
                return_value=share_manager,
            ),
            pytest.raises(HomeAssistantError),
        ):
            await _async_handle_submit_anonymous_share(hass, SimpleNamespace(data={}))

    async def test_get_anonymous_share_report_returns_empty(self, hass) -> None:
        """get_anonymous_share_report returns empty payload when no report."""
        share_manager = MagicMock()
        share_manager.get_pending_report.return_value = None

        with patch(
            "custom_components.lipro.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            result = await _async_handle_get_anonymous_share_report(
                hass, SimpleNamespace(data={})
            )

        assert result == {"has_data": False, "devices": [], "errors": []}
