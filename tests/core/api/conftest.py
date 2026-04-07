"""Shared import home for topicized API regression suites."""

from __future__ import annotations

import hashlib
import json
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.lipro.const.api import (
    PATH_BLE_SCHEDULE_ADD,
    PATH_BLE_SCHEDULE_DELETE,
    PATH_BLE_SCHEDULE_GET,
    PATH_FETCH_BODY_SENSOR_HISTORY,
    PATH_FETCH_DOOR_SENSOR_HISTORY,
    PATH_GET_CITY,
    PATH_QUERY_COMMAND_RESULT,
    PATH_QUERY_CONNECT_STATUS,
    PATH_QUERY_CONTROLLER_OTA,
    PATH_QUERY_OTA_INFO,
    PATH_QUERY_OTA_INFO_V2,
    PATH_QUERY_OUTLET_POWER,
    PATH_QUERY_USER_CLOUD,
    PATH_SCHEDULE_ADD,
    PATH_SCHEDULE_DELETE,
    PATH_SCHEDULE_GET,
)
from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRestFacade,
)

__all__ = [
    "PATH_BLE_SCHEDULE_ADD",
    "PATH_BLE_SCHEDULE_DELETE",
    "PATH_BLE_SCHEDULE_GET",
    "PATH_FETCH_BODY_SENSOR_HISTORY",
    "PATH_FETCH_DOOR_SENSOR_HISTORY",
    "PATH_GET_CITY",
    "PATH_QUERY_COMMAND_RESULT",
    "PATH_QUERY_CONNECT_STATUS",
    "PATH_QUERY_CONTROLLER_OTA",
    "PATH_QUERY_OTA_INFO",
    "PATH_QUERY_OTA_INFO_V2",
    "PATH_QUERY_OUTLET_POWER",
    "PATH_QUERY_USER_CLOUD",
    "PATH_SCHEDULE_ADD",
    "PATH_SCHEDULE_DELETE",
    "PATH_SCHEDULE_GET",
    "AsyncMock",
    "LiproApiError",
    "LiproAuthError",
    "LiproConnectionError",
    "LiproRestFacade",
    "MagicMock",
    "aiohttp",
    "hashlib",
    "json",
    "patch",
    "pytest",
]
