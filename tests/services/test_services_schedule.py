"""Tests for schedule service helpers."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core import LiproApiError
from custom_components.lipro.services.schedule import (
    async_call_schedule_client,
    normalize_schedule_row,
)


def test_normalize_schedule_row_uses_empty_schedule_when_schedule_field_invalid() -> (
    None
):
    """Non-dict ``schedule`` values should fallback to an empty schedule."""
    result = normalize_schedule_row({"id": 10, "schedule": "invalid"})

    assert result == {
        "id": 10,
        "active": True,
        "days": [],
        "times": [],
        "events": [],
    }


@pytest.mark.asyncio
async def test_async_call_schedule_client_maps_lipro_api_error() -> None:
    """LiproApiError should be logged and mapped via raise_service_error."""
    device = SimpleNamespace(
        iot_device_id="03ab0000000000a1",
        device_type_hex="0x1032",
        extra_data={"gateway_device_id": "", "group_member_ids": []},
    )
    api_error = LiproApiError("boom", 500)
    client_call = AsyncMock(side_effect=api_error)
    logger = MagicMock()
    raise_service_error = MagicMock(side_effect=RuntimeError("mapped"))

    with pytest.raises(RuntimeError, match="mapped"):
        await async_call_schedule_client(
            device,
            client_call,
            error_log="API error getting schedules: %s",
            error_translation_key="schedule_fetch_failed",
            logger=logger,
            raise_service_error=raise_service_error,
        )

    client_call.assert_awaited_once_with(
        "03ab0000000000a1",
        "0x1032",
        mesh_gateway_id="",
        mesh_member_ids=[],
    )
    logger.warning.assert_called_once_with("API error getting schedules: %s", api_error)
    raise_service_error.assert_called_once_with("schedule_fetch_failed", err=api_error)
