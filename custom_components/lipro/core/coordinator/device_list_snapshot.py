"""Device list snapshot helpers for coordinator."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
import json
import logging
import re
from typing import Any

from ...const.categories import DeviceCategory
from ...const.config import (
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
from ..device.device import LiproDevice
from ..device.identity_index import register_identity_alias

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
class FetchedDeviceSnapshot:
    """Atomic container for refreshed device indexes."""

    devices: dict[str, LiproDevice]
    device_by_id: dict[str, LiproDevice]
    iot_ids: list[str]
    group_ids: list[str]
    outlet_ids: list[str]
    cloud_serials: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class StaleDeviceReconcilePlan:
    """Computed stale-device reconciliation result."""

    missing_cycles: dict[str, int]
    removable_serials: set[str]


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


def _normalize_filter_value(value: Any) -> str | None:
    """Normalize one filter candidate value for case-insensitive matching."""
    if value is None:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    return normalized.casefold()


def _normalize_filter_mode(value: Any) -> str:
    """Normalize raw mode option to one canonical filter mode."""
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in _VALID_FILTER_MODES:
            return normalized
    return DEVICE_FILTER_MODE_OFF


def _parse_filter_values(value: Any) -> frozenset[str]:
    """Parse list-like option value into normalized tokens."""
    if value is None:
        return frozenset()

    normalized: set[str] = set()

    def _add_candidate(candidate: Any) -> None:
        """Normalize candidate token and add to set if valid."""
        if len(normalized) >= MAX_DEVICE_FILTER_LIST_ITEMS:
            return
        normalized_value = _normalize_filter_value(candidate)
        if normalized_value is None:
            return
        normalized.add(normalized_value)

    def _add_text(text: str) -> None:
        """Split and add tokens from a raw text blob."""
        if len(text) > MAX_DEVICE_FILTER_LIST_CHARS:
            text = text[:MAX_DEVICE_FILTER_LIST_CHARS]
        for token in _FILTER_LIST_SPLIT_RE.split(text):
            _add_candidate(token)
            if len(normalized) >= MAX_DEVICE_FILTER_LIST_ITEMS:
                break

    if isinstance(value, str):
        _add_text(value)
        return frozenset(normalized)

    if isinstance(value, (list, tuple, set, frozenset)):
        for item in value:
            if len(normalized) >= MAX_DEVICE_FILTER_LIST_ITEMS:
                break
            if isinstance(item, str):
                _add_text(item)
                continue
            raw = str(item)
            if len(raw) > MAX_DEVICE_FILTER_LIST_CHARS:
                raw = raw[:MAX_DEVICE_FILTER_LIST_CHARS]
            _add_candidate(raw)
        return frozenset(normalized)

    raw = str(value)
    if len(raw) > MAX_DEVICE_FILTER_LIST_CHARS:
        raw = raw[:MAX_DEVICE_FILTER_LIST_CHARS]
    _add_candidate(raw)
    return frozenset(normalized)


def _build_filter_rule(mode_value: Any, list_value: Any) -> DeviceFilterRule:
    """Build a normalized filter rule from raw option values."""
    return DeviceFilterRule(
        mode=_normalize_filter_mode(mode_value),
        values=_parse_filter_values(list_value),
    )


def build_device_filter_config(options: Mapping[str, Any]) -> DeviceFilterConfig:
    """Build normalized device-filter config from entry options."""
    return DeviceFilterConfig(
        home=_build_filter_rule(
            options.get(CONF_DEVICE_FILTER_HOME_MODE),
            options.get(CONF_DEVICE_FILTER_HOME_LIST),
        ),
        model=_build_filter_rule(
            options.get(CONF_DEVICE_FILTER_MODEL_MODE),
            options.get(CONF_DEVICE_FILTER_MODEL_LIST),
        ),
        ssid=_build_filter_rule(
            options.get(CONF_DEVICE_FILTER_SSID_MODE),
            options.get(CONF_DEVICE_FILTER_SSID_LIST),
        ),
        did=_build_filter_rule(
            options.get(CONF_DEVICE_FILTER_DID_MODE),
            options.get(CONF_DEVICE_FILTER_DID_LIST),
        ),
    )


def has_active_device_filter(filter_config: DeviceFilterConfig) -> bool:
    """Return True when at least one filter rule is enabled."""
    return any(
        rule.mode != DEVICE_FILTER_MODE_OFF
        for rule in (
            filter_config.home,
            filter_config.model,
            filter_config.ssid,
            filter_config.did,
        )
    )


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


def _rule_allows_values(rule: DeviceFilterRule, values: set[str]) -> bool:
    """Apply include/exclude/off rule semantics to extracted values."""
    if rule.mode == DEVICE_FILTER_MODE_OFF:
        return True

    has_match = bool(values & rule.values)
    if rule.mode == DEVICE_FILTER_MODE_INCLUDE:
        return has_match
    if rule.mode == DEVICE_FILTER_MODE_EXCLUDE:
        return not has_match
    return True


def is_device_included_by_filter(
    device_data: Mapping[str, Any],
    filter_config: DeviceFilterConfig,
) -> bool:
    """Return True when a device row passes all configured filter rules."""
    if not has_active_device_filter(filter_config):
        return True

    for rule, extractor in (
        (filter_config.home, _extract_home_values),
        (filter_config.model, _extract_model_values),
        (filter_config.ssid, _collect_ssid_values),
        (filter_config.did, _extract_did_values),
    ):
        if rule.mode == DEVICE_FILTER_MODE_OFF:
            continue
        if not rule.values:
            if rule.mode == DEVICE_FILTER_MODE_INCLUDE:
                return False
            continue
        if not _rule_allows_values(rule, extractor(device_data)):
            return False
    return True


def _safe_device_from_api_data(device_data: dict[str, Any]) -> LiproDevice | None:
    """Build a device from API data, returning None when payload is malformed."""
    try:
        return LiproDevice.from_api_data(device_data)
    except (TypeError, ValueError, AttributeError):
        _LOGGER.debug("Skipping malformed device payload row")
        return None


def _has_valid_device_serial(device: LiproDevice) -> bool:
    """Return True when the device has a valid, non-empty serial."""
    if not isinstance(device.serial, str) or not device.serial.strip():
        _LOGGER.debug("Skipping device with invalid serial type/value")
        return False
    return True


def _safe_is_gateway(device: LiproDevice) -> bool | None:
    """Return gateway status; None when category payload is malformed."""
    try:
        return device.is_gateway
    except (TypeError, ValueError):
        _LOGGER.debug("Skipping device with malformed category payload")
        return None


def _safe_is_outlet(device: LiproDevice) -> bool:
    """Return whether device is an outlet, handling malformed categories."""
    try:
        return device.category == DeviceCategory.OUTLET
    except (TypeError, ValueError):
        _LOGGER.debug("Skipping outlet categorization for malformed device")
        return False


def build_fetched_device_snapshot(
    devices_data: list[dict[str, Any]],
    *,
    device_filter: Callable[[dict[str, Any]], bool] | None = None,
) -> FetchedDeviceSnapshot:
    """Build refreshed device indexes from API payload."""
    new_devices: dict[str, LiproDevice] = {}
    new_device_by_id: dict[str, LiproDevice] = {}
    new_iot_ids: list[str] = []
    new_group_ids: list[str] = []
    new_outlet_ids: list[str] = []
    new_cloud_serials: set[str] = set()

    for device_data in devices_data:
        device = _safe_device_from_api_data(device_data)
        if device is None:
            continue

        if not _has_valid_device_serial(device):
            continue

        is_gateway = _safe_is_gateway(device)
        if is_gateway is None:
            continue

        if is_gateway:
            _LOGGER.debug("Skipping gateway device: %s", device.name)
            continue

        new_cloud_serials.add(device.serial)
        if device_filter is not None and not device_filter(device_data):
            continue

        new_devices[device.serial] = device
        register_identity_alias(new_device_by_id, device.serial, device)

        if device.is_group:
            new_group_ids.append(device.serial)
            if _safe_is_outlet(device):
                new_outlet_ids.append(device.serial)
            continue

        if not device.has_valid_iot_id:
            _LOGGER.debug(
                "Device %s has unexpected IoT ID format: %s",
                device.name,
                device.serial,
            )
            continue
        new_iot_ids.append(device.iot_device_id)

        if _safe_is_outlet(device):
            new_outlet_ids.append(device.iot_device_id)

    return FetchedDeviceSnapshot(
        devices=new_devices,
        device_by_id=new_device_by_id,
        iot_ids=new_iot_ids,
        group_ids=new_group_ids,
        outlet_ids=new_outlet_ids,
        cloud_serials=new_cloud_serials,
    )


def plan_stale_device_reconciliation(
    *,
    previous_serials: set[str],
    current_serials: set[str],
    missing_cycles: dict[str, int],
    remove_threshold: int,
) -> StaleDeviceReconcilePlan:
    """Compute stale-device cycle counters and removable serials."""
    updated_missing_cycles = {
        serial: count
        for serial, count in missing_cycles.items()
        if serial not in current_serials
    }
    stale_serials = (previous_serials | set(updated_missing_cycles)) - current_serials

    removable: set[str] = set()
    for serial in stale_serials:
        miss_count = updated_missing_cycles.get(serial, 0) + 1
        updated_missing_cycles[serial] = miss_count
        if miss_count >= remove_threshold:
            removable.add(serial)

    return StaleDeviceReconcilePlan(
        missing_cycles=updated_missing_cycles,
        removable_serials=removable,
    )
