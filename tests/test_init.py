"""Tests for Lipro integration __init__.py module.

Tests cover:
- PLATFORMS list completeness
- Service schema structure (keys, required/optional)
- Service constants definitions
- Attribute constants definitions

Schema validation tests that call the schema with data require
homeassistant.helpers.config_validation (cv.string, cv.ensure_list),
which is only available in the full HA test environment. Those tests
are marked with skipif accordingly.
"""

from __future__ import annotations

import voluptuous as vol

# Check if full HA test environment is available
try:
    from pytest_homeassistant_custom_component.common import (
        MockConfigEntry,  # noqa: F401
    )

    HAS_HA_TEST_ENV = True
except ImportError:
    HAS_HA_TEST_ENV = False

import pytest

from custom_components.lipro import (
    ATTR_COMMAND,
    ATTR_DAYS,
    ATTR_DEVICE_ID,
    ATTR_EVENTS,
    ATTR_PROPERTIES,
    ATTR_SCHEDULE_IDS,
    ATTR_TIMES,
    PLATFORMS,
    SERVICE_ADD_SCHEDULE,
    SERVICE_ADD_SCHEDULE_SCHEMA,
    SERVICE_DELETE_SCHEDULES,
    SERVICE_DELETE_SCHEDULES_SCHEMA,
    SERVICE_GET_ANONYMOUS_SHARE_REPORT,
    SERVICE_GET_SCHEDULES,
    SERVICE_GET_SCHEDULES_SCHEMA,
    SERVICE_SEND_COMMAND,
    SERVICE_SEND_COMMAND_SCHEMA,
    SERVICE_SUBMIT_ANONYMOUS_SHARE,
)
from homeassistant.const import Platform


class TestPlatforms:
    """Tests for the PLATFORMS list."""

    def test_platforms_count(self):
        """Test PLATFORMS has exactly 8 entries."""
        assert len(PLATFORMS) == 8

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

    def test_service_constants_are_strings(self):
        """Test all service constants are strings."""
        assert isinstance(SERVICE_SEND_COMMAND, str)
        assert isinstance(SERVICE_GET_SCHEDULES, str)
        assert isinstance(SERVICE_ADD_SCHEDULE, str)
        assert isinstance(SERVICE_DELETE_SCHEDULES, str)
        assert isinstance(SERVICE_SUBMIT_ANONYMOUS_SHARE, str)
        assert isinstance(SERVICE_GET_ANONYMOUS_SHARE_REPORT, str)


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


class TestSchemaValidation:
    """Tests for service schema validation with actual data.

    These tests call the schemas with data, which requires cv.string and
    cv.ensure_list from homeassistant.helpers.config_validation to be real.
    They only run in the full HA test environment.
    """

    pytestmark = pytest.mark.skipif(
        not HAS_HA_TEST_ENV,
        reason="Requires pytest-homeassistant-custom-component",
    )

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
