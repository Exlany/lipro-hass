"""Device filter configuration and evaluation logic."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
import json
import logging
import re
from typing import Any

from custom_components.lipro.const.config import (
    CONF_DEVICE_FILTER_DID_LIST,
    CONF_DEVICE_FILTER_DID_MODE,
    CONF_DEVICE_FILTER_HOME_LIST,
    CONF_DEVICE_FILTER_HOME_MODE,
    CONF_DEVICE_FILTER_MODEL_LIST,
    CONF_DEVICE_FILTER_MODEL_MODE,
    CONF_DEVICE_FILTER_SSID_LIST,
    CONF_DEVICE_FILTER_SSID_MODE,
    DEVICE_FILTER_MODE_EXCLUDE,
    DEVICE_FILTER_MODE_INCLUDE,
    DEVICE_FILTER_MODE_OFF,
    MAX_DEVICE_FILTER_LIST_CHARS,
    MAX_DEVICE_FILTER_LIST_ITEMS,
)

from ...types import PropertyDict, PropertyValue

_LOGGER = logging.getLogger(__name__)
_FILTER_LIST_SPLIT_RE = re.compile(r"[\n,;]+")
_VALID_FILTER_MODES = frozenset(
    {
        DEVICE_FILTER_MODE_OFF,
        DEVICE_FILTER_MODE_INCLUDE,
        DEVICE_FILTER_MODE_EXCLUDE,
    }
)


@dataclass(frozen=True)
class DeviceFilterRule:
    """One dimension of device filter configuration."""

    mode: str = DEVICE_FILTER_MODE_OFF
    values: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class DeviceFilterConfig:
    """Device filter configuration for home/model/ssid/did dimensions."""

    home: DeviceFilterRule = field(default_factory=DeviceFilterRule)
    model: DeviceFilterRule = field(default_factory=DeviceFilterRule)
    ssid: DeviceFilterRule = field(default_factory=DeviceFilterRule)
    did: DeviceFilterRule = field(default_factory=DeviceFilterRule)


class DeviceFilter:
    """Evaluates device inclusion based on filter configuration."""

    def __init__(self, *, config: DeviceFilterConfig) -> None:
        """Initialize device filter.

        Args:
            config: Filter configuration with rules for each dimension
        """
        self._config = config

    def is_device_included(self, device_data: Mapping[str, PropertyValue]) -> bool:
        """Check if device passes all filter rules.

        Args:
            device_data: Raw API device data dict

        Returns:
            True if device should be included, False if filtered out
        """
        if not self._has_active_filter():
            return True

        for rule, extractor in (
            (self._config.home, _extract_home_values),
            (self._config.model, _extract_model_values),
            (self._config.ssid, _collect_ssid_values),
            (self._config.did, _extract_did_values),
        ):
            if rule.mode == DEVICE_FILTER_MODE_OFF:
                continue
            if not rule.values:
                if rule.mode == DEVICE_FILTER_MODE_INCLUDE:
                    return False
                continue
            if not self._rule_allows_values(rule, extractor(device_data)):
                return False
        return True

    def _has_active_filter(self) -> bool:
        """Check if any filter rule is enabled."""
        return any(
            rule.mode != DEVICE_FILTER_MODE_OFF
            for rule in (
                self._config.home,
                self._config.model,
                self._config.ssid,
                self._config.did,
            )
        )

    def _rule_allows_values(self, rule: DeviceFilterRule, values: set[str]) -> bool:
        """Apply include/exclude/off rule semantics to extracted values."""
        if rule.mode == DEVICE_FILTER_MODE_OFF:
            return True

        has_match = bool(values & rule.values)
        if rule.mode == DEVICE_FILTER_MODE_INCLUDE:
            return has_match
        if rule.mode == DEVICE_FILTER_MODE_EXCLUDE:
            return not has_match
        return True


def _normalize_filter_value(value: Any) -> str | None:
    """Normalize a filter value to lowercase string or None."""
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped.lower() if stripped else None
    return str(value).strip().lower() or None


def _collect_normalized_values(
    payload: Mapping[str, Any],
    keys: tuple[str, ...],
) -> set[str]:
    """Collect normalized values from a mapping by candidate keys."""
    values: set[str] = set()
    for key in keys:
        normalized = _normalize_filter_value(payload.get(key))
        if normalized is not None:
            values.add(normalized)
    return values


def _collect_property_values(
    properties: Any,
    keys: tuple[str, ...],
) -> set[str]:
    """Collect normalized values from property payload variants."""
    key_set = set(keys)
    if isinstance(properties, Mapping):
        return _collect_normalized_values(properties, keys)

    values: set[str] = set()
    if not isinstance(properties, list):
        return values

    for item in properties:
        if not isinstance(item, Mapping):
            continue
        item_key = item.get("key")
        if item_key not in key_set:
            continue
        normalized = _normalize_filter_value(item.get("value"))
        if normalized is not None:
            values.add(normalized)
    return values


def _collect_ssid_values(device_data: Mapping[str, Any]) -> set[str]:
    """Collect SSID candidates from multiple payload variants."""
    ssid_keys = ("wifi_ssid", "wifiSsid", "ssid")
    values = _collect_normalized_values(device_data, ssid_keys)
    values.update(_collect_property_values(device_data.get("properties"), ssid_keys))

    device_info = device_data.get("deviceInfo")
    if isinstance(device_info, Mapping):
        values.update(_collect_normalized_values(device_info, ssid_keys))
        return values
    if not isinstance(device_info, str):
        return values

    stripped = device_info.lstrip()
    if not stripped or stripped[0] not in "{[":
        return values

    try:
        decoded = json.loads(device_info)
    except (TypeError, ValueError):
        return values
    if isinstance(decoded, Mapping):
        values.update(_collect_normalized_values(decoded, ssid_keys))
    return values


def _extract_home_values(device_data: Mapping[str, Any]) -> set[str]:
    """Extract normalized home candidates from device payload."""
    return _collect_normalized_values(
        device_data,
        (
            "homeName",
            "home_name",
            "home",
            "homeId",
            "home_id",
            "roomName",
            "room_name",
        ),
    )


def _extract_model_values(device_data: Mapping[str, Any]) -> set[str]:
    """Extract normalized model candidates from device payload."""
    return _collect_normalized_values(
        device_data,
        (
            "model",
            "physicalModel",
            "physical_model",
            "productModel",
            "product_model",
            "iotName",
            "iot_name",
        ),
    )


def _extract_did_values(device_data: Mapping[str, Any]) -> set[str]:
    """Extract normalized did/device-id candidates from device payload."""
    return _collect_normalized_values(
        device_data,
        (
            "did",
            "deviceDid",
            "device_did",
            "deviceId",
            "device_id",
            "iotDeviceId",
            "iot_device_id",
            "serial",
        ),
    )


def parse_filter_config(options: PropertyDict) -> DeviceFilterConfig:
    """Parse device filter configuration from config entry options.

    Args:
        options: Config entry options dict

    Returns:
        Parsed DeviceFilterConfig
    """
    return DeviceFilterConfig(
        home=_parse_filter_rule(
            mode=str(options.get(CONF_DEVICE_FILTER_HOME_MODE, DEVICE_FILTER_MODE_OFF)),
            list_str=str(options.get(CONF_DEVICE_FILTER_HOME_LIST, "")),
        ),
        model=_parse_filter_rule(
            mode=str(options.get(CONF_DEVICE_FILTER_MODEL_MODE, DEVICE_FILTER_MODE_OFF)),
            list_str=str(options.get(CONF_DEVICE_FILTER_MODEL_LIST, "")),
        ),
        ssid=_parse_filter_rule(
            mode=str(options.get(CONF_DEVICE_FILTER_SSID_MODE, DEVICE_FILTER_MODE_OFF)),
            list_str=str(options.get(CONF_DEVICE_FILTER_SSID_LIST, "")),
        ),
        did=_parse_filter_rule(
            mode=str(options.get(CONF_DEVICE_FILTER_DID_MODE, DEVICE_FILTER_MODE_OFF)),
            list_str=str(options.get(CONF_DEVICE_FILTER_DID_LIST, "")),
        ),
    )


def _parse_filter_rule(*, mode: str, list_str: str) -> DeviceFilterRule:
    """Parse single filter rule from mode and list string.

    Args:
        mode: Filter mode (off/include/exclude)
        list_str: Comma/newline separated list of values

    Returns:
        Parsed DeviceFilterRule
    """
    if mode not in _VALID_FILTER_MODES:
        _LOGGER.warning("Invalid filter mode '%s', using OFF", mode)
        mode = DEVICE_FILTER_MODE_OFF

    if mode == DEVICE_FILTER_MODE_OFF:
        return DeviceFilterRule(mode=mode, values=frozenset())

    # Parse and validate list
    list_str = list_str[:MAX_DEVICE_FILTER_LIST_CHARS]
    items = [
        item.strip() for item in _FILTER_LIST_SPLIT_RE.split(list_str) if item.strip()
    ]
    items = items[:MAX_DEVICE_FILTER_LIST_ITEMS]

    # Normalize to lowercase
    normalized_items = [item.lower() for item in items]

    return DeviceFilterRule(mode=mode, values=frozenset(normalized_items))


__all__ = [
    "DeviceFilter",
    "DeviceFilterConfig",
    "DeviceFilterRule",
    "parse_filter_config",
]
