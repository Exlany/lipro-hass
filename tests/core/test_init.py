"""Tests for Lipro integration __init__.py module.

Tests cover:
- PLATFORMS list completeness
- Service schema structure (keys, required/optional)
- Service constants definitions
- Attribute constants definitions
"""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
import voluptuous as vol

from custom_components.lipro import (
    PLATFORMS,
    async_reload_entry,
    async_setup,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import (
    CONF_ACCESS_TOKEN,
    CONF_EXPIRES_AT,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REFRESH_TOKEN,
    CONF_REQUEST_TIMEOUT,
    CONF_SCAN_INTERVAL,
    DEFAULT_REQUEST_TIMEOUT,
    MAX_SCAN_INTERVAL,
)
from custom_components.lipro.core import (
    LiproApiError,
    LiproAuthError,
    LiproAuthManager,
    LiproClient,
    LiproConnectionError,
)
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.entry_auth import (
    build_entry_auth_context,
    persist_entry_tokens_if_changed,
)
from custom_components.lipro.runtime_infra import (
    async_ensure_runtime_infra,
    remove_device_registry_listener,
    setup_device_registry_listener,
)
from custom_components.lipro.services.contracts import (
    ATTR_COMMAND,
    ATTR_DAYS,
    ATTR_DEVICE_ID,
    ATTR_ENTRY_ID,
    ATTR_EVENTS,
    ATTR_MAX_ATTEMPTS,
    ATTR_MESH_TYPE,
    ATTR_MSG_SN,
    ATTR_NOTE,
    ATTR_PROPERTIES,
    ATTR_SCHEDULE_IDS,
    ATTR_SENSOR_DEVICE_ID,
    ATTR_TIME_BUDGET_SECONDS,
    ATTR_TIMES,
    SERVICE_ADD_SCHEDULE,
    SERVICE_ADD_SCHEDULE_SCHEMA,
    SERVICE_DELETE_SCHEDULES,
    SERVICE_DELETE_SCHEDULES_SCHEMA,
    SERVICE_FETCH_BODY_SENSOR_HISTORY,
    SERVICE_FETCH_DOOR_SENSOR_HISTORY,
    SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
    SERVICE_GET_ANONYMOUS_SHARE_REPORT,
    SERVICE_GET_ANONYMOUS_SHARE_REPORT_SCHEMA,
    SERVICE_GET_CITY,
    SERVICE_GET_DEVELOPER_REPORT,
    SERVICE_GET_DEVELOPER_REPORT_SCHEMA,
    SERVICE_GET_SCHEDULES,
    SERVICE_GET_SCHEDULES_SCHEMA,
    SERVICE_QUERY_COMMAND_RESULT,
    SERVICE_QUERY_COMMAND_RESULT_SCHEMA,
    SERVICE_QUERY_USER_CLOUD,
    SERVICE_REFRESH_DEVICES,
    SERVICE_REFRESH_DEVICES_SCHEMA,
    SERVICE_SEND_COMMAND,
    SERVICE_SEND_COMMAND_SCHEMA,
    SERVICE_SUBMIT_ANONYMOUS_SHARE,
    SERVICE_SUBMIT_ANONYMOUS_SHARE_SCHEMA,
    SERVICE_SUBMIT_DEVELOPER_FEEDBACK,
    SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA,
)
from custom_components.lipro.services.wiring import (
    _async_handle_add_schedule,
    _async_handle_delete_schedules,
    _async_handle_fetch_body_sensor_history,
    _async_handle_fetch_door_sensor_history,
    _async_handle_get_anonymous_share_report,
    _async_handle_get_city,
    _async_handle_get_developer_report,
    _async_handle_get_schedules,
    _async_handle_query_command_result,
    _async_handle_query_user_cloud,
    _async_handle_refresh_devices,
    _async_handle_send_command,
    _async_handle_submit_anonymous_share,
    _async_handle_submit_developer_feedback,
    _get_device_and_coordinator,
    _summarize_service_properties,
)
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    HomeAssistantError,
    ServiceValidationError,
)
from homeassistant.helpers import device_registry as dr, entity_registry as er
from tests.helpers.service_call import service_call

_TEST_LOGGER = logging.getLogger(__name__)


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

    def test_service_query_user_cloud(self):
        """Test SERVICE_QUERY_USER_CLOUD is defined correctly."""
        assert SERVICE_QUERY_USER_CLOUD == "query_user_cloud"

    def test_service_fetch_body_sensor_history(self):
        """Test SERVICE_FETCH_BODY_SENSOR_HISTORY is defined correctly."""
        assert SERVICE_FETCH_BODY_SENSOR_HISTORY == "fetch_body_sensor_history"

    def test_service_fetch_door_sensor_history(self):
        """Test SERVICE_FETCH_DOOR_SENSOR_HISTORY is defined correctly."""
        assert SERVICE_FETCH_DOOR_SENSOR_HISTORY == "fetch_door_sensor_history"

    def test_service_refresh_devices(self):
        """Test SERVICE_REFRESH_DEVICES is defined correctly."""
        assert SERVICE_REFRESH_DEVICES == "refresh_devices"

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
        assert isinstance(SERVICE_QUERY_USER_CLOUD, str)
        assert isinstance(SERVICE_FETCH_BODY_SENSOR_HISTORY, str)
        assert isinstance(SERVICE_FETCH_DOOR_SENSOR_HISTORY, str)
        assert isinstance(SERVICE_REFRESH_DEVICES, str)


class TestAttributeConstants:
    """Tests for attribute constant definitions."""

    def test_attr_device_id(self):
        """Test ATTR_DEVICE_ID value."""
        assert ATTR_DEVICE_ID == "device_id"

    def test_attr_entry_id(self):
        """Test ATTR_ENTRY_ID value."""
        assert ATTR_ENTRY_ID == "entry_id"

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
        assert isinstance(ATTR_ENTRY_ID, str)
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

    def test_submit_anonymous_share_schema_keys(self):
        """Test submit_anonymous_share schema has expected keys."""
        keys = self._get_schema_keys(SERVICE_SUBMIT_ANONYMOUS_SHARE_SCHEMA)
        assert ATTR_ENTRY_ID in keys
        assert keys[ATTR_ENTRY_ID] is False

    def test_get_anonymous_share_report_schema_keys(self):
        """Test get_anonymous_share_report schema has expected keys."""
        keys = self._get_schema_keys(SERVICE_GET_ANONYMOUS_SHARE_REPORT_SCHEMA)
        assert ATTR_ENTRY_ID in keys
        assert keys[ATTR_ENTRY_ID] is False

    def test_get_developer_report_schema_keys(self):
        """Test get_developer_report schema has expected keys."""
        keys = self._get_schema_keys(SERVICE_GET_DEVELOPER_REPORT_SCHEMA)
        assert ATTR_ENTRY_ID in keys
        assert keys[ATTR_ENTRY_ID] is False

    def test_submit_developer_feedback_schema_keys(self):
        """Test submit_developer_feedback schema has expected keys."""
        keys = self._get_schema_keys(SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA)
        assert ATTR_ENTRY_ID in keys
        assert keys[ATTR_ENTRY_ID] is False
        assert ATTR_NOTE in keys
        assert keys[ATTR_NOTE] is False

    def test_query_command_result_schema_keys(self):
        """Test query_command_result schema has expected keys."""
        keys = self._get_schema_keys(SERVICE_QUERY_COMMAND_RESULT_SCHEMA)
        assert ATTR_DEVICE_ID in keys
        assert keys[ATTR_DEVICE_ID] is False
        assert ATTR_MSG_SN in keys
        assert keys[ATTR_MSG_SN] is True
        assert ATTR_MAX_ATTEMPTS in keys
        assert keys[ATTR_MAX_ATTEMPTS] is False
        assert ATTR_TIME_BUDGET_SECONDS in keys
        assert keys[ATTR_TIME_BUDGET_SECONDS] is False

    def test_fetch_sensor_history_schema_keys(self):
        """Test fetch sensor history schema has expected keys."""
        keys = self._get_schema_keys(SERVICE_FETCH_SENSOR_HISTORY_SCHEMA)
        assert ATTR_DEVICE_ID in keys
        assert keys[ATTR_DEVICE_ID] is False
        assert ATTR_SENSOR_DEVICE_ID in keys
        assert keys[ATTR_SENSOR_DEVICE_ID] is True
        assert ATTR_MESH_TYPE in keys
        assert keys[ATTR_MESH_TYPE] is False

    def test_refresh_devices_schema_is_vol_schema(self):
        """Test SERVICE_REFRESH_DEVICES_SCHEMA is a voluptuous Schema."""
        assert isinstance(SERVICE_REFRESH_DEVICES_SCHEMA, vol.Schema)

    def test_refresh_devices_schema_keys(self):
        """Test refresh_devices schema has expected keys."""
        keys = self._get_schema_keys(SERVICE_REFRESH_DEVICES_SCHEMA)
        assert ATTR_ENTRY_ID in keys
        assert keys[ATTR_ENTRY_ID] is False


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

    def test_submit_developer_feedback_valid_with_entry_id(self):
        """Test submit_developer_feedback schema accepts optional entry_id."""
        result = SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA(
            {"entry_id": "abc123_entry", "note": "group command delayed in app"}
        )
        assert result["entry_id"] == "abc123_entry"
        assert result["note"] == "group command delayed in app"

    def test_get_developer_report_schema_validation(self):
        """Test get_developer_report schema validates optional entry_id."""
        result = SERVICE_GET_DEVELOPER_REPORT_SCHEMA({})
        assert isinstance(result, dict)

        result = SERVICE_GET_DEVELOPER_REPORT_SCHEMA({"entry_id": "abc123_entry"})
        assert result["entry_id"] == "abc123_entry"

        with pytest.raises(vol.MultipleInvalid):
            SERVICE_GET_DEVELOPER_REPORT_SCHEMA({"entry_id": "bad.entry"})

    def test_query_command_result_schema_validation(self):
        """Test query_command_result schema requires msg_sn."""
        result = SERVICE_QUERY_COMMAND_RESULT_SCHEMA({"msg_sn": "123"})
        assert result["msg_sn"] == "123"
        assert result[ATTR_MAX_ATTEMPTS] == 6
        assert result[ATTR_TIME_BUDGET_SECONDS] == 3.0

        customized = SERVICE_QUERY_COMMAND_RESULT_SCHEMA(
            {
                "msg_sn": "123",
                ATTR_MAX_ATTEMPTS: 4,
                ATTR_TIME_BUDGET_SECONDS: 1.5,
            }
        )
        assert customized[ATTR_MAX_ATTEMPTS] == 4
        assert customized[ATTR_TIME_BUDGET_SECONDS] == 1.5

        with pytest.raises(vol.MultipleInvalid):
            SERVICE_QUERY_COMMAND_RESULT_SCHEMA({})
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_QUERY_COMMAND_RESULT_SCHEMA({"msg_sn": "bad.msg.sn"})

    def test_fetch_sensor_history_schema_validation(self):
        """Test fetch sensor history schema validates fields and defaults mesh_type."""
        result = SERVICE_FETCH_SENSOR_HISTORY_SCHEMA(
            {"sensor_device_id": "03ab5ccd7caaaaaa"}
        )
        assert result["sensor_device_id"] == "03ab5ccd7caaaaaa"
        assert result["mesh_type"] == "2"
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_FETCH_SENSOR_HISTORY_SCHEMA({})
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_FETCH_SENSOR_HISTORY_SCHEMA({"sensor_device_id": "invalid"})
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_FETCH_SENSOR_HISTORY_SCHEMA(
                {"sensor_device_id": "03ab5ccd7caaaaaa", "mesh_type": "3"}
            )

    def test_submit_anonymous_share_schema_validation(self):
        """Test submit_anonymous_share schema validates optional entry_id."""
        result = SERVICE_SUBMIT_ANONYMOUS_SHARE_SCHEMA({})
        assert isinstance(result, dict)

        result = SERVICE_SUBMIT_ANONYMOUS_SHARE_SCHEMA({"entry_id": "abc123_entry"})
        assert result["entry_id"] == "abc123_entry"

        with pytest.raises(vol.MultipleInvalid):
            SERVICE_SUBMIT_ANONYMOUS_SHARE_SCHEMA({"entry_id": "bad.entry"})

    def test_get_anonymous_share_report_schema_validation(self):
        """Test get_anonymous_share_report schema validates optional entry_id."""
        result = SERVICE_GET_ANONYMOUS_SHARE_REPORT_SCHEMA({})
        assert isinstance(result, dict)

        result = SERVICE_GET_ANONYMOUS_SHARE_REPORT_SCHEMA({"entry_id": "abc123_entry"})
        assert result["entry_id"] == "abc123_entry"

        with pytest.raises(vol.MultipleInvalid):
            SERVICE_GET_ANONYMOUS_SHARE_REPORT_SCHEMA({"entry_id": "bad.entry"})

    def test_refresh_devices_schema_validation(self):
        """Test refresh_devices schema validates optional entry_id."""
        result = SERVICE_REFRESH_DEVICES_SCHEMA({})
        assert isinstance(result, dict)

        result = SERVICE_REFRESH_DEVICES_SCHEMA({"entry_id": "abc123_entry"})
        assert result["entry_id"] == "abc123_entry"

        with pytest.raises(vol.MultipleInvalid):
            SERVICE_REFRESH_DEVICES_SCHEMA({"entry_id": ""})
        with pytest.raises(vol.MultipleInvalid):
            SERVICE_REFRESH_DEVICES_SCHEMA({"entry_id": "bad.entry"})

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
        assert hass.services.has_service(DOMAIN, SERVICE_QUERY_USER_CLOUD)
        assert hass.services.has_service(DOMAIN, SERVICE_FETCH_BODY_SENSOR_HISTORY)
        assert hass.services.has_service(DOMAIN, SERVICE_FETCH_DOOR_SENSOR_HISTORY)
        assert hass.services.has_service(DOMAIN, SERVICE_REFRESH_DEVICES)

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
                "custom_components.lipro.CoordinatorV2",
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

    def test_build_entry_auth_context_missing_phone_id_raises(self, hass) -> None:
        """Missing required keys in entry.data should raise ConfigEntryAuthFailed."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE: "13800000000",
            },
        )

        with pytest.raises(ConfigEntryAuthFailed):
            build_entry_auth_context(
                hass,
                entry,
                get_client_session=lambda _: MagicMock(),
                client_factory=LiproClient,
                auth_manager_factory=LiproAuthManager,
                logger=_TEST_LOGGER,
            )

    def test_build_entry_auth_context_missing_phone_raises(self, hass) -> None:
        """Missing phone in entry.data should raise ConfigEntryAuthFailed."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
            },
        )

        with pytest.raises(ConfigEntryAuthFailed):
            build_entry_auth_context(
                hass,
                entry,
                get_client_session=lambda _: MagicMock(),
                client_factory=LiproClient,
                auth_manager_factory=LiproAuthManager,
                logger=_TEST_LOGGER,
            )

    async def test_async_ensure_runtime_infra_handles_corrupt_domain_data(
        self,
        hass,
    ) -> None:
        """Shared infra should still be set up when hass.data[DOMAIN] is corrupted."""
        hass.data[DOMAIN] = "not-a-dict"

        mock_setup_services = AsyncMock()
        mock_setup_listener = MagicMock()

        await async_ensure_runtime_infra(
            hass,
            setup_services=mock_setup_services,
            setup_device_registry_listener=mock_setup_listener,
        )

        mock_setup_services.assert_awaited_once()
        mock_setup_listener.assert_called_once()

    def test_device_registry_listener_helpers_handle_corrupt_domain_data(
        self,
        hass,
    ) -> None:
        """Listener helpers should no-op when hass.data[DOMAIN] is corrupted."""
        hass.data[DOMAIN] = "not-a-dict"
        setup_device_registry_listener(hass, logger=_TEST_LOGGER)
        remove_device_registry_listener(hass)

    def test_persist_entry_tokens_skips_when_tokens_missing(self, hass) -> None:
        """Token persistence should not update entry when auth data is incomplete."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
            },
        )
        entry.add_to_hass(hass)

        mock_auth = MagicMock()
        mock_auth.get_auth_data.return_value = {}

        with patch.object(hass.config_entries, "async_update_entry") as mock_update:
            persist_entry_tokens_if_changed(hass, entry, mock_auth)

        mock_update.assert_not_called()

    async def test_async_setup_entry_forward_setup_failure_rolls_back_runtime_data(
        self, hass
    ) -> None:
        """Platform setup failure should shut down coordinator and clear runtime data."""
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
        mock_coordinator.async_shutdown = AsyncMock()

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch("custom_components.lipro.LiproClient", return_value=MagicMock()),
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            patch(
                "custom_components.lipro.CoordinatorV2",
                return_value=mock_coordinator,
            ),
            patch.object(
                hass.config_entries,
                "async_forward_entry_setups",
                AsyncMock(side_effect=RuntimeError("platform setup failed")),
            ),
            patch.object(hass.config_entries, "async_update_entry"),
            pytest.raises(RuntimeError, match="platform setup failed"),
        ):
            await async_setup_entry(hass, entry)

        mock_coordinator.async_shutdown.assert_awaited_once()
        assert getattr(entry, "runtime_data", None) is None
        entry.add_update_listener.assert_not_called()
        entry.async_on_unload.assert_not_called()

    async def test_async_setup_entry_first_refresh_failure_cleans_up(
        self,
        hass,
    ) -> None:
        """First refresh failure should shut down coordinator and avoid listener setup."""
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
            CONF_ACCESS_TOKEN: "old_access",
            CONF_REFRESH_TOKEN: "old_refresh",
            CONF_EXPIRES_AT: 1234567890,
        }

        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock(
            side_effect=RuntimeError("refresh failed")
        )
        mock_coordinator.async_shutdown = AsyncMock()

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch("custom_components.lipro.LiproClient", return_value=MagicMock()),
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            patch(
                "custom_components.lipro.CoordinatorV2",
                return_value=mock_coordinator,
            ),
            pytest.raises(RuntimeError, match="refresh failed"),
        ):
            await async_setup_entry(hass, entry)

        mock_coordinator.async_shutdown.assert_awaited_once()
        assert getattr(entry, "runtime_data", None) is None
        entry.add_update_listener.assert_not_called()
        entry.async_on_unload.assert_not_called()

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
                "custom_components.lipro.CoordinatorV2",
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
        assert not hass.services.has_service(DOMAIN, SERVICE_QUERY_USER_CLOUD)
        assert not hass.services.has_service(DOMAIN, SERVICE_REFRESH_DEVICES)

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
        assert getattr(entry, "runtime_data", None) is None

    async def test_async_unload_entry_logs_and_continues_on_shutdown_error(
        self,
        hass,
    ) -> None:
        """Unload should catch shutdown errors so unload can complete."""
        await async_setup(hass, {})
        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)

        coordinator = MagicMock()
        coordinator.async_shutdown = AsyncMock(side_effect=RuntimeError("boom"))
        entry.runtime_data = coordinator

        with (
            patch.object(
                hass.config_entries,
                "async_unload_platforms",
                AsyncMock(return_value=True),
            ),
            patch("custom_components.lipro._LOGGER.warning") as mock_warning,
        ):
            assert await async_unload_entry(hass, entry) is True

        mock_warning.assert_called()
        assert getattr(entry, "runtime_data", None) is None

    async def test_async_unload_entry_removes_services_when_lock_unavailable(
        self,
        hass,
    ) -> None:
        """Unload should remove shared infra when lock store is unavailable."""
        await async_setup(hass, {})
        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)

        hass.data[DOMAIN] = "not-a-dict"

        with (
            patch.object(
                hass.config_entries,
                "async_unload_platforms",
                AsyncMock(return_value=True),
            ),
            patch(
                "custom_components.lipro.has_other_runtime_entries", return_value=False
            ),
            patch("custom_components.lipro.remove_services") as mock_remove_services,
            patch(
                "custom_components.lipro.remove_device_registry_listener"
            ) as mock_remove_listener,
        ):
            assert await async_unload_entry(hass, entry) is True

        from custom_components.lipro.services.registrations import SERVICE_REGISTRATIONS

        mock_remove_services.assert_called_once_with(
            hass,
            domain=DOMAIN,
            registrations=SERVICE_REGISTRATIONS,
        )
        mock_remove_listener.assert_called_once_with(hass)

    async def test_async_reload_entry_forwards_to_hass(self, hass) -> None:
        """async_reload_entry should delegate to hass reload."""
        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)

        mock_reload = AsyncMock()
        with patch.object(hass.config_entries, "async_reload", mock_reload):
            await async_reload_entry(hass, entry)

        mock_reload.assert_awaited_once_with(entry.entry_id)

    async def test_async_unload_entry_removes_services_when_only_non_runtime_entries_remain(
        self, hass
    ) -> None:
        """Services should be removed when no other runtime-loaded entry remains."""
        await async_setup(hass, {})
        active_entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        active_entry.add_to_hass(hass)
        active_entry.runtime_data = MagicMock(async_shutdown=AsyncMock())

        # Simulate a configured but not loaded entry (no runtime_data).
        passive_entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13900000000"})
        passive_entry.add_to_hass(hass)

        with patch.object(
            hass.config_entries,
            "async_unload_platforms",
            AsyncMock(return_value=True),
        ):
            assert await async_unload_entry(hass, active_entry) is True

        assert not hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_SCHEDULES)
        assert getattr(passive_entry, "runtime_data", None) is None

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

    async def test_refresh_devices_handler_refreshes_all_loaded_entries(
        self, hass
    ) -> None:
        """refresh_devices should refresh all loaded entry coordinators by default."""
        first = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        first.add_to_hass(hass)
        first.runtime_data = MagicMock(async_refresh_devices=AsyncMock())

        second = MockConfigEntry(domain=DOMAIN, data={"phone": "13900000000"})
        second.add_to_hass(hass)
        second.runtime_data = MagicMock(async_refresh_devices=AsyncMock())

        result = await _async_handle_refresh_devices(hass, service_call(hass, {}))

        assert result["success"] is True
        assert result["refreshed_entries"] == 2
        assert "entry_ids" not in result
        first.runtime_data.async_refresh_devices.assert_awaited_once()
        second.runtime_data.async_refresh_devices.assert_awaited_once()

    async def test_refresh_devices_handler_filters_by_entry_id(self, hass) -> None:
        """refresh_devices should refresh only the selected config entry."""
        first = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        first.add_to_hass(hass)
        first.runtime_data = MagicMock(async_refresh_devices=AsyncMock())

        second = MockConfigEntry(domain=DOMAIN, data={"phone": "13900000000"})
        second.add_to_hass(hass)
        second.runtime_data = MagicMock(async_refresh_devices=AsyncMock())

        result = await _async_handle_refresh_devices(
            hass,
            service_call(hass, {ATTR_ENTRY_ID: second.entry_id}),
        )

        assert result["success"] is True
        assert result["refreshed_entries"] == 1
        assert result["requested_entry_id"] == second.entry_id
        first.runtime_data.async_refresh_devices.assert_not_awaited()
        second.runtime_data.async_refresh_devices.assert_awaited_once()

    async def test_refresh_devices_handler_unknown_entry_raises(self, hass) -> None:
        """refresh_devices should raise translated validation error for bad entry_id."""
        with pytest.raises(ServiceValidationError) as exc:
            await _async_handle_refresh_devices(
                hass,
                service_call(hass, {ATTR_ENTRY_ID: "missing_entry"}),
            )

        assert exc.value.translation_key == "entry_not_found"

    async def test_device_registry_disable_enable_triggers_entry_reload(
        self, hass
    ) -> None:
        """Lipro device disable/enable transitions should trigger config entry reload."""
        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = MagicMock()

        with patch.object(
            hass.config_entries,
            "async_reload",
            AsyncMock(return_value=True),
        ) as mock_reload:
            await async_setup(hass, {})

            device_registry = dr.async_get(hass)
            device_entry = device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={(DOMAIN, "03ab5ccd7c123456")},
                manufacturer="Lipro",
                name="Lipro Device",
            )

            device_registry.async_update_device(
                device_entry.id,
                disabled_by=dr.DeviceEntryDisabler.USER,
            )
            await hass.async_block_till_done()

            device_registry.async_update_device(
                device_entry.id,
                disabled_by=None,
            )
            await hass.async_block_till_done()

        assert mock_reload.await_count == 2
        assert mock_reload.await_args_list[0].args == (entry.entry_id,)
        assert mock_reload.await_args_list[1].args == (entry.entry_id,)

    async def test_device_registry_listener_ignores_non_lipro_device_updates(
        self, hass
    ) -> None:
        """Only Lipro devices with disabled_by changes should trigger reload."""
        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = MagicMock()

        with patch.object(
            hass.config_entries,
            "async_reload",
            AsyncMock(return_value=True),
        ) as mock_reload:
            await async_setup(hass, {})

            device_registry = dr.async_get(hass)
            non_lipro = device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={("other_domain", "dev-1")},
                manufacturer="Other",
                name="Other Device",
            )
            lipro = device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={(DOMAIN, "03ab5ccd7c999999")},
                manufacturer="Lipro",
                name="Lipro Device",
            )

            # Non-Lipro device: ignore even if disabled_by changed.
            device_registry.async_update_device(
                non_lipro.id,
                disabled_by=dr.DeviceEntryDisabler.USER,
            )
            # Lipro device, but unrelated update: ignore.
            device_registry.async_update_device(
                lipro.id,
                name="Renamed Lipro Device",
            )
            await hass.async_block_till_done()

        mock_reload.assert_not_awaited()

    async def test_async_unload_entry_removes_device_registry_listener(
        self, hass
    ) -> None:
        """Device registry updates should stop reloading after the last unload."""
        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = MagicMock(async_shutdown=AsyncMock())

        with patch.object(
            hass.config_entries,
            "async_reload",
            AsyncMock(return_value=True),
        ) as mock_reload:
            await async_setup(hass, {})

            device_registry = dr.async_get(hass)
            device_entry = device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={(DOMAIN, "03ab5ccd7c111111")},
                manufacturer="Lipro",
                name="Lipro Device",
            )

            with patch.object(
                hass.config_entries,
                "async_unload_platforms",
                AsyncMock(return_value=True),
            ):
                assert await async_unload_entry(hass, entry) is True

            device_registry.async_update_device(
                device_entry.id,
                disabled_by=dr.DeviceEntryDisabler.USER,
            )
            await hass.async_block_till_done()

        mock_reload.assert_not_awaited()

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

        call = service_call(hass, {ATTR_ENTITY_ID: [entity_id]})
        got_device, got_coordinator = await _get_device_and_coordinator(hass, call)

        assert got_device is device
        assert got_coordinator is coordinator

    async def test_get_device_from_target_entity_id(self, hass) -> None:
        """Resolve device via ServiceCall.target.entity_id."""
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
                suggested_object_id="lipro_target_test_device",
            )
            .entity_id
        )

        call = service_call(hass, {}, target_entity_ids=[entity_id])
        got_device, got_coordinator = await _get_device_and_coordinator(hass, call)

        assert got_device is device
        assert got_coordinator is coordinator

    async def test_get_device_from_multiple_entity_targets_same_device_resolves(
        self, hass
    ) -> None:
        """Multiple entities that map to one device should resolve successfully."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_registry = er.async_get(hass)
        entity_1 = entity_registry.async_get_or_create(
            "light",
            DOMAIN,
            f"lipro_{device.serial}_light",
            suggested_object_id="lipro_test_device_1",
        ).entity_id
        entity_2 = entity_registry.async_get_or_create(
            "switch",
            DOMAIN,
            f"lipro_{device.serial}_switch",
            suggested_object_id="lipro_test_device_2",
        ).entity_id

        got_device, got_coordinator = await _get_device_and_coordinator(
            hass,
            service_call(hass, {ATTR_ENTITY_ID: [entity_1, entity_2]}),
        )

        assert got_device is device
        assert got_coordinator is coordinator

    async def test_get_device_from_multiple_entity_targets_different_devices_raises(
        self, hass
    ) -> None:
        """Multiple entities from different devices should still be rejected."""
        first_device = self._create_device(serial="03ab5ccd7c123456")
        second_device = self._create_device(serial="03ab5ccd7c654321")
        coordinator = MagicMock()
        coordinator.get_device.side_effect = [first_device, second_device]

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_registry = er.async_get(hass)
        first_entity = entity_registry.async_get_or_create(
            "light",
            DOMAIN,
            f"lipro_{first_device.serial}_light",
            suggested_object_id="lipro_device_first",
        ).entity_id
        second_entity = entity_registry.async_get_or_create(
            "switch",
            DOMAIN,
            f"lipro_{second_device.serial}_switch",
            suggested_object_id="lipro_device_second",
        ).entity_id

        with pytest.raises(ServiceValidationError):
            await _get_device_and_coordinator(
                hass,
                service_call(hass, {ATTR_ENTITY_ID: [first_entity, second_entity]}),
            )

    async def test_get_device_falls_back_to_get_device_by_id(self, hass) -> None:
        """Fallback to coordinator alias lookup when serial lookup misses."""
        device = self._create_device(serial="mesh_group_10001")
        coordinator = MagicMock()
        coordinator.get_device.return_value = None
        coordinator.get_device_by_id.return_value = device

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        call = service_call(hass, {ATTR_DEVICE_ID: "03AB5CCD7C716177"})
        got_device, got_coordinator = await _get_device_and_coordinator(hass, call)

        assert got_device is device
        assert got_coordinator is coordinator
        coordinator.get_device.assert_called_once_with("03AB5CCD7C716177")
        coordinator.get_device_by_id.assert_called_once_with("03AB5CCD7C716177")

    async def test_get_device_without_id_or_entity_raises(self, hass) -> None:
        """Missing device_id and entity target should raise validation error."""
        with pytest.raises(ServiceValidationError):
            await _get_device_and_coordinator(hass, service_call(hass, {}))

    async def test_add_schedule_times_events_mismatch_raises(self, hass) -> None:
        """Mismatched lengths in add_schedule should fail validation."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        call = service_call(
            hass,
            {
                ATTR_DEVICE_ID: device.serial,
                ATTR_DAYS: [1, 2],
                ATTR_TIMES: [3600],
                ATTR_EVENTS: [1, 0],
            },
        )

        with pytest.raises(ServiceValidationError):
            await _async_handle_add_schedule(hass, call)

    async def test_submit_anonymous_share_disabled_raises(self, hass) -> None:
        """submit_anonymous_share validates opt-in flag."""
        share_manager = MagicMock()
        share_manager.is_enabled = False

        with (
            patch(
                "custom_components.lipro.services.wiring.get_anonymous_share_manager",
                return_value=share_manager,
            ),
            pytest.raises(ServiceValidationError),
        ):
            await _async_handle_submit_anonymous_share(hass, service_call(hass, {}))

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
            "custom_components.lipro.services.wiring.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            result = await _async_handle_get_anonymous_share_report(
                hass, service_call(hass, {})
            )

        assert result == {
            "has_data": True,
            "device_count": 1,
            "error_count": 2,
            "devices": ["a"],
            "errors": ["b"],
        }

    async def test_submit_anonymous_share_forwards_entry_id(self, hass) -> None:
        """submit_anonymous_share targets one scoped manager when entry_id is provided."""
        share_manager = MagicMock()
        share_manager.is_enabled = True
        share_manager.pending_count = (1, 0)
        share_manager.submit_report = AsyncMock(return_value=True)

        with patch(
            "custom_components.lipro.services.wiring.get_anonymous_share_manager",
            return_value=share_manager,
        ) as get_share_manager:
            result = await _async_handle_submit_anonymous_share(
                hass,
                service_call(hass, {ATTR_ENTRY_ID: "entry-2"}),
            )

        get_share_manager.assert_called_once_with(hass, entry_id="entry-2")
        assert result == {
            "success": True,
            "devices": 1,
            "errors": 0,
            "requested_entry_id": "entry-2",
        }

    async def test_get_anonymous_share_report_forwards_entry_id(self, hass) -> None:
        """get_anonymous_share_report targets one scoped manager when entry_id is provided."""
        share_manager = MagicMock()
        share_manager.get_pending_report.return_value = {
            "device_count": 1,
            "error_count": 0,
            "devices": ["a"],
            "errors": [],
        }

        with patch(
            "custom_components.lipro.services.wiring.get_anonymous_share_manager",
            return_value=share_manager,
        ) as get_share_manager:
            result = await _async_handle_get_anonymous_share_report(
                hass,
                service_call(hass, {ATTR_ENTRY_ID: "entry-3"}),
            )

        get_share_manager.assert_called_once_with(hass, entry_id="entry-3")
        assert result == {
            "has_data": True,
            "device_count": 1,
            "error_count": 0,
            "devices": ["a"],
            "errors": [],
            "requested_entry_id": "entry-3",
        }

    async def test_get_developer_report_returns_entry_reports(self, hass) -> None:
        """get_developer_report returns sanitized diagnostics per config entry."""
        coordinator = MagicMock()
        coordinator.build_developer_report.return_value = {"debug_mode": True}

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_get_developer_report(hass, service_call(hass, {}))

        assert result == {
            "entry_count": 1,
            "reports": [{"debug_mode": True}],
        }
        coordinator.build_developer_report.assert_called_once()

    async def test_get_developer_report_filters_by_entry_id(self, hass) -> None:
        """get_developer_report scopes diagnostics to one requested config entry."""
        first = MagicMock()
        first.build_developer_report.return_value = {"debug_mode": True}
        second = MagicMock()
        second.build_developer_report.return_value = {"debug_mode": False}

        entry_1 = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry_1.add_to_hass(hass)
        entry_1.runtime_data = first

        entry_2 = MockConfigEntry(domain=DOMAIN, data={"phone": "13900000000"})
        entry_2.add_to_hass(hass)
        entry_2.runtime_data = second

        result = await _async_handle_get_developer_report(
            hass,
            service_call(hass, {ATTR_ENTRY_ID: entry_2.entry_id}),
        )

        assert result == {
            "entry_count": 1,
            "reports": [{"debug_mode": False}],
            "requested_entry_id": entry_2.entry_id,
        }
        first.build_developer_report.assert_not_called()
        second.build_developer_report.assert_called_once()

    async def test_get_developer_report_skips_broken_entry(self, hass) -> None:
        """get_developer_report should skip one broken coordinator report."""
        broken = MagicMock()
        broken.build_developer_report.side_effect = RuntimeError("boom")
        healthy = MagicMock()
        healthy.build_developer_report.return_value = {"debug_mode": False}

        entry_1 = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry_1.add_to_hass(hass)
        entry_1.runtime_data = broken

        entry_2 = MockConfigEntry(domain=DOMAIN, data={"phone": "13900000000"})
        entry_2.add_to_hass(hass)
        entry_2.runtime_data = healthy

        result = await _async_handle_get_developer_report(hass, service_call(hass, {}))

        assert result == {
            "entry_count": 1,
            "reports": [{"debug_mode": False}],
        }
        broken.build_developer_report.assert_called_once()
        healthy.build_developer_report.assert_called_once()

    async def test_query_command_result_service(self, hass) -> None:
        """query_command_result service should return one confirmed diagnostic result."""
        device = self._create_device(serial="mesh_group_49155")
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.client.query_command_result = AsyncMock(
            return_value={"success": True}
        )

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_query_command_result(
            hass,
            service_call(
                hass,
                {ATTR_DEVICE_ID: device.serial, ATTR_MSG_SN: "682550445474"},
            ),
        )

        assert result["serial"] == "mesh_group_49155"
        assert result["msg_sn"] == "682550445474"
        assert result["max_attempts"] == 6
        assert result["time_budget_seconds"] == 3.0
        assert result["state"] == "confirmed"
        assert result["attempts"] == 1
        assert result["attempt_limit"] == 5
        assert result["retry_delays_seconds"] == pytest.approx((0.35, 0.7, 1.4, 0.55))
        assert result["result"] == {"success": True}
        coordinator.client.query_command_result.assert_awaited_once_with(
            msg_sn="682550445474",
            device_id="mesh_group_49155",
            device_type=device.device_type_hex,
        )

    async def test_query_command_result_service_polls_until_confirmed(
        self, hass
    ) -> None:
        """query_command_result service should keep polling pending states within budget."""
        device = self._create_device(serial="mesh_group_49155")
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.client.query_command_result = AsyncMock(
            side_effect=[
                {"code": "140006", "message": "设备未响应", "success": False},
                {"code": "100000", "message": "服务异常", "success": False},
                {"code": "0000", "message": "success", "success": True},
            ]
        )

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        sleep_mock = AsyncMock()
        with patch(
            "custom_components.lipro.core.command.result.asyncio.sleep",
            new=sleep_mock,
        ):
            result = await _async_handle_query_command_result(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_MSG_SN: "682550445474"},
                ),
            )

        assert result["state"] == "confirmed"
        assert result["attempts"] == 3
        assert result["attempt_limit"] == 5
        assert result["result"] == {
            "code": "0000",
            "message": "success",
            "success": True,
        }
        assert result["retry_delays_seconds"] == pytest.approx((0.35, 0.7, 1.4, 0.55))
        assert sleep_mock.await_args_list == [call(0.35), call(0.7)]
        assert coordinator.client.query_command_result.await_count == 3

    async def test_get_city_service(self, hass) -> None:
        """get_city service should return first coordinator city result."""
        coordinator = MagicMock()
        coordinator.client.get_city = AsyncMock(
            return_value={"province": "广东省", "city": "江门市"}
        )

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_get_city(hass, service_call(hass, {}))
        assert result == {"result": {"province": "广东省", "city": "江门市"}}

    async def test_query_user_cloud_service(self, hass) -> None:
        """query_user_cloud service should return first coordinator result."""
        coordinator = MagicMock()
        coordinator.client.query_user_cloud = AsyncMock(return_value={"data": []})

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await _async_handle_query_user_cloud(hass, service_call(hass, {}))
        assert result == {"result": {"data": []}}

    async def test_get_city_service_falls_back_to_next_coordinator(self, hass) -> None:
        """get_city should continue to next coordinator when one fails."""
        first = MagicMock()
        first.client.get_city = AsyncMock(
            side_effect=LiproApiError("temporary failure", code=500)
        )
        second = MagicMock()
        second.client.get_city = AsyncMock(
            return_value={"province": "广东省", "city": "深圳市"}
        )

        entry_1 = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry_1.add_to_hass(hass)
        entry_1.runtime_data = first

        entry_2 = MockConfigEntry(domain=DOMAIN, data={"phone": "13900000000"})
        entry_2.add_to_hass(hass)
        entry_2.runtime_data = second

        result = await _async_handle_get_city(hass, service_call(hass, {}))
        assert result == {"result": {"province": "广东省", "city": "深圳市"}}

    async def test_get_city_service_skips_unexpected_error(self, hass) -> None:
        """get_city should skip unexpected coordinator errors and continue."""
        first = MagicMock()
        first.client.get_city = AsyncMock(side_effect=RuntimeError("boom"))
        second = MagicMock()
        second.client.get_city = AsyncMock(
            return_value={"province": "浙江省", "city": "杭州市"}
        )

        entry_1 = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry_1.add_to_hass(hass)
        entry_1.runtime_data = first

        entry_2 = MockConfigEntry(domain=DOMAIN, data={"phone": "13900000000"})
        entry_2.add_to_hass(hass)
        entry_2.runtime_data = second

        result = await _async_handle_get_city(hass, service_call(hass, {}))
        assert result == {"result": {"province": "浙江省", "city": "杭州市"}}

    async def test_query_user_cloud_service_falls_back_to_next_coordinator(
        self, hass
    ) -> None:
        """query_user_cloud should continue to next coordinator when one fails."""
        first = MagicMock()
        first.client.query_user_cloud = AsyncMock(
            side_effect=LiproApiError("temporary failure", code=500)
        )
        second = MagicMock()
        second.client.query_user_cloud = AsyncMock(return_value={"data": [1, 2]})

        entry_1 = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry_1.add_to_hass(hass)
        entry_1.runtime_data = first

        entry_2 = MockConfigEntry(domain=DOMAIN, data={"phone": "13900000000"})
        entry_2.add_to_hass(hass)
        entry_2.runtime_data = second

        result = await _async_handle_query_user_cloud(hass, service_call(hass, {}))
        assert result == {"result": {"data": [1, 2]}}

    async def test_query_user_cloud_service_skips_unexpected_error(self, hass) -> None:
        """query_user_cloud should skip unexpected coordinator errors and continue."""
        first = MagicMock()
        first.client.query_user_cloud = AsyncMock(side_effect=RuntimeError("boom"))
        second = MagicMock()
        second.client.query_user_cloud = AsyncMock(return_value={"data": []})

        entry_1 = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry_1.add_to_hass(hass)
        entry_1.runtime_data = first

        entry_2 = MockConfigEntry(domain=DOMAIN, data={"phone": "13900000000"})
        entry_2.add_to_hass(hass)
        entry_2.runtime_data = second

        result = await _async_handle_query_user_cloud(hass, service_call(hass, {}))
        assert result == {"result": {"data": []}}

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
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_SENSOR_DEVICE_ID: "03ab5ccd7c7167d8",
                    ATTR_MESH_TYPE: "2",
                },
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
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_SENSOR_DEVICE_ID: "03ab5ccd7c7167d8",
                    ATTR_MESH_TYPE: "2",
                },
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
        """submit_developer_feedback uploads one scoped report when entry_id is provided."""
        coordinator = MagicMock()
        coordinator.build_developer_report.return_value = {"runtime": {"ok": True}}

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        share_manager = MagicMock()
        share_manager.submit_developer_feedback = AsyncMock(return_value=True)

        with (
            patch(
                "custom_components.lipro.services.wiring.get_anonymous_share_manager",
                return_value=share_manager,
            ) as get_share_manager,
            patch(
                "custom_components.lipro.services.wiring.async_get_clientsession",
                return_value=MagicMock(),
            ),
        ):
            result = await _async_handle_submit_developer_feedback(
                hass,
                service_call(
                    hass,
                    {ATTR_ENTRY_ID: entry.entry_id, "note": "manual validation run"},
                ),
            )

        assert result == {
            "success": True,
            "submitted_entries": 1,
            "requested_entry_id": entry.entry_id,
        }
        get_share_manager.assert_called_once_with(hass, entry_id=entry.entry_id)
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
                "custom_components.lipro.services.wiring.get_anonymous_share_manager",
                return_value=share_manager,
            ),
            patch(
                "custom_components.lipro.services.wiring.async_get_clientsession",
                return_value=MagicMock(),
            ),
            pytest.raises(HomeAssistantError),
        ):
            await _async_handle_submit_developer_feedback(hass, service_call(hass, {}))

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
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_COMMAND: "POWER_ON",
                    ATTR_PROPERTIES: [{"key": "powerState", "value": "1"}],
                },
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
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: requested_id,
                    ATTR_COMMAND: "POWER_ON",
                },
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
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )

    async def test_send_command_handler_push_failed_maps_translation(
        self, hass
    ) -> None:
        """pushSuccess=false style failures should use push_failed translation key."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        coordinator.async_send_command = AsyncMock(return_value=False)
        coordinator.last_command_failure = {
            "reason": "push_failed",
            "code": "push_failed",
        }

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await _async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )
        assert exc.value.translation_key == "command_push_failed"

    async def test_send_command_handler_offline_code_maps_translation(
        self, hass
    ) -> None:
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
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
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
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
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
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )

    async def test_send_command_handler_api_error_code_maps_translation(
        self, hass
    ) -> None:
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
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
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
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
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
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
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
            hass, service_call(hass, {ATTR_DEVICE_ID: device.serial})
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
            hass, service_call(hass, {ATTR_ENTITY_ID: entity_id})
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
            hass, service_call(hass, {ATTR_DEVICE_ID: device.serial})
        )

        assert result == {
            "serial": device.serial,
            "schedules": [
                {
                    "id": 9,
                    "active": True,
                    "days": [1],
                    "times": ["01:00"],
                    "events": [1],
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
            hass, service_call(hass, {ATTR_DEVICE_ID: device.serial})
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
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_DAYS: [1, 2, 3],
                    ATTR_TIMES: [3600],
                    ATTR_EVENTS: [0],
                },
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
            service_call(
                hass,
                {
                    ATTR_ENTITY_ID: [entity_id],
                    ATTR_DAYS: [1],
                    ATTR_TIMES: [3600],
                    ATTR_EVENTS: [1],
                },
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
            service_call(
                hass,
                {ATTR_DEVICE_ID: device.serial, ATTR_SCHEDULE_IDS: [1]},
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
            service_call(
                hass,
                {ATTR_DEVICE_ID: device.serial, ATTR_SCHEDULE_IDS: [1, 2]},
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
            service_call(
                hass,
                {ATTR_ENTITY_ID: entity_id, ATTR_SCHEDULE_IDS: [1, 2]},
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
            "custom_components.lipro.services.wiring.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            result = await _async_handle_submit_anonymous_share(
                hass, service_call(hass, {})
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
                "custom_components.lipro.services.wiring.get_anonymous_share_manager",
                return_value=share_manager,
            ),
            pytest.raises(HomeAssistantError),
        ):
            await _async_handle_submit_anonymous_share(hass, service_call(hass, {}))

    async def test_get_anonymous_share_report_returns_empty(self, hass) -> None:
        """get_anonymous_share_report returns empty payload when no report."""
        share_manager = MagicMock()
        share_manager.get_pending_report.return_value = None

        with patch(
            "custom_components.lipro.services.wiring.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            result = await _async_handle_get_anonymous_share_report(
                hass, service_call(hass, {})
            )

        assert result == {"has_data": False, "devices": [], "errors": []}
