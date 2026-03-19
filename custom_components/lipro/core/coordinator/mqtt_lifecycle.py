"""MQTT lifecycle management for coordinator."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from ...const.config import CONF_PHONE_ID
from ..api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from ..mqtt.credentials import decrypt_mqtt_credential
from ..protocol import LiproMqttFacade, LiproProtocolFacade
from ..protocol.contracts import CanonicalMqttConfig
from ..protocol.mqtt_facade import MqttMessageCallback
from .mqtt.setup import build_mqtt_subscription_device_ids, resolve_mqtt_biz_id

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from ..device import LiproDevice
    from ..utils.background_task_manager import BackgroundTaskManager
    from .runtime.mqtt_runtime import MqttRuntime
    from .types import PropertyDict

_LOGGER = logging.getLogger(__name__)
_MQTT_CONFIG_TIMEOUT_SECONDS = 10
_MQTT_CONNECT_TIMEOUT_SECONDS = 15


async def _teardown_failed_mqtt_setup(
    *,
    protocol: LiproProtocolFacade,
    mqtt_runtime: MqttRuntime,
    mqtt_facade: LiproMqttFacade | None,
) -> None:
    """Detach a partially constructed MQTT transport after setup failure."""
    if mqtt_facade is not None:
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


async def _async_fetch_mqtt_config(
    *,
    protocol: LiproProtocolFacade,
    mqtt_runtime: MqttRuntime,
) -> CanonicalMqttConfig | None:
    """Fetch MQTT config under an explicit timeout budget."""
    try:
        async with asyncio.timeout(_MQTT_CONFIG_TIMEOUT_SECONDS):
            return await protocol.get_mqtt_config()
    except TimeoutError:
        mqtt_runtime.handle_transport_error(
            TimeoutError("mqtt_config_timeout"),
            stage="config_fetch",
        )
        _LOGGER.error(
            "MQTT config fetch timeout after %d seconds",
            _MQTT_CONFIG_TIMEOUT_SECONDS,
        )
        return None


def _resolve_mqtt_credentials(
    mqtt_config: CanonicalMqttConfig,
) -> tuple[str, str] | None:
    """Decrypt MQTT credentials and require both access/secret keys."""
    access_key = decrypt_mqtt_credential(str(mqtt_config.get("accessKey", "")))
    secret_key = decrypt_mqtt_credential(str(mqtt_config.get("secretKey", "")))
    if not access_key or not secret_key:
        _LOGGER.warning("Failed to decrypt MQTT credentials")
        return None
    return access_key, secret_key


def _resolve_subscription_device_ids(
    devices: dict[str, LiproDevice],
) -> list[str] | None:
    """Resolve MQTT subscription IDs and require at least one valid target."""
    device_ids = build_mqtt_subscription_device_ids(devices)
    if device_ids:
        return device_ids
    _LOGGER.warning("No valid device IDs available for MQTT subscriptions")
    return None


def _build_message_bridge(
    *,
    background_task_manager: BackgroundTaskManager,
    mqtt_runtime: MqttRuntime,
) -> MqttMessageCallback:
    """Build the runtime-owned MQTT message bridge callback."""

    async def _async_handle_message(
        topic: str,
        payload: PropertyDict,
    ) -> None:
        try:
            await mqtt_runtime.handle_message(topic, payload)
        except asyncio.CancelledError:
            raise
        except (RuntimeError, ValueError, TypeError, LookupError) as err:
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

    return _on_message_bridge


def _bind_mqtt_transport(
    *,
    protocol: LiproProtocolFacade,
    mqtt_runtime: MqttRuntime,
    background_task_manager: BackgroundTaskManager,
    access_key: str,
    secret_key: str,
    biz_id: str,
    phone_id: str,
) -> LiproMqttFacade:
    """Build and bind the active protocol-owned MQTT child façade."""
    mqtt_facade = protocol.build_mqtt_facade(
        access_key=access_key,
        secret_key=secret_key,
        biz_id=biz_id,
        phone_id=phone_id,
        on_message=_build_message_bridge(
            background_task_manager=background_task_manager,
            mqtt_runtime=mqtt_runtime,
        ),
        on_connect=mqtt_runtime.on_transport_connected,
        on_disconnect=mqtt_runtime.on_transport_disconnected,
        on_error=mqtt_runtime.handle_transport_error,
    )
    mqtt_runtime.bind_transport(mqtt_facade)
    return mqtt_facade


async def _async_connect_bound_mqtt_transport(
    *,
    protocol: LiproProtocolFacade,
    mqtt_runtime: MqttRuntime,
    mqtt_facade: LiproMqttFacade,
    device_ids: list[str],
) -> bool:
    """Connect a bound MQTT transport under the setup timeout budget."""
    try:
        async with asyncio.timeout(_MQTT_CONNECT_TIMEOUT_SECONDS):
            connected = await mqtt_runtime.connect(device_ids=device_ids)
    except TimeoutError:
        mqtt_runtime.handle_transport_error(
            TimeoutError("mqtt_connect_timeout"),
            stage="connect",
        )
        _LOGGER.error(
            "MQTT connection timeout after %d seconds",
            _MQTT_CONNECT_TIMEOUT_SECONDS,
        )
        await _teardown_failed_mqtt_setup(
            protocol=protocol,
            mqtt_runtime=mqtt_runtime,
            mqtt_facade=mqtt_facade,
        )
        return False

    if connected and mqtt_runtime.is_connected:
        return True

    _LOGGER.warning("MQTT transport not connected after setup")
    await _teardown_failed_mqtt_setup(
        protocol=protocol,
        mqtt_runtime=mqtt_runtime,
        mqtt_facade=mqtt_facade,
    )
    return False


async def async_setup_mqtt(
    *,
    protocol: LiproProtocolFacade,
    config_entry: ConfigEntry,
    background_task_manager: BackgroundTaskManager,
    devices: dict[str, LiproDevice],
    mqtt_runtime: MqttRuntime,
) -> tuple[LiproMqttFacade, str] | None:
    """Create and bind one protocol-owned MQTT façade to the existing runtime."""
    mqtt_facade: LiproMqttFacade | None = None

    try:
        mqtt_config = await _async_fetch_mqtt_config(
            protocol=protocol,
            mqtt_runtime=mqtt_runtime,
        )
        if mqtt_config is None:
            return None

        credentials = _resolve_mqtt_credentials(mqtt_config)
        if credentials is None:
            return None
        access_key, secret_key = credentials

        biz_id = resolve_mqtt_biz_id(config_entry.data)
        if biz_id is None:
            _LOGGER.warning("No biz_id available for MQTT")
            return None

        device_ids = _resolve_subscription_device_ids(devices)
        if device_ids is None:
            return None

        mqtt_facade = _bind_mqtt_transport(
            protocol=protocol,
            mqtt_runtime=mqtt_runtime,
            background_task_manager=background_task_manager,
            access_key=access_key,
            secret_key=secret_key,
            biz_id=biz_id,
            phone_id=str(config_entry.data.get(CONF_PHONE_ID, "")),
        )
        if not await _async_connect_bound_mqtt_transport(
            protocol=protocol,
            mqtt_runtime=mqtt_runtime,
            mqtt_facade=mqtt_facade,
            device_ids=device_ids,
        ):
            return None
        return mqtt_facade, biz_id

    except asyncio.CancelledError:
        raise
    except (
        LiproRefreshTokenExpiredError,
        LiproAuthError,
        LiproConnectionError,
        LiproApiError,
        RuntimeError,
        ValueError,
        TypeError,
        LookupError,
    ) as err:
        mqtt_runtime.handle_transport_error(err, stage="setup")
        await _teardown_failed_mqtt_setup(
            protocol=protocol,
            mqtt_runtime=mqtt_runtime,
            mqtt_facade=mqtt_facade,
        )
        _LOGGER.exception("Failed to setup MQTT")
        return None


__all__ = ["async_setup_mqtt"]
