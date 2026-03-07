"""Tests for schedule endpoint mixin branch coverage."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.core.api.endpoints.schedule import (
    _ClientScheduleEndpointsMixin,
)
from custom_components.lipro.core.api.errors import LiproApiError


class _DummyClient(_ClientScheduleEndpointsMixin):
    @staticmethod
    def _is_invalid_param_error_code(code: object) -> bool:
        return str(code) == "100000"


def test_resolve_ble_schedule_candidate_ids_invalid_device_id_returns_empty() -> None:
    client = _DummyClient()

    assert client._resolve_ble_schedule_candidate_ids(device_id="not-an-iot-id") == []


@pytest.mark.asyncio
async def test_execute_schedule_operation_uses_mesh_request_when_candidate_ids_present() -> (
    None
):
    client = _DummyClient()
    mesh_request = AsyncMock(return_value=[{"id": 1}])
    ble_request = AsyncMock(return_value=[{"id": 2}])
    standard_request = AsyncMock(return_value=[{"id": 3}])

    result = await client._execute_schedule_operation(
        device_id="03ab0000000000a1",
        candidate_ids=["03ab0000000000a1"],
        ble_candidate_ids=[],
        ble_operation="GET",
        ble_request=ble_request,
        mesh_request=mesh_request,
        standard_request=standard_request,
    )

    assert result == [{"id": 1}]
    mesh_request.assert_awaited_once_with(["03ab0000000000a1"])
    ble_request.assert_not_awaited()
    standard_request.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_schedule_operation_raises_invalid_param_for_mesh_get_without_standard_fallback() -> None:
    client = _DummyClient()
    err = LiproApiError("invalid", code="100000")
    ble_request = AsyncMock(side_effect=err)
    standard_request = AsyncMock(return_value=[{"id": 3}])

    with pytest.raises(LiproApiError, match="invalid"):
        await client._execute_schedule_operation(
            device_id="mesh_group_49155",
            candidate_ids=["03ab0000000000a1"],
            ble_candidate_ids=["03ab0000000000a1"],
            ble_operation="GET",
            ble_request=ble_request,
            mesh_request=AsyncMock(return_value=[{"id": 1}]),
            standard_request=standard_request,
            allow_standard_fallback=False,
        )

    standard_request.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_schedule_operation_falls_back_to_standard_when_allowed() -> None:
    client = _DummyClient()
    ble_request = AsyncMock(side_effect=LiproApiError("invalid", code="100000"))
    standard_request = AsyncMock(return_value=[{"id": 3}])

    result = await client._execute_schedule_operation(
        device_id="03ab0000000000a1",
        candidate_ids=None,
        ble_candidate_ids=["03ab0000000000a1"],
        ble_operation="GET",
        ble_request=ble_request,
        mesh_request=AsyncMock(return_value=[{"id": 1}]),
        standard_request=standard_request,
    )

    assert result == [{"id": 3}]
    standard_request.assert_awaited_once()
