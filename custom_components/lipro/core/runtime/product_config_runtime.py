"""Runtime helpers for matching and applying product config overrides."""

from __future__ import annotations

import logging
from typing import Any

from ...const import MIN_COLOR_TEMP_KELVIN
from ..device import LiproDevice


def coerce_int_or_zero(value: Any) -> int:
    """Coerce mixed numeric payloads into int with safe fallback."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def index_product_configs(
    configs: list[dict[str, Any]],
) -> tuple[dict[int, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Create lookup maps by product ID and fwIotName."""
    configs_by_id: dict[int, dict[str, Any]] = {}
    configs_by_iot_name: dict[str, dict[str, Any]] = {}

    for config in configs:
        config_id = coerce_int_or_zero(config.get("id"))
        if config_id > 0:
            configs_by_id[config_id] = config

        fw_iot_name = config.get("fwIotName")
        if isinstance(fw_iot_name, str) and fw_iot_name:
            configs_by_iot_name[fw_iot_name.lower()] = config

    return configs_by_id, configs_by_iot_name


def match_product_config(
    device: LiproDevice,
    *,
    configs_by_id: dict[int, dict[str, Any]],
    configs_by_iot_name: dict[str, dict[str, Any]],
    logger: logging.Logger,
) -> dict[str, Any] | None:
    """Match one device to its best product config."""
    if device.product_id:
        matched = configs_by_id.get(device.product_id)
        if matched:
            logger.debug(
                "Device %s: matched config by productId=%d -> %s",
                device.name,
                device.product_id,
                matched.get("name"),
            )
            return matched

    if device.iot_name:
        matched = configs_by_iot_name.get(device.iot_name.lower())
        if matched:
            logger.debug(
                "Device %s: matched config by iotName=%s -> %s",
                device.name,
                device.iot_name,
                matched.get("name"),
            )
            return matched

    return None


def apply_product_config(
    device: LiproDevice,
    config: dict[str, Any],
    *,
    logger: logging.Logger,
) -> None:
    """Apply matched product-config overrides to runtime device model."""
    min_temp = coerce_int_or_zero(config.get("minTemperature", 0))
    max_temp = coerce_int_or_zero(config.get("maxTemperature", 0))
    max_fan_gear = coerce_int_or_zero(config.get("maxFanGear", 0))

    if max_temp > 0:
        device.min_color_temp_kelvin = min_temp or MIN_COLOR_TEMP_KELVIN
        device.max_color_temp_kelvin = max_temp
        logger.debug(
            "Device %s: color temp range %d-%d K",
            device.name,
            device.min_color_temp_kelvin,
            device.max_color_temp_kelvin,
        )
    elif max_temp == 0 and min_temp == 0:
        device.min_color_temp_kelvin = 0
        device.max_color_temp_kelvin = 0
        logger.debug(
            "Device %s: single color temperature (no adjustment)",
            device.name,
        )

    if max_fan_gear > 0:
        device.default_max_fan_gear_in_model = max_fan_gear
        device.max_fan_gear = max(device.max_fan_gear, max_fan_gear)
        logger.debug(
            "Device %s: fan gear baseline 1-%d, effective 1-%d",
            device.name,
            device.default_max_fan_gear_in_model,
            device.max_fan_gear,
        )
