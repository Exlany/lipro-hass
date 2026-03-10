"""Integration tests for coordinator MQTT wiring with the refactored client."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.core.mqtt.client import LiproMqttClient
from custom_components.lipro.core.mqtt.connection_manager import MqttConnectionManager
from custom_components.lipro.core.mqtt.message_processor import MqttMessageProcessor
from custom_components.lipro.core.mqtt.topic_builder import MqttTopicBuilder

_CONFIG_ENTRY_DATA = {
    "phone": "13800000000",
    "password_hash": "e10adc3949ba59abbe56e057f20f883e",
    "phone_id": "test-phone-id",
    "access_token": "test_token",
    "refresh_token": "test_refresh",
    "user_id": 10001,
}


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
        "custom_components.lipro.core.coordinator.state.get_anonymous_share_manager"
    ) as mock_share:
        mock_share.return_value = MagicMock(is_enabled=False, set_enabled=MagicMock())
        from custom_components.lipro.core.coordinator import LiproDataUpdateCoordinator

        return LiproDataUpdateCoordinator(
            hass, mock_lipro_api_client, mock_auth_manager, entry
        )


@pytest.mark.asyncio
async def test_async_setup_mqtt_builds_refactored_client(
    coordinator, mock_lipro_api_client
) -> None:
    coordinator._devices = {
        "dev1": _make_device("dev1"),
        "mesh_group_1": _make_device("mesh_group_1", is_group=True),
    }
    mock_lipro_api_client.get_mqtt_config.return_value = {
        "accessKey": "enc-ak",
        "secretKey": "enc-sk",
    }

    with (
        patch(
            "custom_components.lipro.core.mqtt.credentials.decrypt_mqtt_credential",
            side_effect=["ak", "sk"],
        ),
        patch.object(LiproMqttClient, "start", new_callable=AsyncMock) as mock_start,
    ):
        ok = await coordinator.async_setup_mqtt()

    assert ok is True
    assert isinstance(coordinator._mqtt_client, LiproMqttClient)
    assert isinstance(coordinator._mqtt_client._topic_builder, MqttTopicBuilder)
    assert isinstance(
        coordinator._mqtt_client._connection_manager,
        MqttConnectionManager,
    )
    assert isinstance(
        coordinator._mqtt_client._message_processor,
        MqttMessageProcessor,
    )
    assert mock_start.await_args is not None
    assert mock_start.await_args.args == (["mesh_group_1"],)


@pytest.mark.asyncio
async def test_coordinator_mqtt_service_sync_and_stop_use_client_runtime(
    coordinator,
) -> None:
    mqtt_client = LiproMqttClient(
        access_key="access",
        secret_key="secret",
        biz_id="biz001",
        phone_id="test-phone-id",
    )
    sync_mock = AsyncMock()
    stop_mock = AsyncMock()
    coordinator._mqtt_client = mqtt_client
    coordinator._mqtt_connected = True
    coordinator._devices = {
        "dev_a": _make_device("dev_a"),
        "mesh_group_1": _make_device("mesh_group_1", is_group=True),
    }

    with (
        patch.object(mqtt_client, "sync_subscriptions", sync_mock),
        patch.object(mqtt_client, "stop", stop_mock),
    ):
        await coordinator.async_sync_mqtt_subscriptions()
        await coordinator.async_stop_mqtt()

    sync_mock.assert_awaited_once_with({"dev_a", "mesh_group_1"})
    stop_mock.assert_awaited_once_with()
    assert coordinator._mqtt_client is None
    assert coordinator._mqtt_connected is False
