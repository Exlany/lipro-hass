"""Resilience tests for service schemas and multi-coordinator behavior."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
import voluptuous as vol

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.core import LiproApiError
from custom_components.lipro.services.contracts import (
    ATTR_COMMAND,
    ATTR_DEVICE_ID,
    ATTR_ENTRY_ID,
    ATTR_MAX_ATTEMPTS,
    ATTR_MESH_TYPE,
    ATTR_MSG_SN,
    ATTR_NOTE,
    ATTR_PROPERTIES,
    ATTR_SENSOR_DEVICE_ID,
    ATTR_TIME_BUDGET_SECONDS,
    SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
    SERVICE_GET_DEVELOPER_REPORT_SCHEMA,
    SERVICE_QUERY_COMMAND_RESULT_SCHEMA,
    SERVICE_REFRESH_DEVICES_SCHEMA,
    SERVICE_SEND_COMMAND_SCHEMA,
    SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA,
)
from custom_components.lipro.services.wiring import _async_handle_get_city
from homeassistant.exceptions import HomeAssistantError
from tests.helpers.service_call import service_call


def _add_runtime_entry(hass, coordinator: MagicMock, *, phone: str) -> MockConfigEntry:
    """Attach one runtime coordinator to Home Assistant config entries."""
    entry = MockConfigEntry(domain=DOMAIN, data={"phone": phone})
    entry.add_to_hass(hass)
    entry.runtime_data = coordinator
    return entry


@pytest.mark.parametrize(
    ("schema", "payload"),
    [
        pytest.param(
            SERVICE_SEND_COMMAND_SCHEMA,
            {ATTR_COMMAND: "a" * 65},
            id="send_command_command_too_long",
        ),
        pytest.param(
            SERVICE_SEND_COMMAND_SCHEMA,
            {ATTR_COMMAND: ""},
            id="send_command_command_empty",
        ),
        pytest.param(
            SERVICE_SEND_COMMAND_SCHEMA,
            {ATTR_COMMAND: "powerOn", ATTR_DEVICE_ID: ""},
            id="send_command_device_id_empty",
        ),
        pytest.param(
            SERVICE_SEND_COMMAND_SCHEMA,
            {ATTR_COMMAND: "powerOn", ATTR_DEVICE_ID: "d" * 65},
            id="send_command_device_id_too_long",
        ),
        pytest.param(
            SERVICE_SEND_COMMAND_SCHEMA,
            {
                ATTR_COMMAND: "powerOn",
                ATTR_PROPERTIES: [{"key": "k" * 65, "value": "1"}],
            },
            id="send_command_property_key_too_long",
        ),
        pytest.param(
            SERVICE_SEND_COMMAND_SCHEMA,
            {
                ATTR_COMMAND: "powerOn",
                ATTR_PROPERTIES: [{"key": "powerState", "value": "v" * 513}],
            },
            id="send_command_property_value_too_long",
        ),
        pytest.param(
            SERVICE_QUERY_COMMAND_RESULT_SCHEMA,
            {ATTR_MSG_SN: ""},
            id="query_command_result_msg_sn_empty",
        ),
        pytest.param(
            SERVICE_QUERY_COMMAND_RESULT_SCHEMA,
            {ATTR_MSG_SN: "m" * 129},
            id="query_command_result_msg_sn_too_long",
        ),
        pytest.param(
            SERVICE_QUERY_COMMAND_RESULT_SCHEMA,
            {ATTR_MSG_SN: "123", ATTR_MAX_ATTEMPTS: 0},
            id="query_command_result_max_attempts_too_low",
        ),
        pytest.param(
            SERVICE_QUERY_COMMAND_RESULT_SCHEMA,
            {ATTR_MSG_SN: "123", ATTR_MAX_ATTEMPTS: 11},
            id="query_command_result_max_attempts_too_high",
        ),
        pytest.param(
            SERVICE_QUERY_COMMAND_RESULT_SCHEMA,
            {ATTR_MSG_SN: "123", ATTR_TIME_BUDGET_SECONDS: -0.1},
            id="query_command_result_time_budget_negative",
        ),
        pytest.param(
            SERVICE_QUERY_COMMAND_RESULT_SCHEMA,
            {ATTR_MSG_SN: "123", ATTR_TIME_BUDGET_SECONDS: 15.1},
            id="query_command_result_time_budget_too_high",
        ),
        pytest.param(
            SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA,
            {ATTR_NOTE: "n" * 501},
            id="submit_developer_feedback_note_too_long",
        ),
        pytest.param(
            SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA,
            {ATTR_ENTRY_ID: ""},
            id="submit_developer_feedback_entry_id_empty",
        ),
        pytest.param(
            SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA,
            {ATTR_ENTRY_ID: "e" * 65},
            id="submit_developer_feedback_entry_id_too_long",
        ),
        pytest.param(
            SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA,
            {ATTR_ENTRY_ID: "entry.bad"},
            id="submit_developer_feedback_entry_id_invalid_chars",
        ),
        pytest.param(
            SERVICE_GET_DEVELOPER_REPORT_SCHEMA,
            {ATTR_ENTRY_ID: ""},
            id="get_developer_report_entry_id_empty",
        ),
        pytest.param(
            SERVICE_GET_DEVELOPER_REPORT_SCHEMA,
            {ATTR_ENTRY_ID: "e" * 65},
            id="get_developer_report_entry_id_too_long",
        ),
        pytest.param(
            SERVICE_GET_DEVELOPER_REPORT_SCHEMA,
            {ATTR_ENTRY_ID: "entry.bad"},
            id="get_developer_report_entry_id_invalid_chars",
        ),
        pytest.param(
            SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
            {ATTR_SENSOR_DEVICE_ID: "", ATTR_MESH_TYPE: "2"},
            id="fetch_sensor_history_sensor_device_id_empty",
        ),
        pytest.param(
            SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
            {ATTR_SENSOR_DEVICE_ID: "03ab5ccd7caaaaaa", ATTR_MESH_TYPE: ""},
            id="fetch_sensor_history_mesh_type_empty",
        ),
        pytest.param(
            SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
            {ATTR_SENSOR_DEVICE_ID: "03ab5ccd7caaaaaa", ATTR_MESH_TYPE: "3"},
            id="fetch_sensor_history_mesh_type_invalid_enum",
        ),
        pytest.param(
            SERVICE_REFRESH_DEVICES_SCHEMA,
            {ATTR_ENTRY_ID: ""},
            id="refresh_devices_entry_id_empty",
        ),
        pytest.param(
            SERVICE_REFRESH_DEVICES_SCHEMA,
            {ATTR_ENTRY_ID: "e" * 65},
            id="refresh_devices_entry_id_too_long",
        ),
        pytest.param(
            SERVICE_REFRESH_DEVICES_SCHEMA,
            {ATTR_ENTRY_ID: "entry.bad"},
            id="refresh_devices_entry_id_invalid_chars",
        ),
    ],
)
def test_service_schemas_reject_boundary_invalid_inputs(schema, payload) -> None:
    """Schemas should reject overlong/empty/invalid enum inputs."""
    with pytest.raises(vol.MultipleInvalid):
        schema(payload)


def test_send_command_schema_accepts_max_length_values() -> None:
    """send_command schema should accept max-length boundary values."""
    payload = {
        ATTR_DEVICE_ID: "d" * 64,
        ATTR_COMMAND: "a" * 64,
        ATTR_PROPERTIES: [{"key": "k" * 64, "value": "v" * 512}],
    }
    result = SERVICE_SEND_COMMAND_SCHEMA(payload)
    assert result == payload


def test_query_command_result_schema_accepts_max_msg_sn_length() -> None:
    """query_command_result schema should accept 128-char msg_sn."""
    result = SERVICE_QUERY_COMMAND_RESULT_SCHEMA({ATTR_MSG_SN: "m" * 128})
    assert result[ATTR_MSG_SN] == "m" * 128


def test_query_command_result_schema_applies_polling_defaults() -> None:
    """query_command_result schema should apply bounded polling defaults."""
    result = SERVICE_QUERY_COMMAND_RESULT_SCHEMA({ATTR_MSG_SN: "123"})
    assert result[ATTR_MAX_ATTEMPTS] == 6
    assert result[ATTR_TIME_BUDGET_SECONDS] == 3.0


def test_submit_developer_feedback_schema_accepts_max_note_length() -> None:
    """submit_developer_feedback schema should accept 500-char note."""
    result = SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA({ATTR_NOTE: "n" * 500})
    assert result[ATTR_NOTE] == "n" * 500


def test_submit_developer_feedback_schema_accepts_max_entry_id_length() -> None:
    """submit_developer_feedback schema should accept 64-char entry_id."""
    result = SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA({ATTR_ENTRY_ID: "e" * 64})
    assert result[ATTR_ENTRY_ID] == "e" * 64


def test_get_developer_report_schema_accepts_max_entry_id_length() -> None:
    """get_developer_report schema should accept 64-char entry_id."""
    result = SERVICE_GET_DEVELOPER_REPORT_SCHEMA({ATTR_ENTRY_ID: "e" * 64})
    assert result[ATTR_ENTRY_ID] == "e" * 64


def test_refresh_devices_schema_accepts_max_entry_id_length() -> None:
    """refresh_devices schema should accept 64-char entry_id."""
    result = SERVICE_REFRESH_DEVICES_SCHEMA({ATTR_ENTRY_ID: "e" * 64})
    assert result[ATTR_ENTRY_ID] == "e" * 64


@pytest.mark.parametrize("mesh_type", ["1", "2"])
def test_fetch_sensor_history_schema_accepts_mesh_type_enum(mesh_type: str) -> None:
    """fetch_sensor_history schema should accept supported mesh_type values."""
    result = SERVICE_FETCH_SENSOR_HISTORY_SCHEMA(
        {ATTR_SENSOR_DEVICE_ID: "03ab5ccd7caaaaaa", ATTR_MESH_TYPE: mesh_type}
    )
    assert result[ATTR_MESH_TYPE] == mesh_type


@pytest.mark.asyncio
async def test_get_city_raises_last_api_error_when_all_coordinators_fail(hass) -> None:
    """When all coordinators fail with API errors, the last error is surfaced."""
    first = MagicMock()
    first.async_get_city = AsyncMock(
        side_effect=LiproApiError("first failure", code="140004")
    )
    second = MagicMock()
    second.async_get_city = AsyncMock(
        side_effect=LiproApiError("last failure", code="250001")
    )

    _add_runtime_entry(hass, first, phone="13800000000")
    _add_runtime_entry(hass, second, phone="13900000000")

    with pytest.raises(HomeAssistantError, match=r"code=250001"):
        await _async_handle_get_city(hass, service_call(hass, {}))

    assert first.async_get_city.await_count == 1
    assert second.async_get_city.await_count == 1


@pytest.mark.asyncio
async def test_get_city_mixed_coordinator_results_return_first_success(hass) -> None:
    """Unexpected/API failures should be skipped until first successful coordinator."""
    runtime_error_coordinator = MagicMock()
    runtime_error_coordinator.async_get_city = AsyncMock(
        side_effect=RuntimeError("boom")
    )

    api_error_coordinator = MagicMock()
    api_error_coordinator.async_get_city = AsyncMock(
        side_effect=LiproApiError("temporary", code="500")
    )

    success_coordinator = MagicMock()
    success_coordinator.async_get_city = AsyncMock(
        return_value={"province": "江苏省", "city": "苏州市"}
    )

    never_called_after_success = MagicMock()
    never_called_after_success.async_get_city = AsyncMock(
        return_value={"province": "浙江省", "city": "杭州市"}
    )

    _add_runtime_entry(hass, runtime_error_coordinator, phone="13800000000")
    _add_runtime_entry(hass, api_error_coordinator, phone="13900000000")
    _add_runtime_entry(hass, success_coordinator, phone="13700000000")
    _add_runtime_entry(hass, never_called_after_success, phone="13600000000")

    result = await _async_handle_get_city(hass, service_call(hass, {}))

    assert result == {"result": {"province": "江苏省", "city": "苏州市"}}
    assert runtime_error_coordinator.async_get_city.await_count == 1
    assert api_error_coordinator.async_get_city.await_count == 1
    assert success_coordinator.async_get_city.await_count == 1
    never_called_after_success.async_get_city.assert_not_called()


@pytest.mark.asyncio
async def test_get_city_returns_empty_result_without_active_coordinators(hass) -> None:
    """No active coordinator should produce an empty payload instead of errors."""
    entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
    entry.add_to_hass(hass)
    entry.runtime_data = None

    result = await _async_handle_get_city(hass, service_call(hass, {}))
    assert result == {"result": {}}


@pytest.mark.asyncio
async def test_get_city_concurrent_calls_with_mixed_coordinators_are_stable(
    hass,
) -> None:
    """Concurrent get_city calls should complete without unhandled exceptions."""
    failing = MagicMock()
    failing.async_get_city = AsyncMock(
        side_effect=LiproApiError("transient", code="500")
    )

    async def _slow_success() -> dict[str, str]:
        await asyncio.sleep(0)
        return {"province": "广东省", "city": "深圳市"}

    succeeding = MagicMock()
    succeeding.async_get_city = AsyncMock(side_effect=_slow_success)

    _add_runtime_entry(hass, failing, phone="13800000000")
    _add_runtime_entry(hass, succeeding, phone="13900000000")

    call_count = 25
    results = await asyncio.gather(
        *(
            _async_handle_get_city(hass, service_call(hass, {}))
            for _ in range(call_count)
        )
    )

    assert len(results) == call_count
    assert all(
        result == {"result": {"province": "广东省", "city": "深圳市"}}
        for result in results
    )
    assert failing.async_get_city.await_count == call_count
    assert succeeding.async_get_city.await_count == call_count
