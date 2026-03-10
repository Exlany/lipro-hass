"""Integration tests for coordinator MQTT wiring with the refactored client."""

from __future__ import annotations

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
            "custom_components.lipro.core.coordinator.coordinator.decrypt_mqtt_credential",
            side_effect=["ak", "sk"],
        ),
        patch(
            "custom_components.lipro.core.mqtt.mqtt_client.LiproMqttClient"
        ) as mock_client_cls,
        patch(
            "custom_components.lipro.core.coordinator.coordinator.MqttRuntime"
        ) as mock_runtime_cls,
    ):
        mock_client = AsyncMock()
        mock_client_cls.return_value = mock_client

        mock_runtime = MagicMock()
        mock_runtime.is_connected = True
        mock_runtime.connect = AsyncMock()
        mock_runtime_cls.return_value = mock_runtime

        ok = await coordinator.mqtt_service.async_setup()

    assert ok is True
    assert coordinator._mqtt_runtime is not None
    mock_runtime.connect.assert_awaited_once()


@pytest.mark.asyncio
async def test_coordinator_mqtt_service_sync_and_stop_use_client_runtime(
    coordinator,
) -> None:
    # Mock MQTT runtime
    mock_mqtt_runtime = AsyncMock()
    mock_mqtt_runtime.is_connected = True
    mock_mqtt_runtime.connect = AsyncMock()
    mock_mqtt_runtime.disconnect = AsyncMock()
    coordinator._mqtt_runtime = mock_mqtt_runtime
    coordinator._biz_id = "biz001"
    coordinator._devices = {
        "dev_a": _make_device("dev_a"),
        "mesh_group_1": _make_device("mesh_group_1", is_group=True),
    }

    # Mock MQTT client
    mock_client = AsyncMock()
    coordinator._mqtt_client = mock_client

    # Test sync subscriptions
    await coordinator.mqtt_service.async_sync_subscriptions()
    mock_mqtt_runtime.connect.assert_awaited_once()

    # Test stop
    await coordinator.mqtt_service.async_stop()
    mock_mqtt_runtime.disconnect.assert_awaited_once()
