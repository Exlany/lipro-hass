"""MQTT lifecycle management for coordinator."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from ...const.config import CONF_PHONE_ID
from ..mqtt.credentials import decrypt_mqtt_credential
from ..protocol import LiproMqttFacade, LiproProtocolFacade
from .mqtt.setup import build_mqtt_subscription_device_ids, resolve_mqtt_biz_id

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from ..device import LiproDevice
    from ..utils.background_task_manager import BackgroundTaskManager
    from .runtime.mqtt_runtime import MqttRuntime
    from .types import PropertyDict

_LOGGER = logging.getLogger(__name__)


async def _teardown_failed_mqtt_setup(
    *,
    protocol: LiproProtocolFacade,
    mqtt_runtime: MqttRuntime,
    mqtt_client: LiproMqttFacade | None,
) -> None:
    """Detach a partially constructed MQTT transport after setup failure."""
    if mqtt_client is not None:
        try:
            await mqtt_runtime.disconnect()
        except asyncio.CancelledError:
            raise
        except (RuntimeError, OSError, TimeoutError) as err:
            _LOGGER.debug(
                "Ignore MQTT teardown error after setup failure (%s)",
                type(err).__name__,
            )
    mqtt_runtime.detach_transport()
    protocol.attach_mqtt_facade(None)


async def async_setup_mqtt(
    *,
    protocol: LiproProtocolFacade,
    config_entry: ConfigEntry,
    background_task_manager: BackgroundTaskManager,
    devices: dict[str, LiproDevice],
    mqtt_runtime: MqttRuntime,
) -> tuple[LiproMqttFacade, str] | None:
    """Create and bind one protocol-owned MQTT façade to the existing runtime."""
    mqtt_client: LiproMqttFacade | None = None

    try:
        try:
            async with asyncio.timeout(10):
                mqtt_config = await protocol.get_mqtt_config()
        except TimeoutError:
            mqtt_runtime.handle_transport_error(
                TimeoutError("mqtt_config_timeout"),
                stage="config_fetch",
            )
            _LOGGER.error("MQTT config fetch timeout after 10 seconds")
            return None

        access_key = decrypt_mqtt_credential(mqtt_config.get("accessKey", ""))
        secret_key = decrypt_mqtt_credential(mqtt_config.get("secretKey", ""))
        if not access_key or not secret_key:
            _LOGGER.warning("Failed to decrypt MQTT credentials")
            return None

        biz_id = resolve_mqtt_biz_id(config_entry.data)
        if biz_id is None:
            _LOGGER.warning("No biz_id available for MQTT")
            return None

        device_ids = build_mqtt_subscription_device_ids(devices)
        if not device_ids:
            _LOGGER.warning("No valid device IDs available for MQTT subscriptions")
            return None

        phone_id = config_entry.data.get(CONF_PHONE_ID, "")

        async def _async_handle_message(
            topic: str,
            payload: PropertyDict,
        ) -> None:
            try:
                await mqtt_runtime.handle_message(topic, payload)
            except asyncio.CancelledError:
                raise
            except Exception as err:
                mqtt_runtime.handle_transport_error(err, stage="message_bridge")
                raise

        def _on_message_bridge(topic: str, payload: PropertyDict) -> None:
            background_task_manager.create(
                _async_handle_message(topic, payload),
                create_task=lambda coro: asyncio.create_task(
                    coro,
                    name=f"mqtt_message_{topic}",
                ),
            )

        mqtt_client = protocol.build_mqtt_facade(
            access_key=access_key,
            secret_key=secret_key,
            biz_id=biz_id,
            phone_id=phone_id,
            on_message=_on_message_bridge,
            on_connect=mqtt_runtime.on_transport_connected,
            on_disconnect=mqtt_runtime.on_transport_disconnected,
            on_error=mqtt_runtime.handle_transport_error,
        )
        mqtt_runtime.bind_transport(mqtt_client)

        try:
            async with asyncio.timeout(15):
                connected = await mqtt_runtime.connect(device_ids=device_ids)
        except TimeoutError:
            mqtt_runtime.handle_transport_error(
                TimeoutError("mqtt_connect_timeout"),
                stage="connect",
            )
            _LOGGER.error("MQTT connection timeout after 15 seconds")
            await _teardown_failed_mqtt_setup(
                protocol=protocol,
                mqtt_runtime=mqtt_runtime,
                mqtt_client=mqtt_client,
            )
            return None

        if not connected or not mqtt_runtime.is_connected:
            _LOGGER.warning("MQTT client not connected after setup")
            await _teardown_failed_mqtt_setup(
                protocol=protocol,
                mqtt_runtime=mqtt_runtime,
                mqtt_client=mqtt_client,
            )
            return None

        return (mqtt_client, biz_id)

    except asyncio.CancelledError:
        raise
    except Exception as err:
        mqtt_runtime.handle_transport_error(err, stage="setup")
        await _teardown_failed_mqtt_setup(
            protocol=protocol,
            mqtt_runtime=mqtt_runtime,
            mqtt_client=mqtt_client,
        )
        _LOGGER.exception("Failed to setup MQTT")
        return None


__all__ = ["async_setup_mqtt"]
