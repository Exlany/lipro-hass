"""Service contract constants and schemas for Lipro integration."""

from __future__ import annotations

from collections.abc import Mapping
import re
from typing import Final, NotRequired, TypedDict, cast

import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from ..const.base import IOT_DEVICE_ID_PREFIX

SERVICE_SEND_COMMAND: Final = "send_command"
SERVICE_GET_SCHEDULES: Final = "get_schedules"
SERVICE_ADD_SCHEDULE: Final = "add_schedule"
SERVICE_DELETE_SCHEDULES: Final = "delete_schedules"
SERVICE_SUBMIT_ANONYMOUS_SHARE: Final = "submit_anonymous_share"
SERVICE_GET_ANONYMOUS_SHARE_REPORT: Final = "get_anonymous_share_report"
SERVICE_GET_DEVELOPER_REPORT: Final = "get_developer_report"
SERVICE_SUBMIT_DEVELOPER_FEEDBACK: Final = "submit_developer_feedback"
SERVICE_QUERY_COMMAND_RESULT: Final = "query_command_result"
SERVICE_GET_CITY: Final = "get_city"
SERVICE_QUERY_USER_CLOUD: Final = "query_user_cloud"
SERVICE_FETCH_BODY_SENSOR_HISTORY: Final = "fetch_body_sensor_history"
SERVICE_FETCH_DOOR_SENSOR_HISTORY: Final = "fetch_door_sensor_history"
SERVICE_REFRESH_DEVICES: Final = "refresh_devices"

ATTR_DEVICE_ID: Final = "device_id"
ATTR_ENTRY_ID: Final = "entry_id"
ATTR_COMMAND: Final = "command"
ATTR_PROPERTIES: Final = "properties"
ATTR_DAYS: Final = "days"
ATTR_TIMES: Final = "times"
ATTR_EVENTS: Final = "events"
ATTR_SCHEDULE_IDS: Final = "schedule_ids"
ATTR_NOTE: Final = "note"
ATTR_MSG_SN: Final = "msg_sn"
ATTR_MAX_ATTEMPTS: Final = "max_attempts"
ATTR_TIME_BUDGET_SECONDS: Final = "time_budget_seconds"
ATTR_SENSOR_DEVICE_ID: Final = "sensor_device_id"
ATTR_MESH_TYPE: Final = "mesh_type"

_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
_COMMAND_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_MSG_SN_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
_SENSOR_DEVICE_ID_PATTERN = re.compile(
    rf"^{re.escape(IOT_DEVICE_ID_PREFIX)}[0-9A-Fa-f]{{12}}$"
)
_MESH_TYPE_PATTERN = re.compile(r"^[12]$")

_MAX_DEVICE_ID_LEN: Final = 64
_MAX_COMMAND_LEN: Final = 64
_MAX_PROPERTY_KEY_LEN: Final = 64
_MAX_PROPERTY_VALUE_LEN: Final = 512
_MAX_SERVICE_LIST_ITEMS: Final = 64
_MAX_ENTRY_ID_LEN: Final = 64
_MAX_NOTE_LEN: Final = 500
_MAX_MSG_SN_LEN: Final = 128
_MAX_QUERY_COMMAND_RESULT_ATTEMPTS: Final = 10
_MAX_QUERY_COMMAND_RESULT_TIME_BUDGET_SECONDS: Final = 15.0
_MAX_SENSOR_DEVICE_ID_LEN: Final = 64
_MAX_MESH_TYPE_LEN: Final = 16

def _strict_string(value: object) -> str:
    """Accept only already-string values without coercion."""
    if not isinstance(value, str):
        raise vol.Invalid("expected string")
    return value


def _strict_list(value: object) -> list[object]:
    """Accept only list payloads without coercion."""
    if not isinstance(value, list):
        raise vol.Invalid("expected list")
    return value


_DEVICE_ID_VALIDATOR = vol.All(
    _strict_string,
    vol.Length(min=1, max=_MAX_DEVICE_ID_LEN),
    vol.Match(_IDENTIFIER_PATTERN),
)
_COMMAND_VALIDATOR = vol.All(
    _strict_string,
    vol.Length(min=1, max=_MAX_COMMAND_LEN),
    vol.Match(_COMMAND_PATTERN),
)
_PROPERTY_KEY_VALIDATOR = vol.All(
    _strict_string,
    vol.Length(min=1, max=_MAX_PROPERTY_KEY_LEN),
    vol.Match(_IDENTIFIER_PATTERN),
)
_PROPERTY_VALUE_VALIDATOR = vol.All(
    _strict_string,
    vol.Length(max=_MAX_PROPERTY_VALUE_LEN),
)
_PROPERTY_ITEM_SCHEMA = vol.Schema(
    {
        vol.Required("key"): _PROPERTY_KEY_VALIDATOR,
        vol.Required("value"): _PROPERTY_VALUE_VALIDATOR,
    }
)


SERVICE_SEND_COMMAND_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): _DEVICE_ID_VALIDATOR,
        vol.Required(ATTR_COMMAND): _COMMAND_VALIDATOR,
        vol.Optional(ATTR_PROPERTIES): vol.All(
            _strict_list,
            vol.Length(max=_MAX_SERVICE_LIST_ITEMS),
            [_PROPERTY_ITEM_SCHEMA],
        ),
    },
)

SERVICE_GET_SCHEDULES_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): vol.All(
            cv.string,
            vol.Length(min=1, max=_MAX_DEVICE_ID_LEN),
            vol.Match(_IDENTIFIER_PATTERN),
        ),
    },
)

SERVICE_ADD_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): vol.All(
            cv.string,
            vol.Length(min=1, max=_MAX_DEVICE_ID_LEN),
            vol.Match(_IDENTIFIER_PATTERN),
        ),
        vol.Required(ATTR_DAYS): vol.All(
            cv.ensure_list,
            vol.Length(max=_MAX_SERVICE_LIST_ITEMS),
            [vol.All(vol.Coerce(int), vol.Range(min=1, max=7))],
        ),
        vol.Required(ATTR_TIMES): vol.All(
            cv.ensure_list,
            vol.Length(max=_MAX_SERVICE_LIST_ITEMS),
            [vol.All(vol.Coerce(int), vol.Range(min=0, max=86399))],
        ),
        vol.Required(ATTR_EVENTS): vol.All(
            cv.ensure_list,
            vol.Length(max=_MAX_SERVICE_LIST_ITEMS),
            [vol.Coerce(int)],
        ),
    },
)

SERVICE_DELETE_SCHEDULES_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): vol.All(
            cv.string,
            vol.Length(min=1, max=_MAX_DEVICE_ID_LEN),
            vol.Match(_IDENTIFIER_PATTERN),
        ),
        vol.Required(ATTR_SCHEDULE_IDS): vol.All(
            cv.ensure_list,
            vol.Length(max=_MAX_SERVICE_LIST_ITEMS),
            [vol.Coerce(int)],
        ),
    },
)

SERVICE_SUBMIT_ANONYMOUS_SHARE_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): vol.All(
            cv.string,
            vol.Length(min=1, max=_MAX_ENTRY_ID_LEN),
            vol.Match(_IDENTIFIER_PATTERN),
        ),
    },
)

SERVICE_GET_ANONYMOUS_SHARE_REPORT_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): vol.All(
            cv.string,
            vol.Length(min=1, max=_MAX_ENTRY_ID_LEN),
            vol.Match(_IDENTIFIER_PATTERN),
        ),
    },
)

SERVICE_GET_DEVELOPER_REPORT_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): vol.All(
            cv.string,
            vol.Length(min=1, max=_MAX_ENTRY_ID_LEN),
            vol.Match(_IDENTIFIER_PATTERN),
        ),
    },
)

SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): vol.All(
            cv.string,
            vol.Length(min=1, max=_MAX_ENTRY_ID_LEN),
            vol.Match(_IDENTIFIER_PATTERN),
        ),
        vol.Optional(ATTR_NOTE): vol.All(cv.string, vol.Length(max=_MAX_NOTE_LEN)),
    },
)

SERVICE_QUERY_COMMAND_RESULT_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): vol.All(
            cv.string,
            vol.Length(min=1, max=_MAX_DEVICE_ID_LEN),
            vol.Match(_IDENTIFIER_PATTERN),
        ),
        vol.Required(ATTR_MSG_SN): vol.All(
            cv.string,
            vol.Length(min=1, max=_MAX_MSG_SN_LEN),
            vol.Match(_MSG_SN_PATTERN),
        ),
        vol.Optional(ATTR_MAX_ATTEMPTS, default=6): vol.All(
            vol.Coerce(int),
            vol.Range(min=1, max=_MAX_QUERY_COMMAND_RESULT_ATTEMPTS),
        ),
        vol.Optional(ATTR_TIME_BUDGET_SECONDS, default=3.0): vol.All(
            vol.Coerce(float),
            vol.Range(min=0, max=_MAX_QUERY_COMMAND_RESULT_TIME_BUDGET_SECONDS),
        ),
    },
)

SERVICE_FETCH_SENSOR_HISTORY_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): vol.All(
            cv.string,
            vol.Length(min=1, max=_MAX_DEVICE_ID_LEN),
            vol.Match(_IDENTIFIER_PATTERN),
        ),
        vol.Required(ATTR_SENSOR_DEVICE_ID): vol.All(
            cv.string,
            vol.Length(min=1, max=_MAX_SENSOR_DEVICE_ID_LEN),
            vol.Match(_SENSOR_DEVICE_ID_PATTERN),
        ),
        vol.Optional(ATTR_MESH_TYPE, default="2"): vol.All(
            cv.string,
            vol.Length(min=1, max=_MAX_MESH_TYPE_LEN),
            vol.Match(_MESH_TYPE_PATTERN),
        ),
    },
)

SERVICE_REFRESH_DEVICES_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): vol.All(
            cv.string,
            vol.Length(min=1, max=_MAX_ENTRY_ID_LEN),
            vol.Match(_IDENTIFIER_PATTERN),
        ),
    },
)


class ServiceProperty(TypedDict):
    """One key/value property item accepted by send_command."""

    key: str
    value: str


type ServicePropertyList = list[ServiceProperty]


class SendCommandServiceData(TypedDict, total=False):
    """Normalized payload accepted by the send_command service handler."""

    device_id: str
    command: str
    properties: ServicePropertyList


class ServicePropertySummary(TypedDict):
    """Log-safe summary of the requested command properties."""

    count: int
    keys: list[str]


class CommandFailureSummary(TypedDict, total=False):
    """Normalized command failure details exposed to control/service callers."""

    reason: str
    code: int | str
    route: str
    device_id: str


class SendCommandResult(TypedDict):
    """Structured response payload returned by send_command."""

    success: bool
    serial: str
    requested_device_id: NotRequired[str]
    resolved_device_id: NotRequired[str]


class RefreshDevicesResult(TypedDict):
    """Structured response payload returned by refresh_devices."""

    success: bool
    refreshed_entries: int
    requested_entry_id: NotRequired[str]



def normalize_send_command_payload(
    payload: Mapping[str, object],
) -> SendCommandServiceData:
    """Validate and normalize one direct send_command payload."""
    return cast(SendCommandServiceData, SERVICE_SEND_COMMAND_SCHEMA(dict(payload)))
