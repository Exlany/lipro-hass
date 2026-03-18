"""Tests for Lipro integration __init__.py module.

Tests cover:
- PLATFORMS list completeness
- Service schema structure (keys, required/optional)
- Service constants definitions
- Attribute constants definitions
"""

from __future__ import annotations

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

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
    CONF_DEBUG_MODE,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REFRESH_TOKEN,
    CONF_REQUEST_TIMEOUT,
    CONF_SCAN_INTERVAL,
    DEFAULT_REQUEST_TIMEOUT,
    MAX_SCAN_INTERVAL,
)
from custom_components.lipro.control.service_router import (
    _summarize_service_properties,
    async_handle_refresh_devices,
)
from custom_components.lipro.core import (
    AuthSessionSnapshot,
    LiproAuthError,
    LiproAuthManager,
    LiproConnectionError,
    LiproProtocolFacade,
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
from homeassistant.const import Platform
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    ServiceValidationError,
)
from homeassistant.helpers import device_registry as dr
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

    @staticmethod
    def _attach_auth_service(coordinator: MagicMock) -> MagicMock:
        """Attach the formal async auth and protocol surfaces expected by services."""
        coordinator.auth_service = MagicMock(
            async_ensure_authenticated=AsyncMock(),
            async_trigger_reauth=AsyncMock(),
        )
        coordinator.protocol_service = MagicMock()
        return coordinator

    async def test_async_setup_registers_services(self, hass) -> None:
        """Services are registered by async_setup and idempotent."""
        assert await async_setup(hass, {}) is True
        assert hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND)
        assert hass.services.has_service(DOMAIN, SERVICE_GET_SCHEDULES)
        assert hass.services.has_service(DOMAIN, SERVICE_ADD_SCHEDULE)
        assert hass.services.has_service(DOMAIN, SERVICE_DELETE_SCHEDULES)
        assert hass.services.has_service(DOMAIN, SERVICE_SUBMIT_ANONYMOUS_SHARE)
        assert hass.services.has_service(DOMAIN, SERVICE_GET_ANONYMOUS_SHARE_REPORT)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_DEVELOPER_REPORT)
        assert not hass.services.has_service(DOMAIN, SERVICE_SUBMIT_DEVELOPER_FEEDBACK)
        assert not hass.services.has_service(DOMAIN, SERVICE_QUERY_COMMAND_RESULT)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_CITY)
        assert not hass.services.has_service(DOMAIN, SERVICE_QUERY_USER_CLOUD)
        assert not hass.services.has_service(DOMAIN, SERVICE_FETCH_BODY_SENSOR_HISTORY)
        assert not hass.services.has_service(DOMAIN, SERVICE_FETCH_DOOR_SENSOR_HISTORY)
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
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.add_update_listener = MagicMock(return_value=MagicMock())
        entry.async_on_unload = MagicMock()

        mock_auth = MagicMock()
        mock_auth.set_tokens = MagicMock()
        mock_auth.set_credentials = MagicMock()
        mock_auth.ensure_valid_token = AsyncMock()
        mock_auth.get_auth_session.return_value = AuthSessionSnapshot(
            access_token="new_access",
            refresh_token="new_refresh",
            user_id=None,
            expires_at=1234567890,
            phone_id="phone-id",
            biz_id=None,
        )

        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator.config_entry = entry

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.LiproProtocolFacade", return_value=MagicMock()
            ),
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            patch(
                "custom_components.lipro.Coordinator",
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
        assert hass.services.has_service(DOMAIN, SERVICE_GET_DEVELOPER_REPORT)
        assert hass.services.has_service(DOMAIN, SERVICE_SUBMIT_DEVELOPER_FEEDBACK)
        assert hass.services.has_service(DOMAIN, SERVICE_QUERY_COMMAND_RESULT)
        assert hass.services.has_service(DOMAIN, SERVICE_GET_CITY)
        assert hass.services.has_service(DOMAIN, SERVICE_QUERY_USER_CLOUD)
        assert hass.services.has_service(DOMAIN, SERVICE_FETCH_BODY_SENSOR_HISTORY)
        assert hass.services.has_service(DOMAIN, SERVICE_FETCH_DOOR_SENSOR_HISTORY)

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
                client_factory=LiproProtocolFacade,
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
                client_factory=LiproProtocolFacade,
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
        mock_auth.get_auth_session.return_value = AuthSessionSnapshot(
            access_token=None,
            refresh_token=None,
            user_id=None,
            expires_at=None,
            phone_id="phone-id",
            biz_id=None,
        )

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
        mock_auth.get_auth_session.return_value = AuthSessionSnapshot(
            access_token="new_access",
            refresh_token="new_refresh",
            user_id=None,
            expires_at=1234567890,
            phone_id="phone-id",
            biz_id=None,
        )

        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator.async_shutdown = AsyncMock()

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.LiproProtocolFacade", return_value=MagicMock()
            ),
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            patch(
                "custom_components.lipro.Coordinator",
                return_value=mock_coordinator,
            ),
            patch.object(
                hass.config_entries,
                "async_forward_entry_setups",
                AsyncMock(side_effect=RuntimeError("platform setup failed")),
            ),
            patch.object(hass.config_entries, "async_update_entry"),
            patch("custom_components.lipro._LOGGER.debug") as mock_debug,
            pytest.raises(RuntimeError, match="platform setup failed"),
        ):
            await async_setup_entry(hass, entry)

        mock_coordinator.async_shutdown.assert_awaited_once()
        assert mock_debug.call_args.args[1:] == (
            "setup",
            "setup_failed",
            "cleanup_and_raise",
            "RuntimeError",
        )
        assert getattr(entry, "runtime_data", None) is None
        entry.add_update_listener.assert_not_called()
        entry.async_on_unload.assert_not_called()

    async def test_async_setup_entry_forward_setup_cancelled_rolls_back_runtime_data(
        self,
        hass,
    ) -> None:
        """Platform setup cancellation should still shut down coordinator and clear runtime data."""
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
        mock_auth.get_auth_session.return_value = AuthSessionSnapshot(
            access_token="new_access",
            refresh_token="new_refresh",
            user_id=None,
            expires_at=1234567890,
            phone_id="phone-id",
            biz_id=None,
        )

        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator.async_shutdown = AsyncMock()

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.LiproProtocolFacade", return_value=MagicMock()
            ),
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            patch(
                "custom_components.lipro.Coordinator",
                return_value=mock_coordinator,
            ),
            patch.object(
                hass.config_entries,
                "async_forward_entry_setups",
                AsyncMock(side_effect=asyncio.CancelledError),
            ),
            patch.object(hass.config_entries, "async_update_entry"),
            pytest.raises(asyncio.CancelledError),
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
        mock_auth.get_auth_session.return_value = AuthSessionSnapshot(
            access_token="old_access",
            refresh_token="old_refresh",
            user_id=None,
            expires_at=1234567890,
            phone_id="phone-id",
            biz_id=None,
        )

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
            patch(
                "custom_components.lipro.LiproProtocolFacade", return_value=MagicMock()
            ),
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            patch(
                "custom_components.lipro.Coordinator",
                return_value=mock_coordinator,
            ),
            pytest.raises(RuntimeError, match="refresh failed"),
        ):
            await async_setup_entry(hass, entry)

        mock_coordinator.async_shutdown.assert_awaited_once()
        assert getattr(entry, "runtime_data", None) is None
        entry.add_update_listener.assert_not_called()
        entry.async_on_unload.assert_not_called()

    async def test_async_setup_entry_first_refresh_not_ready_uses_named_contract(
        self,
        hass,
    ) -> None:
        """First refresh not-ready failures should keep a named setup contract."""
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
        mock_auth.get_auth_session.return_value = AuthSessionSnapshot(
            access_token="old_access",
            refresh_token="old_refresh",
            user_id=None,
            expires_at=1234567890,
            phone_id="phone-id",
            biz_id=None,
        )

        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock(
            side_effect=ConfigEntryNotReady("refresh later")
        )
        mock_coordinator.async_shutdown = AsyncMock()

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.LiproProtocolFacade", return_value=MagicMock()
            ),
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            patch(
                "custom_components.lipro.Coordinator",
                return_value=mock_coordinator,
            ),
            patch("custom_components.lipro._LOGGER.debug") as mock_debug,
            pytest.raises(ConfigEntryNotReady),
        ):
            await async_setup_entry(hass, entry)

        mock_coordinator.async_shutdown.assert_awaited_once()
        assert mock_debug.call_args.args[1:] == (
            "setup",
            "setup_not_ready",
            "cleanup_and_raise",
            "ConfigEntryNotReady",
        )
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
            patch(
                "custom_components.lipro.LiproProtocolFacade", return_value=MagicMock()
            ),
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
        mock_auth.get_auth_session.return_value = AuthSessionSnapshot(
            access_token="access",
            refresh_token="refresh",
            user_id=None,
            expires_at=1234567890,
            phone_id="phone-id",
            biz_id=None,
        )

        mock_client = MagicMock()
        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.LiproProtocolFacade", return_value=mock_client
            ) as pc,
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            patch(
                "custom_components.lipro.Coordinator",
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
            patch(
                "custom_components.lipro.LiproProtocolFacade", return_value=MagicMock()
            ),
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            pytest.raises(ConfigEntryNotReady),
        ):
            await async_setup_entry(hass, entry)

    async def test_async_unload_entry_removes_services_on_last_entry(
        self, hass
    ) -> None:
        """Service registrations are removed when last entry unloads."""
        await async_setup(hass, {})
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
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
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
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
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
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

        assert mock_warning.call_args.args[1:] == (
            "unload",
            "unload_shutdown_degraded",
            "log_and_continue",
            "RuntimeError",
        )
        assert getattr(entry, "runtime_data", None) is None

    async def test_async_unload_entry_removes_services_when_lock_unavailable(
        self,
        hass,
    ) -> None:
        """Unload should remove shared infra when lock store is unavailable."""
        await async_setup(hass, {})
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
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
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        mock_reload = AsyncMock()
        with patch.object(hass.config_entries, "async_reload", mock_reload):
            await async_reload_entry(hass, entry)

        mock_reload.assert_awaited_once_with(entry.entry_id)

    async def test_async_reload_entry_uses_named_not_ready_contract(
        self, hass
    ) -> None:
        """Reload failures should preserve a named contract before re-raising."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        with (
            patch.object(
                hass.config_entries,
                "async_reload",
                AsyncMock(side_effect=ConfigEntryNotReady("retry reload")),
            ),
            patch("custom_components.lipro._LOGGER.debug") as mock_debug,
            pytest.raises(ConfigEntryNotReady),
        ):
            await async_reload_entry(hass, entry)

        assert mock_debug.call_args.args[1:] == (
            "reload",
            "reload_not_ready",
            "propagate",
            "ConfigEntryNotReady",
        )

    async def test_async_unload_entry_removes_services_when_only_non_runtime_entries_remain(
        self, hass
    ) -> None:
        """Services should be removed when no other runtime-loaded entry remains."""
        await async_setup(hass, {})
        active_entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        active_entry.add_to_hass(hass)
        active_entry.runtime_data = MagicMock(async_shutdown=AsyncMock())

        # Simulate a configured but not loaded entry (no runtime_data).
        passive_entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
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
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
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
        first = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        first.add_to_hass(hass)
        first_service = MagicMock()
        first_service.async_refresh_devices = AsyncMock()
        first.runtime_data = MagicMock(device_refresh_service=first_service)

        second = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
        second.add_to_hass(hass)
        second_service = MagicMock()
        second_service.async_refresh_devices = AsyncMock()
        second.runtime_data = MagicMock(device_refresh_service=second_service)

        result = await async_handle_refresh_devices(hass, service_call(hass, {}))

        assert result["success"] is True
        assert result["refreshed_entries"] == 2
        assert "entry_ids" not in result
        first_service.async_refresh_devices.assert_awaited_once()
        second_service.async_refresh_devices.assert_awaited_once()

    async def test_refresh_devices_handler_filters_by_entry_id(self, hass) -> None:
        """refresh_devices should refresh only the selected config entry."""
        first = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        first.add_to_hass(hass)
        first_service = MagicMock()
        first_service.async_refresh_devices = AsyncMock()
        first.runtime_data = MagicMock(device_refresh_service=first_service)

        second = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
        second.add_to_hass(hass)
        second_service = MagicMock()
        second_service.async_refresh_devices = AsyncMock()
        second.runtime_data = MagicMock(device_refresh_service=second_service)

        result = await async_handle_refresh_devices(
            hass,
            service_call(hass, {ATTR_ENTRY_ID: second.entry_id}),
        )

        assert result["success"] is True
        assert result["refreshed_entries"] == 1
        assert result["requested_entry_id"] == second.entry_id
        first_service.async_refresh_devices.assert_not_awaited()
        second_service.async_refresh_devices.assert_awaited_once()

    async def test_refresh_devices_handler_unknown_entry_raises(self, hass) -> None:
        """refresh_devices should raise translated validation error for bad entry_id."""
        with pytest.raises(ServiceValidationError) as exc:
            await async_handle_refresh_devices(
                hass,
                service_call(hass, {ATTR_ENTRY_ID: "missing_entry"}),
            )

        assert exc.value.translation_key == "entry_not_found"

    async def test_device_registry_disable_enable_triggers_entry_reload(
        self, hass
    ) -> None:
        """Lipro device disable/enable transitions should trigger config entry reload."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
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
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
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
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
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
