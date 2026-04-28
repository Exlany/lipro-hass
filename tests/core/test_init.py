# ruff: noqa: F401
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


__all__ = [
    "ATTR_COMMAND",
    "ATTR_DAYS",
    "ATTR_DEVICE_ID",
    "ATTR_ENTRY_ID",
    "ATTR_EVENTS",
    "ATTR_MAX_ATTEMPTS",
    "ATTR_MESH_TYPE",
    "ATTR_MSG_SN",
    "ATTR_NOTE",
    "ATTR_PROPERTIES",
    "ATTR_SCHEDULE_IDS",
    "ATTR_SENSOR_DEVICE_ID",
    "ATTR_TIMES",
    "ATTR_TIME_BUDGET_SECONDS",
    "CONF_ACCESS_TOKEN",
    "CONF_PASSWORD_HASH",
    "CONF_PHONE",
    "CONF_PHONE_ID",
    "CONF_REFRESH_TOKEN",
    "CONF_REQUEST_TIMEOUT",
    "CONF_SCAN_INTERVAL",
    "DEFAULT_REQUEST_TIMEOUT",
    "DOMAIN",
    "MAX_SCAN_INTERVAL",
    "SERVICE_ADD_SCHEDULE_SCHEMA",
    "SERVICE_DELETE_SCHEDULES_SCHEMA",
    "SERVICE_FETCH_SENSOR_HISTORY_SCHEMA",
    "SERVICE_GET_ANONYMOUS_SHARE_REPORT_SCHEMA",
    "SERVICE_GET_DEVELOPER_REPORT_SCHEMA",
    "SERVICE_GET_SCHEDULES_SCHEMA",
    "SERVICE_QUERY_COMMAND_RESULT_SCHEMA",
    "SERVICE_REFRESH_DEVICES_SCHEMA",
    "SERVICE_SEND_COMMAND_SCHEMA",
    "SERVICE_SUBMIT_ANONYMOUS_SHARE_SCHEMA",
    "SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA",
    "AsyncMock",
    "AuthSessionSnapshot",
    "ConfigEntryAuthFailed",
    "ConfigEntryNotReady",
    "LiproAuthError",
    "LiproConnectionError",
    "LiproDevice",
    "MagicMock",
    "MockConfigEntry",
    "_summarize_service_properties",
    "async_setup_entry",
    "asyncio",
    "patch",
    "pytest",
    "vol",
]
