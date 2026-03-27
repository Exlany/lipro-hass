"""Protocol contract facade and runtime smoke suites."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api import LiproRestFacade
from custom_components.lipro.core.api.session_state import RestSessionState
from custom_components.lipro.core.protocol import LiproProtocolFacade
from custom_components.lipro.core.protocol.diagnostics_context import (
    ProtocolDiagnosticsContext,
)
from custom_components.lipro.core.protocol.facade import LiproMqttFacade
from custom_components.lipro.core.protocol.session import ProtocolSessionState
from custom_components.lipro.core.protocol.telemetry import ProtocolTelemetry


def test_lipro_rest_facade_is_available_as_phase_2_rest_child_facade() -> None:
    assert LiproRestFacade.__name__ == "LiproRestFacade"


def _build_mqtt_facade(client: MagicMock) -> tuple[LiproMqttFacade, ProtocolTelemetry]:
    telemetry = ProtocolTelemetry()
    session_state = ProtocolSessionState(
        RestSessionState(
            phone_id="test-phone-id",
            session=None,
            request_timeout=30,
            entry_id="entry-1",
        )
    )
    diagnostics_context = ProtocolDiagnosticsContext(
        session_state=session_state,
        telemetry=telemetry,
        entry_id="entry-1",
    )
    return (
        LiproMqttFacade(
            client,
            session_state=session_state,
            telemetry=telemetry,
            diagnostics_context=diagnostics_context,
        ),
        telemetry,
    )


@pytest.mark.asyncio
async def test_lipro_mqtt_facade_records_transport_error_and_reraises() -> None:
    client = MagicMock()
    client.is_connected = False
    client.subscribed_devices = set()
    client.subscribed_count = 0
    client.last_error = None
    client.start = AsyncMock(side_effect=RuntimeError("boom"))

    mqtt_facade, telemetry = _build_mqtt_facade(client)

    with pytest.raises(RuntimeError, match="boom"):
        await mqtt_facade.start(["03ab5ccd7c000001"])

    assert telemetry.mqtt_start_count == 1
    assert telemetry.mqtt_last_error_type == "RuntimeError"
    assert telemetry.mqtt_last_error_stage == "start"


@pytest.mark.asyncio
async def test_lipro_mqtt_facade_reraises_cancelled_without_recording_error() -> None:
    client = MagicMock()
    client.is_connected = False
    client.subscribed_devices = set()
    client.subscribed_count = 0
    client.last_error = None
    client.start = AsyncMock(side_effect=asyncio.CancelledError)

    mqtt_facade, telemetry = _build_mqtt_facade(client)

    with pytest.raises(asyncio.CancelledError):
        await mqtt_facade.start(["03ab5ccd7c000001"])

    assert telemetry.mqtt_start_count == 1
    assert telemetry.mqtt_last_error_type is None
    assert telemetry.mqtt_last_error_stage is None


def test_lipro_rest_facade_uses_explicit_surface_instead_of_dynamic_delegation() -> None:
    for base in LiproRestFacade.__mro__:
        if base is object:
            continue
        assert "__getattr__" not in base.__dict__
        assert "__dir__" not in base.__dict__


def test_lipro_rest_facade_no_longer_exports_aggregate_endpoint_mixin() -> None:
    module_text = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "lipro"
        / "core"
        / "api"
        / "endpoints"
        / "__init__.py"
    ).read_text(encoding="utf-8")
    assert "_ClientEndpointsMixin" not in module_text


def test_schedule_api_service_no_longer_shapes_rest_schedule_surface() -> None:
    module_text = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "lipro"
        / "core"
        / "api"
        / "client.py"
    ).read_text(encoding="utf-8")
    assert "ScheduleApiService" not in module_text


def test_protocol_root_owns_shared_rest_session_and_request_policy() -> None:
    client = LiproProtocolFacade("test-phone-id")

    assert client.rest._session_state is client.session_state.rest_state
    assert client.rest._request_policy is client.request_policy


def test_protocol_root_keeps_request_gateway_and_transport_executor_inside_rest_child() -> None:
    client = LiproProtocolFacade("test-phone-id")

    assert client.rest.request_policy is client.request_policy
    assert client.rest._transport_executor._request_policy is client.request_policy
    assert hasattr(client.rest, "_request_gateway")
    assert hasattr(client.rest, "_transport_executor")
    assert not hasattr(client, "_request_gateway")
    assert not hasattr(client, "_transport_executor")


def test_protocol_root_file_keeps_rest_port_and_mqtt_child_out_of_root_body() -> None:
    module_text = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "lipro"
        / "core"
        / "protocol"
        / "facade.py"
    ).read_text(encoding="utf-8")

    assert "from .mqtt_facade import" in module_text
    assert "from .rest_port import" in module_text
    assert "class LiproMqttFacade:" not in module_text
    assert "class _RestFacadePort(" not in module_text
    assert "self._rest_port." not in module_text
    assert "bind_protocol_rest_port_family" in module_text


def test_rest_port_file_exposes_concern_local_ports_instead_of_one_wide_port() -> None:
    module_text = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "lipro"
        / "core"
        / "protocol"
        / "rest_port.py"
    ).read_text(encoding="utf-8")

    assert "class _RestFacadePort(" not in module_text
    assert "class _RestAuthPort(" in module_text
    assert "class _RestStatusPort(" in module_text
    assert "class _RestCommandPort(" in module_text
    assert "class _RestSchedulePort(" in module_text
    assert "class ProtocolRestPortFamily:" in module_text


def test_protocol_rest_method_support_file_stays_bound_to_single_root_story() -> None:
    method_text = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "lipro"
        / "core"
        / "protocol"
        / "protocol_facade_rest_methods.py"
    ).read_text(encoding="utf-8")
    facade_text = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "lipro"
        / "core"
        / "protocol"
        / "facade.py"
    ).read_text(encoding="utf-8")

    assert "class LiproProtocolFacade" not in method_text
    assert "class LiproRestFacade" not in method_text
    assert "self._rest_ports.auth." in method_text
    assert "self._rest_ports.schedule." in method_text
    assert "from . import protocol_facade_rest_methods as _rest_methods" in facade_text
    assert "login = _rest_methods.login" in facade_text
    assert "query_device_status = _rest_methods.query_device_status" in facade_text


def test_rest_child_facade_file_uses_local_request_and_endpoint_collaborators() -> None:
    client_module_text = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "lipro"
        / "core"
        / "api"
        / "client.py"
    ).read_text(encoding="utf-8")
    facade_module_text = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "lipro"
        / "core"
        / "api"
        / "rest_facade.py"
    ).read_text(encoding="utf-8")

    assert "from .rest_facade import LiproRestFacade" in client_module_text
    assert "RestAuthRecoveryCoordinator" in facade_module_text
    assert "RestTransportExecutor" in facade_module_text
    assert "RestEndpointSurface" in facade_module_text
    assert "RestSessionState" in facade_module_text
