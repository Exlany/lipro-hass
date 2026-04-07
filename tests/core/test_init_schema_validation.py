"""Topicized init regression coverage extracted from `tests/core/test_init.py` (test_init_schema_validation)."""

from __future__ import annotations

from .test_init import (
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
    SERVICE_ADD_SCHEDULE_SCHEMA,
    SERVICE_DELETE_SCHEDULES_SCHEMA,
    SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
    SERVICE_GET_ANONYMOUS_SHARE_REPORT_SCHEMA,
    SERVICE_GET_DEVELOPER_REPORT_SCHEMA,
    SERVICE_GET_SCHEDULES_SCHEMA,
    SERVICE_QUERY_COMMAND_RESULT_SCHEMA,
    SERVICE_REFRESH_DEVICES_SCHEMA,
    SERVICE_SEND_COMMAND_SCHEMA,
    SERVICE_SUBMIT_ANONYMOUS_SHARE_SCHEMA,
    SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA,
    _summarize_service_properties,
    pytest,
    vol,
)


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
