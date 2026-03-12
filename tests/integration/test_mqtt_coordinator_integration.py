"""Integration tests for coordinator MQTT wiring with the refactored client."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN

_CONFIG_ENTRY_DATA = {
    "phone": "13800000000",
    "password_hash": "e10adc3949ba59abbe56e057f20f883e",
    "phone_id": "test-phone-id",
    "access_token": "test_token",
    "refresh_token": "test_refresh",
    "user_id": 10001,
}


class _FakeMqttClient:
    """Capture lifecycle callbacks while emulating a connected MQTT client."""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        biz_id: str,
        phone_id: str,
        on_message=None,
        on_connect=None,
        on_disconnect=None,
        on_error=None,
    ) -> None:
        self.access_key = access_key
        self.secret_key = secret_key
        self.biz_id = biz_id
        self.phone_id = phone_id
        self.on_message = on_message
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_error = on_error
        self.start = AsyncMock()
        self.stop = AsyncMock()
        self.sync_subscriptions = AsyncMock()
        self.wait_until_connected = AsyncMock(side_effect=self._wait_until_connected)

    async def _wait_until_connected(self) -> bool:
        if self.on_connect is not None:
            self.on_connect()
        return True


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
        from custom_components.lipro.core.coordinator.coordinator import Coordinator

        return Coordinator(
            hass, mock_lipro_api_client, mock_auth_manager, entry
        )


@pytest.mark.asyncio
async def test_async_setup_mqtt_builds_refactored_client(
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
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.MqttRuntime"
        ) as mock_runtime_cls,
    ):
        mock_client = MagicMock()
        mock_lipro_api_client.build_mqtt_facade = MagicMock(return_value=mock_client)

        mock_runtime = MagicMock()
        mock_runtime.is_connected = True
        mock_runtime.connect = AsyncMock(return_value=True)
        mock_runtime.set_polling_updater = MagicMock()
        mock_runtime_cls.return_value = mock_runtime

        ok = await coordinator.mqtt_service.async_setup()

    assert ok is True
    assert coordinator._runtimes.mqtt is not None
    mock_runtime.connect.assert_awaited_once()
    mock_runtime.set_polling_updater.assert_called_once_with(coordinator)
    mqtt_client_kwargs = mock_lipro_api_client.build_mqtt_facade.call_args.kwargs
    assert callable(mqtt_client_kwargs["on_message"])
    assert callable(mqtt_client_kwargs["on_connect"])
    assert callable(mqtt_client_kwargs["on_disconnect"])
    assert callable(mqtt_client_kwargs["on_error"])


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
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.MqttRuntime"
        ) as mock_runtime_cls,
    ):
        mock_runtime = MagicMock()
        mock_runtime.is_connected = True
        mock_runtime.connect = AsyncMock(side_effect=TimeoutError())
        mock_runtime.disconnect = AsyncMock()
        mock_runtime_cls.return_value = mock_runtime

        ok = await coordinator.async_setup_mqtt()

    assert ok is False
    mock_runtime.connect.assert_awaited_once()
    mock_runtime.disconnect.assert_awaited_once()


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
        patch(
            "custom_components.lipro.core.coordinator.mqtt_lifecycle.MqttRuntime"
        ) as mock_runtime_cls,
    ):
        mock_runtime = MagicMock()
        mock_runtime.is_connected = False
        mock_runtime.connect = AsyncMock(return_value=False)
        mock_runtime.disconnect = AsyncMock()
        mock_runtime_cls.return_value = mock_runtime

        ok = await coordinator.async_setup_mqtt()

    assert ok is False
    mock_runtime.connect.assert_awaited_once()
    mock_runtime.disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_setup_mqtt_reraises_cancelled_error(
    coordinator, mock_lipro_api_client
) -> None:
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
async def test_coordinator_mqtt_service_sync_and_stop_use_client_runtime(
    coordinator,
) -> None:
    mock_mqtt_runtime = AsyncMock()
    mock_mqtt_runtime.is_connected = True
    mock_mqtt_runtime.sync_subscriptions = AsyncMock(return_value=True)
    mock_mqtt_runtime.disconnect = AsyncMock()
    object.__setattr__(coordinator._runtimes, "mqtt", mock_mqtt_runtime)
    coordinator._state.biz_id = "biz001"
    coordinator._state.devices = {
        "dev_a": _make_device("dev_a"),
        "mesh_group_1": _make_device("mesh_group_1", is_group=True),
    }

    mock_client = AsyncMock()
    coordinator._state.mqtt_client = mock_client

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
        side_effect=lambda **kwargs: _FakeMqttClient(**kwargs)
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
    mqtt_client = coordinator.mqtt_client
    assert mqtt_client is not None
    raw_client = getattr(mqtt_client, "raw_client", mqtt_client)
    assert isinstance(raw_client, _FakeMqttClient)

    assert raw_client.on_message is not None
    raw_client.on_message(device.serial, {"connectState": "1"})
    await asyncio.gather(*tuple(coordinator.background_task_manager.tasks))

    coordinator._runtimes.state.apply_properties_update.assert_awaited_once_with(
        device,
        {"connectState": "1"},
        source="mqtt",
    )
    coordinator.async_set_updated_data.assert_called_with(coordinator.devices)
    assert not coordinator.background_task_manager.tasks


@pytest.mark.asyncio
async def test_async_setup_mqtt_client_callbacks_drive_runtime_connection_state(
    coordinator,
    mock_lipro_api_client,
) -> None:
    coordinator._state.devices = {"mesh_group_1": _make_device("mesh_group_1", is_group=True)}
    mock_lipro_api_client.get_mqtt_config.return_value = {
        "accessKey": "enc-ak",
        "secretKey": "enc-sk",
    }

    mock_lipro_api_client.build_mqtt_facade = MagicMock(
        side_effect=lambda **kwargs: _FakeMqttClient(**kwargs)
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
    mqtt_client = coordinator.mqtt_client
    assert mqtt_client is not None
    raw_client = getattr(mqtt_client, "raw_client", mqtt_client)
    assert isinstance(raw_client, _FakeMqttClient)
    assert coordinator.mqtt_runtime is not None
    assert coordinator.mqtt_runtime.is_connected

    assert raw_client.on_disconnect is not None
    raw_client.on_disconnect()
    assert coordinator.mqtt_runtime is not None
    assert not coordinator.mqtt_runtime.is_connected

    on_connect = raw_client.on_connect
    assert on_connect is not None
    on_connect()
    assert coordinator.mqtt_runtime is not None
    assert coordinator.mqtt_runtime.is_connected
