"""Sensor platform for Lipro integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, cast

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfEnergy,
    UnitOfPower,
)

from .helpers.platform import (
    add_entry_entities,
    build_device_entities_from_rules,
    create_device_entities,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.update_coordinator import (
        CoordinatorEntity,
        DataUpdateCoordinator,
    )

    from . import LiproConfigEntry
    from .core.capability import CapabilitySnapshot
    from .core.device import LiproDevice
    from .runtime_types import LiproRuntimeCoordinator

    class _LiproEntityBase(CoordinatorEntity[DataUpdateCoordinator[dict[str, object]]]):
        def __init__(
            self,
            coordinator: LiproRuntimeCoordinator,
            device: LiproDevice,
            entity_suffix: str = "",
        ) -> None: ...

        @property
        def device(self) -> LiproDevice: ...

        @property
        def capabilities(self) -> CapabilitySnapshot: ...

        async def async_change_state(
            self,
            properties: Mapping[str, object],
            *,
            optimistic_state: Mapping[str, object] | None = None,
            debounced: bool = False,
        ) -> bool | None: ...

else:
    _LiproEntityBase = cast(
        type[object],
        __import__(
            "custom_components.lipro.entities.base",
            fromlist=["LiproEntity"],
        ).LiproEntity,
    )

# No parallel update limit needed for read-only sensors using coordinator
PARALLEL_UPDATES = 0

# WiFi signal strength thresholds (dBm) for icon selection
_WIFI_RSSI_EXCELLENT: Final = -50
_WIFI_RSSI_GOOD: Final = -60
_WIFI_RSSI_FAIR: Final = -70
_WIFI_RSSI_WEAK: Final = -80


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro sensors."""
    add_entry_entities(
        entry,
        async_add_entities,
        entity_builder=lambda coordinator: create_device_entities(
            coordinator,
            _build_device_sensors,
        ),
    )


def _build_device_sensors(
    coordinator: LiproRuntimeCoordinator,
    device: LiproDevice,
) -> list[SensorEntity]:
    """Build all sensor entities for one device."""
    return build_device_entities_from_rules(
        coordinator,
        device,
        rules=(
            (
                lambda d: d.capabilities.is_outlet,
                (
                    lambda current_coordinator, current_device: LiproOutletPowerSensor(
                        current_coordinator,
                        current_device,
                    ),
                    lambda current_coordinator, current_device: LiproOutletEnergySensor(
                        current_coordinator,
                        current_device,
                    ),
                ),
            ),
            (
                lambda d: d.has_battery,
                (
                    lambda current_coordinator, current_device: LiproBatterySensor(
                        current_coordinator,
                        current_device,
                    ),
                ),
            ),
            (
                lambda d: d.wifi_rssi is not None,
                (
                    lambda current_coordinator, current_device: LiproWiFiSignalSensor(
                        current_coordinator,
                        current_device,
                    ),
                ),
            ),
        ),
    )


class LiproSensor(_LiproEntityBase, SensorEntity):
    """Base class for Lipro sensors."""

    @staticmethod
    def _coerce_float(value: object) -> float | None:
        """Convert one scalar-like payload value into float safely."""
        if value is None:
            return None
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                return None
            try:
                return float(normalized)
            except ValueError:
                return None
        return None

    def _get_power_info(self) -> dict[str, object] | None:
        """Get power info from the device's formal outlet-power primitive."""
        return self.device.outlet_power_info


class LiproOutletPowerSensor(LiproSensor):
    """Sensor for outlet current power consumption."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_suggested_display_precision = 1
    _attr_translation_key = "power"
    _entity_suffix = "power"

    @property
    def native_value(self) -> float | None:
        """Return the current power in watts."""
        power_info = self._get_power_info()
        if power_info is None:
            return None
        return self._coerce_float(power_info.get("nowPower"))


class LiproOutletEnergySensor(LiproSensor):
    """Sensor for outlet total energy consumption.

    Uses TOTAL (not TOTAL_INCREASING) because the value is a sum of daily
    records from a sliding window (up to 90 days). When old days fall off,
    the total decreases — which TOTAL_INCREASING would misinterpret as a
    meter reset.
    """

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 2
    _attr_translation_key = "energy"
    _entity_suffix = "energy"

    @property
    def native_value(self) -> float | None:
        """Return the total energy consumption in kWh."""
        power_info = self._get_power_info()
        if power_info is None:
            return None

        # Sum up all energy values from energyList
        # API returns "v" for energy value (kWh), "t" for date (YYYYMMDD)
        energy_list = power_info.get("energyList")
        if not isinstance(energy_list, list) or not energy_list:
            return None

        return sum(
            self._safe_energy_value(item)
            for item in energy_list
            if isinstance(item, dict)
        )

    @staticmethod
    def _safe_energy_value(item: dict[str, object]) -> float:
        """Extract energy value from an energy list item, returning 0.0 on failure."""
        value = item.get("v")
        if value is None:
            return 0.0
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                return 0.0
            try:
                return float(normalized)
            except ValueError:
                return 0.0
        return 0.0


class LiproBatterySensor(LiproSensor):
    """Sensor for device battery level.

    Available on battery-powered devices like Bedside Light (床头灯).
    """

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_translation_key = "battery"
    _entity_suffix = "battery"

    @property
    def native_value(self) -> int | None:
        """Return the battery level percentage."""
        return self.device.state.battery_level

    @property
    def icon(self) -> str | None:
        """Return charging icon when device is charging.

        Programmatic override: icons.json cannot express cross-attribute
        conditions (charging state is a separate device property, not the
        entity's own state value).
        """
        if self.device.state.is_charging:
            return "mdi:battery-charging"
        return None  # Let HA handle battery level icons via device_class

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes."""
        return {
            "charging": self.device.state.is_charging,
        }


class LiproWiFiSignalSensor(LiproSensor):
    """Sensor for device WiFi signal strength (RSSI).

    Available on WiFi-connected devices. Shows signal strength in dBm.
    """

    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _attr_translation_key = "wifi_signal"
    _entity_suffix = "wifi_signal"

    @property
    def native_value(self) -> int | None:
        """Return the WiFi signal strength in dBm."""
        return self.device.network_info.wifi_rssi

    @property
    def icon(self) -> str:
        """Return the icon based on signal strength.

        Programmatic override: icons.json cannot express numeric-range
        thresholds on the entity's native value (dBm RSSI).
        """
        rssi = self.device.network_info.wifi_rssi
        if rssi is None:
            return "mdi:wifi-off"
        if rssi >= _WIFI_RSSI_EXCELLENT:
            return "mdi:wifi-strength-4"
        if rssi >= _WIFI_RSSI_GOOD:
            return "mdi:wifi-strength-3"
        if rssi >= _WIFI_RSSI_FAIR:
            return "mdi:wifi-strength-2"
        if rssi >= _WIFI_RSSI_WEAK:
            return "mdi:wifi-strength-1"
        return "mdi:wifi-strength-alert-outline"

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes."""
        attrs: dict[str, object] = {}
        if self.device.network_info.net_type:
            attrs["network_type"] = self.device.network_info.net_type
        return attrs
