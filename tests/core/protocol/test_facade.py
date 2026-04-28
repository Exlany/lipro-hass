"""Focused regressions for the unified protocol root and MQTT child facade."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar, cast
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.lipro.core.api.client import LiproRestFacade
from custom_components.lipro.core.api.request_policy import RequestPolicy
from custom_components.lipro.core.api.session_state import RestSessionState
from custom_components.lipro.core.api.types import (
    ConnectStatusOutcome,
    ConnectStatusQueryResult,
)
from custom_components.lipro.core.protocol.diagnostics_context import (
    ProtocolDiagnosticsContext,
)
from custom_components.lipro.core.protocol.facade import LiproProtocolFacade
from custom_components.lipro.core.protocol.mqtt_facade import LiproMqttFacade
from custom_components.lipro.core.protocol.session import ProtocolSessionState
from custom_components.lipro.core.protocol.telemetry import ProtocolTelemetry


def _as_mapping(value: object) -> Mapping[str, object]:
    assert isinstance(value, Mapping)
    return value


class _FakeRestFacade:
    created: ClassVar[list[_FakeRestFacade]] = []

    def __init__(
        self,
        phone_id: str,
        session: object | None = None,
        request_timeout: int = 30,
        *,
        entry_id: str | None = None,
        session_state: RestSessionState | None = None,
        request_policy: RequestPolicy | None = None,
    ) -> None:
        self.phone_id = phone_id
        self.session = session
        self.request_timeout = request_timeout
        self.entry_id = entry_id
        self.session_state = session_state
        self.request_policy = request_policy
        type(self).created.append(self)

    def auth_recovery_telemetry_snapshot(self) -> dict[str, object]:
        return {"refresh_attempts": 2}


def _build_mqtt_facade(
    *,
    biz_id: str = "mqtt-biz",
    is_connected: bool = True,
    subscribed_count: int = 2,
    last_error: Exception | None = None,
) -> LiproMqttFacade:
    rest_state = RestSessionState(
        phone_id="test-phone-id",
        session=None,
        request_timeout=30,
        entry_id="entry-1",
    )
    session_state = ProtocolSessionState(rest_state)
    session_state.bind_mqtt_biz_id(biz_id)
    telemetry = ProtocolTelemetry()
    diagnostics_context = ProtocolDiagnosticsContext(
        session_state=session_state,
        telemetry=telemetry,
        entry_id="entry-1",
    )
    transport = MagicMock()
    transport.is_connected = is_connected
    transport.subscribed_devices = {"device-1"}
    transport.subscribed_count = subscribed_count
    transport.last_error = last_error
    transport.wait_until_connected = AsyncMock(return_value=True)
    return LiproMqttFacade(
        transport,
        session_state=session_state,
        telemetry=telemetry,
        diagnostics_context=diagnostics_context,
    )


def test_protocol_facade_builds_rest_child_from_shared_state_and_policy() -> None:
    _FakeRestFacade.created.clear()
    request_policy = RequestPolicy()
    session = cast(aiohttp.ClientSession, MagicMock(spec=aiohttp.ClientSession))
    session_state = RestSessionState(
        phone_id="test-phone-id",
        session=None,
        request_timeout=45,
        entry_id="entry-1",
    )

    facade = LiproProtocolFacade(
        "test-phone-id",
        session,
        request_timeout=45,
        entry_id="entry-1",
        session_state=session_state,
        request_policy=request_policy,
        rest_facade_factory=cast(type[LiproRestFacade], _FakeRestFacade),
    )

    rest = _FakeRestFacade.created[-1]
    assert cast(object, facade.rest) is rest
    assert rest.phone_id == "test-phone-id"
    assert rest.session is session
    assert rest.request_timeout == 45
    assert rest.entry_id == "entry-1"
    assert rest.session_state is session_state
    assert rest.session_state is facade.session_state.rest_state
    assert rest.request_policy is request_policy
    assert facade.request_policy is request_policy

    facade.access_token = "access-token"
    facade.refresh_token = "refresh-token"
    facade.user_id = 42
    facade.biz_id = "biz-42"

    assert session_state.access_token == "access-token"
    assert session_state.refresh_token == "refresh-token"
    assert session_state.user_id == 42
    assert session_state.biz_id == "biz-42"


def test_attach_mqtt_facade_updates_active_child_and_diagnostics_snapshot() -> None:
    facade = LiproProtocolFacade(
        "test-phone-id",
        entry_id="entry-1",
        rest_facade_factory=cast(type[LiproRestFacade], _FakeRestFacade),
    )
    mqtt_facade = _build_mqtt_facade()

    facade.attach_mqtt_facade(mqtt_facade)
    snapshot = facade.protocol_diagnostics_snapshot()

    assert facade.mqtt is mqtt_facade
    assert facade.biz_id == "mqtt-biz"
    assert snapshot["entry_id"] == "entry-1"
    session_snapshot = _as_mapping(snapshot["session"])
    telemetry_snapshot = _as_mapping(snapshot["telemetry"])

    assert session_snapshot["biz_id"] == "mqtt-biz"
    assert telemetry_snapshot["mqtt_connected"] is True
    assert telemetry_snapshot["mqtt_subscribed_count"] == 2
    assert snapshot["auth_recovery"] == {"refresh_attempts": 2}


def test_build_mqtt_facade_uses_shared_protocol_state() -> None:
    facade = LiproProtocolFacade(
        "test-phone-id",
        entry_id="entry-1",
        rest_facade_factory=cast(type[LiproRestFacade], _FakeRestFacade),
    )
    fake_mqtt = MagicMock()
    fake_mqtt.protocol_session_state.biz_id = "biz-77"

    with patch(
        "custom_components.lipro.core.protocol.facade.LiproMqttFacade.from_credentials",
        return_value=fake_mqtt,
    ) as factory:
        result = facade.build_mqtt_facade(
            access_key="ak",
            secret_key="sk",
            biz_id="biz-77",
            phone_id="test-phone-id",
        )

    assert result is fake_mqtt
    assert facade.mqtt is fake_mqtt
    assert facade.biz_id == "biz-77"
    factory.assert_called_once_with(
        access_key="ak",
        secret_key="sk",
        biz_id="biz-77",
        phone_id="test-phone-id",
        session_state=facade.session_state,
        telemetry=facade.telemetry,
        diagnostics_context=facade.diagnostics_context,
        on_message=None,
        on_connect=None,
        on_disconnect=None,
        on_error=None,
    )


def test_mqtt_facade_last_error_records_transport_error_on_access() -> None:
    mqtt_facade = _build_mqtt_facade(last_error=RuntimeError("boom"))

    err = mqtt_facade.last_error

    assert isinstance(err, RuntimeError)
    assert mqtt_facade.telemetry.mqtt_last_error_type == "RuntimeError"
    assert mqtt_facade.telemetry.mqtt_last_error_stage == "transport"


@pytest.mark.asyncio
async def test_mqtt_facade_wait_until_connected_records_transport_error_after_success() -> (
    None
):
    mqtt_facade = _build_mqtt_facade(last_error=RuntimeError("boom"))

    connected = await mqtt_facade.wait_until_connected(timeout=3.0)

    assert connected is True
    cast(Any, mqtt_facade._transport.wait_until_connected).assert_awaited_once_with(
        timeout=3.0
    )
    assert mqtt_facade.telemetry.mqtt_last_error_type == "RuntimeError"
    assert mqtt_facade.telemetry.mqtt_last_error_stage == "transport"


def test_protocol_rest_ports_bind_real_adapters_instead_of_rest_aliases() -> None:
    facade = LiproProtocolFacade(
        "test-phone-id",
        entry_id="entry-1",
        rest_facade_factory=cast(type[LiproRestFacade], _FakeRestFacade),
    )

    assert facade._rest_ports.auth is not facade.rest
    assert facade._rest_ports.inventory is not facade.rest
    assert facade._rest_ports.status is not facade.rest
    assert facade._rest_ports.command is not facade.rest
    assert facade._rest_ports.misc is not facade.rest
    assert facade._rest_ports.schedule is not facade.rest
    assert facade._rest_ports.diagnostics is not facade.rest


@pytest.mark.asyncio
async def test_protocol_query_connect_status_preserves_typed_result() -> None:
    facade = LiproProtocolFacade(
        "test-phone-id",
        entry_id="entry-1",
        rest_facade_factory=cast(type[LiproRestFacade], _FakeRestFacade),
    )
    expected = ConnectStatusQueryResult(
        ConnectStatusOutcome.SUCCESS,
        {"03ab5ccd7caaaaaa": True},
    )
    facade._rest_ports.status.query_connect_status = AsyncMock(return_value=expected)

    result = await facade.query_connect_status(["03ab5ccd7caaaaaa"])

    assert result is expected
    cast(Any, facade._rest_ports.status.query_connect_status).assert_awaited_once_with(
        ["03ab5ccd7caaaaaa"]
    )


@pytest.mark.asyncio
async def test_protocol_add_device_schedule_forwards_group_id() -> None:
    facade = LiproProtocolFacade(
        "test-phone-id",
        entry_id="entry-1",
        rest_facade_factory=cast(type[LiproRestFacade], _FakeRestFacade),
    )
    facade._rest_ports.schedule.add_device_schedule = AsyncMock(return_value=[])

    result = await facade.add_device_schedule(
        "03ab5ccd7caaaaaa",
        1,
        [1, 2, 3],
        [3600],
        [0],
        group_id="mesh_group_10001",
    )

    assert result == []
    cast(Any, facade._rest_ports.schedule.add_device_schedule).assert_awaited_once_with(
        "03ab5ccd7caaaaaa",
        1,
        [1, 2, 3],
        [3600],
        [0],
        "mesh_group_10001",
        mesh_gateway_id="",
        mesh_member_ids=None,
    )


@pytest.mark.asyncio
async def test_protocol_delete_device_schedules_forwards_group_id() -> None:
    facade = LiproProtocolFacade(
        "test-phone-id",
        entry_id="entry-1",
        rest_facade_factory=cast(type[LiproRestFacade], _FakeRestFacade),
    )
    facade._rest_ports.schedule.delete_device_schedules = AsyncMock(return_value=[])

    result = await facade.delete_device_schedules(
        "03ab5ccd7caaaaaa",
        1,
        [4],
        group_id="mesh_group_10001",
    )

    assert result == []
    cast(
        Any, facade._rest_ports.schedule.delete_device_schedules
    ).assert_awaited_once_with(
        "03ab5ccd7caaaaaa",
        1,
        [4],
        "mesh_group_10001",
        mesh_gateway_id="",
        mesh_member_ids=None,
    )
