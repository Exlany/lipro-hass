"""Integration tests for coordinator MQTT wiring with the refactored transport façade."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.core.protocol.contracts import MqttTransportFacade
from custom_components.lipro.core.protocol.facade import LiproMqttFacade

_CONFIG_ENTRY_DATA = {
    "phone": "13800000000",
    "password_hash": "e10adc3949ba59abbe56e057f20f883e",
    "phone_id": "test-phone-id",
    "access_token": "test_token",
    "refresh_token": "test_refresh",
    "user_id": 10001,
}


class _FakeMqttTransport:
    """Capture lifecycle callbacks while emulating a connected MQTT transport."""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        biz_id: str,
        phone_id: str,
        on_message: Callable[[str, dict[str, Any]], None] | None = None,
        on_connect: Callable[[], None] | None = None,
        on_disconnect: Callable[[], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> None:
        self.access_key = access_key
        self.secret_key = secret_key
        self.biz_id = biz_id
        self.phone_id = phone_id
        self.on_message = on_message
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_error = on_error
        self.is_connected = False
        self.last_error: Exception | None = None
        self.subscribed_devices: set[str] = set()
        self.start = AsyncMock(side_effect=self._start)
        self.stop = AsyncMock(side_effect=self._stop)
        self.sync_subscriptions = AsyncMock(side_effect=self._sync_subscriptions)
        self.wait_until_connected = AsyncMock(side_effect=self._wait_until_connected)

    @property
    def subscribed_count(self) -> int:
        return len(self.subscribed_devices)

    async def _start(self, device_ids: list[str]) -> None:
        self.subscribed_devices = set(device_ids)

    async def _stop(self) -> None:
        self.is_connected = False

    async def _sync_subscriptions(self, device_ids: set[str]) -> None:
        self.subscribed_devices = set(device_ids)

    async def _wait_until_connected(self, timeout: float | None = None) -> bool:
        self.is_connected = True
        if self.on_connect is not None:
            self.on_connect()
        return True


class _FakeMqttFacade(LiproMqttFacade):
    """Test façade with explicit callback emit helpers."""

    def __init__(self, **kwargs: Any) -> None:
        self._fake_transport = _FakeMqttTransport(**kwargs)
        self._transport = cast(MqttTransportFacade, self._fake_transport)
        self._session_state = MagicMock()
        self._telemetry = MagicMock()
        self._diagnostics_context = MagicMock()

    def emit_message(self, device_id: str, payload: dict[str, str]) -> None:
        callback = self._fake_transport.on_message
        assert callback is not None
        callback(device_id, payload)

    def emit_disconnect(self) -> None:
        callback = self._fake_transport.on_disconnect
        assert callback is not None
        callback()

    def emit_connect(self) -> None:
        callback = self._fake_transport.on_connect
        assert callback is not None
        callback()


def _make_device(
    serial: str = "03ab5ccd7cxxxxxx",
    *,
    is_group: bool = False,
):
    from custom_components.lipro.core.device import LiproDevice

    return LiproDevice(
        device_number=1,
        serial=serial,
        name="Test Device",
        device_type=1,
        iot_name="lipro_led",
        physical_model="light",
        is_group=is_group,
        properties={},
    )


@pytest.fixture
def coordinator(hass, mock_lipro_api_client, mock_auth_manager):
    """Create a real coordinator wired to mocked API/auth objects."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=_CONFIG_ENTRY_DATA,
        options={},
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
    ) as mock_share:
        mock_share.return_value = MagicMock(is_enabled=False, set_enabled=MagicMock())
        mock_lipro_api_client.attach_mqtt_facade = MagicMock()
        from custom_components.lipro.core.coordinator.coordinator import Coordinator

        return Coordinator(hass, mock_lipro_api_client, mock_auth_manager, entry)


@pytest.mark.asyncio
async def test_async_setup_mqtt_builds_refactored_facade(
    coordinator, mock_lipro_api_client
) -> None:
    coordinator._state.devices = {
        "dev1": _make_device("dev1"),
        "mesh_group_1": _make_device("mesh_group_1", is_group=True),
    }
    mock_lipro_api_client.get_mqtt_config.return_value = {
        "accessKey": "enc-ak",
        "secretKey": "enc-sk",
    }

    with (
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.decrypt_mqtt_credential",
            side_effect=["ak", "sk"],
        ),
    ):
        mock_facade = MagicMock()
        mock_lipro_api_client.build_mqtt_facade = MagicMock(return_value=mock_facade)

        mock_runtime = MagicMock()
        mock_runtime.has_transport = False
        mock_runtime.is_connected = True
        mock_runtime.connect = AsyncMock(return_value=True)
        mock_runtime.bind_transport = MagicMock()
        object.__setattr__(coordinator._runtimes, "mqtt", mock_runtime)

        ok = await coordinator.mqtt_service.async_setup()

    assert ok is True
    mock_runtime.bind_transport.assert_called_once_with(mock_facade)
    mock_runtime.connect.assert_awaited_once_with(device_ids=["mesh_group_1"])
    mqtt_facade_kwargs = mock_lipro_api_client.build_mqtt_facade.call_args.kwargs
    assert callable(mqtt_facade_kwargs["on_message"])
    assert callable(mqtt_facade_kwargs["on_connect"])
    assert callable(mqtt_facade_kwargs["on_disconnect"])
    assert callable(mqtt_facade_kwargs["on_error"])


@pytest.mark.asyncio
async def test_async_setup_mqtt_returns_false_without_config_entry(coordinator) -> None:
    coordinator.config_entry = None

    assert await coordinator.async_setup_mqtt() is False


@pytest.mark.asyncio
async def test_async_setup_mqtt_returns_false_on_config_fetch_timeout(
    coordinator, mock_lipro_api_client
) -> None:
    mock_lipro_api_client.get_mqtt_config.side_effect = TimeoutError()

    assert await coordinator.async_setup_mqtt() is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("decrypt_results", "biz_id"),
    [
        (["", "sk"], "biz001"),
        (["ak", "sk"], None),
    ],
)
async def test_async_setup_mqtt_requires_decrypted_credentials_and_biz_id(
    coordinator,
    mock_lipro_api_client,
    decrypt_results: list[str],
    biz_id: str | None,
) -> None:
    coordinator._state.devices = {"dev1": _make_device("dev1")}
    mock_lipro_api_client.get_mqtt_config.return_value = {
        "accessKey": "enc-ak",
        "secretKey": "enc-sk",
    }

    with (
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.decrypt_mqtt_credential",
            side_effect=decrypt_results,
        ),
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.resolve_mqtt_biz_id",
            return_value=biz_id,
        ),
    ):
        assert await coordinator.async_setup_mqtt() is False


@pytest.mark.asyncio
async def test_async_setup_mqtt_returns_false_when_group_connect_times_out(
    coordinator, mock_lipro_api_client
) -> None:
    coordinator._state.devices = {
        "mesh_group_1": _make_device("mesh_group_1", is_group=True),
    }
    mock_lipro_api_client.get_mqtt_config.return_value = {
        "accessKey": "enc-ak",
        "secretKey": "enc-sk",
    }

    with (
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.decrypt_mqtt_credential",
            side_effect=["ak", "sk"],
        ),
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.resolve_mqtt_biz_id",
            return_value="biz001",
        ),
    ):
        mock_runtime = MagicMock()
        mock_runtime.has_transport = False
        mock_runtime.is_connected = False
        mock_runtime.connect = AsyncMock(side_effect=TimeoutError())
        mock_runtime.disconnect = AsyncMock()
        mock_runtime.detach_transport = MagicMock()
        mock_runtime.bind_transport = MagicMock()
        object.__setattr__(coordinator._runtimes, "mqtt", mock_runtime)

        ok = await coordinator.async_setup_mqtt()

    assert ok is False
    mock_runtime.connect.assert_awaited_once()
    mock_runtime.disconnect.assert_awaited_once()
    mock_runtime.detach_transport.assert_called_once()


@pytest.mark.asyncio
async def test_async_setup_mqtt_returns_false_when_runtime_stays_disconnected(
    coordinator, mock_lipro_api_client
) -> None:
    coordinator._state.devices = {"dev1": _make_device("dev1")}
    mock_lipro_api_client.get_mqtt_config.return_value = {
        "accessKey": "enc-ak",
        "secretKey": "enc-sk",
    }

    with (
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.decrypt_mqtt_credential",
            side_effect=["ak", "sk"],
        ),
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.resolve_mqtt_biz_id",
            return_value="biz001",
        ),
    ):
        mock_runtime = MagicMock()
        mock_runtime.has_transport = False
        mock_runtime.is_connected = False
        mock_runtime.connect = AsyncMock(return_value=False)
        mock_runtime.disconnect = AsyncMock()
        mock_runtime.detach_transport = MagicMock()
        mock_runtime.bind_transport = MagicMock()
        object.__setattr__(coordinator._runtimes, "mqtt", mock_runtime)

        ok = await coordinator.async_setup_mqtt()

    assert ok is False
    mock_runtime.connect.assert_awaited_once()
    mock_runtime.disconnect.assert_awaited_once()
    mock_runtime.detach_transport.assert_called_once()


@pytest.mark.asyncio
async def test_async_setup_mqtt_reraises_cancelled_error(
    coordinator, mock_lipro_api_client
) -> None:
    coordinator._state.devices = {"dev1": _make_device("dev1")}
    mock_lipro_api_client.get_mqtt_config.side_effect = asyncio.CancelledError()

    with pytest.raises(asyncio.CancelledError):
        await coordinator.async_setup_mqtt()


@pytest.mark.asyncio
async def test_async_setup_mqtt_returns_false_on_unexpected_error(
    coordinator, mock_lipro_api_client
) -> None:
    coordinator._state.devices = {"dev1": _make_device("dev1")}
    mock_lipro_api_client.get_mqtt_config.return_value = {
        "accessKey": "enc-ak",
        "secretKey": "enc-sk",
    }

    with patch(
        "custom_components.lipro.core.coordinator.mqtt_lifecycle.decrypt_mqtt_credential",
        side_effect=RuntimeError("boom"),
    ):
        assert await coordinator.async_setup_mqtt() is False


@pytest.mark.asyncio
async def test_coordinator_mqtt_service_sync_and_stop_use_transport_runtime(
    coordinator,
) -> None:
    mock_mqtt_runtime = AsyncMock()
    mock_mqtt_runtime.is_connected = True
    mock_mqtt_runtime.sync_subscriptions = AsyncMock(return_value=True)
    mock_mqtt_runtime.disconnect = AsyncMock()
    object.__setattr__(coordinator._runtimes, "mqtt", mock_mqtt_runtime)
    coordinator._state.devices = {
        "dev_a": _make_device("dev_a"),
        "mesh_group_1": _make_device("mesh_group_1", is_group=True),
    }

    coordinator._runtimes.mqtt.has_transport = True

    await coordinator.mqtt_service.async_sync_subscriptions()
    mock_mqtt_runtime.sync_subscriptions.assert_awaited_once_with(["mesh_group_1"])

    await coordinator.mqtt_service.async_stop()
    mock_mqtt_runtime.disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_setup_mqtt_message_callback_bridges_to_runtime_and_coordinator(
    coordinator,
    mock_lipro_api_client,
) -> None:
    device = _make_device("mesh_group_1", is_group=True)
    coordinator._state.devices = {device.serial: device}
    coordinator._runtimes.state.get_device_by_id = MagicMock(return_value=device)
    coordinator._runtimes.state.apply_properties_update = AsyncMock(return_value=True)
    coordinator.async_set_updated_data = MagicMock()
    mock_lipro_api_client.get_mqtt_config.return_value = {
        "accessKey": "enc-ak",
        "secretKey": "enc-sk",
    }

    mock_lipro_api_client.build_mqtt_facade = MagicMock(
        side_effect=lambda **kwargs: _FakeMqttFacade(**kwargs)
    )

    with (
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.decrypt_mqtt_credential",
            side_effect=["ak", "sk"],
        ),
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.resolve_mqtt_biz_id",
            return_value="biz001",
        ),
    ):
        ok = await coordinator.async_setup_mqtt()

    assert ok is True
    mqtt_facade = coordinator._runtimes.mqtt._mqtt_transport
    assert mqtt_facade is not None
    assert isinstance(mqtt_facade, LiproMqttFacade)
    assert isinstance(mqtt_facade, _FakeMqttFacade)

    mqtt_facade.emit_message(device.serial, {"connectState": "1"})
    await asyncio.gather(*tuple(coordinator._state.background_task_manager.tasks))

    coordinator._runtimes.state.apply_properties_update.assert_awaited_once_with(
        device,
        {"connectState": "1"},
        source="mqtt",
    )
    assert coordinator.async_set_updated_data.call_args.args == (
        coordinator._state.devices,
    )
    assert not coordinator._state.background_task_manager.tasks


@pytest.mark.asyncio
async def test_async_setup_mqtt_message_callback_records_bridge_failures(
    coordinator,
    mock_lipro_api_client,
) -> None:
    device = _make_device("mesh_group_1", is_group=True)
    coordinator._state.devices = {device.serial: device}
    coordinator._runtimes.state.get_device_by_id = MagicMock(return_value=device)
    coordinator._runtimes.state.apply_properties_update = AsyncMock(
        side_effect=RuntimeError("bridge boom")
    )
    coordinator.async_set_updated_data = MagicMock()
    mock_lipro_api_client.get_mqtt_config.return_value = {
        "accessKey": "enc-ak",
        "secretKey": "enc-sk",
    }

    mock_lipro_api_client.build_mqtt_facade = MagicMock(
        side_effect=lambda **kwargs: _FakeMqttFacade(**kwargs)
    )

    with (
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.decrypt_mqtt_credential",
            side_effect=["ak", "sk"],
        ),
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.resolve_mqtt_biz_id",
            return_value="biz001",
        ),
    ):
        ok = await coordinator.async_setup_mqtt()

    assert ok is True
    mqtt_facade = coordinator._runtimes.mqtt._mqtt_transport
    assert mqtt_facade is not None
    assert isinstance(mqtt_facade, _FakeMqttFacade)

    mqtt_facade.emit_message(device.serial, {"connectState": "1"})
    await asyncio.gather(
        *tuple(coordinator._state.background_task_manager.tasks),
        return_exceptions=True,
    )

    metrics = coordinator._runtimes.mqtt.get_runtime_metrics()
    assert metrics["last_transport_error_stage"] == "message_bridge"
    assert metrics["failure_summary"]["error_type"] == "RuntimeError"
    coordinator.async_set_updated_data.assert_not_called()


@pytest.mark.asyncio
async def test_async_setup_mqtt_facade_callbacks_drive_runtime_connection_state(
    coordinator,
    mock_lipro_api_client,
) -> None:
    coordinator._state.devices = {
        "mesh_group_1": _make_device("mesh_group_1", is_group=True)
    }
    mock_lipro_api_client.get_mqtt_config.return_value = {
        "accessKey": "enc-ak",
        "secretKey": "enc-sk",
    }

    mock_lipro_api_client.build_mqtt_facade = MagicMock(
        side_effect=lambda **kwargs: _FakeMqttFacade(**kwargs)
    )

    with (
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.decrypt_mqtt_credential",
            side_effect=["ak", "sk"],
        ),
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.resolve_mqtt_biz_id",
            return_value="biz001",
        ),
    ):
        ok = await coordinator.async_setup_mqtt()

    assert ok is True
    mqtt_facade = coordinator._runtimes.mqtt._mqtt_transport
    assert mqtt_facade is not None
    assert isinstance(mqtt_facade, LiproMqttFacade)
    assert isinstance(mqtt_facade, _FakeMqttFacade)
    assert coordinator._runtimes.mqtt is not None
    assert coordinator._runtimes.mqtt.is_connected

    mqtt_facade.emit_disconnect()
    assert coordinator._runtimes.mqtt is not None
    assert not coordinator._runtimes.mqtt.is_connected

    mqtt_facade.emit_connect()
    assert coordinator._runtimes.mqtt is not None
    assert coordinator._runtimes.mqtt.is_connected
