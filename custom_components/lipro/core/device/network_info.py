"""Structured network and diagnostics snapshot for one Lipro device."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ...const.properties import (
    PROP_BLE_MAC,
    PROP_IP,
    PROP_LATEST_SYNC_TIMESTAMP,
    PROP_MAC,
    PROP_MESH_ADDRESS,
    PROP_MESH_GATEWAY,
    PROP_MESH_TYPE,
    PROP_NET_TYPE,
    PROP_VERSION,
    PROP_WIFI_RSSI,
    PROP_WIFI_SSID,
)
from ..utils.coerce import coerce_boollike


@dataclass(frozen=True, slots=True)
class DeviceNetworkInfo:
    """Network and diagnostics fields derived from normalized device properties."""

    ip_address: str | None = None
    wifi_ssid: str | None = None
    wifi_rssi: int | None = None
    net_type: str | None = None
    mac_address: str | None = None
    firmware_version: str | None = None
    latest_sync_timestamp: int | None = None
    mesh_address: int | None = None
    mesh_type: int | None = None
    is_mesh_gateway: bool = False
    ble_mac: str | None = None

    @classmethod
    def from_properties(cls, properties: Mapping[str, object]) -> DeviceNetworkInfo:
        """Build network info from normalized device properties."""
        return cls(
            ip_address=_coerce_optional_str(properties.get(PROP_IP)),
            wifi_ssid=_coerce_optional_str(properties.get(PROP_WIFI_SSID)),
            wifi_rssi=_coerce_optional_int(properties.get(PROP_WIFI_RSSI)),
            net_type=_coerce_optional_str(properties.get(PROP_NET_TYPE)),
            mac_address=_coerce_optional_str(properties.get(PROP_MAC)),
            firmware_version=_coerce_optional_str(properties.get(PROP_VERSION)),
            latest_sync_timestamp=_coerce_optional_int(
                properties.get(PROP_LATEST_SYNC_TIMESTAMP)
            ),
            mesh_address=_coerce_optional_int(properties.get(PROP_MESH_ADDRESS)),
            mesh_type=_coerce_optional_int(properties.get(PROP_MESH_TYPE)),
            is_mesh_gateway=coerce_boollike(
                properties.get(PROP_MESH_GATEWAY), context="DeviceNetworkInfo"
            ),
            ble_mac=_coerce_optional_str(properties.get(PROP_BLE_MAC)),
        )

    @classmethod
    def from_diagnostics_data(
        cls, diagnostics: Mapping[str, object]
    ) -> DeviceNetworkInfo:
        """Build network info from diagnostics payloads."""
        return cls.from_properties(diagnostics)

    @property
    def connection_quality(self) -> str:
        """Return a coarse connection quality label from RSSI."""
        if self.wifi_rssi is None:
            return "unknown"
        if self.wifi_rssi >= -60:
            return "excellent"
        if self.wifi_rssi >= -70:
            return "good"
        if self.wifi_rssi >= -80:
            return "fair"
        return "poor"


def _coerce_optional_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        normalized = value.strip()
        if normalized.lstrip("-").isdigit():
            return int(normalized)
    return None


def _coerce_optional_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


__all__ = ["DeviceNetworkInfo"]
