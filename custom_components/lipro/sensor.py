"""Sensor platform for Lipro integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

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

from .const.categories import DeviceCategory
from .entities.base import LiproEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry

# No parallel update limit needed for read-only sensors using coordinator
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro sensors."""
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = []

    for device in coordinator.devices.values():
        # Add power sensor for outlets
        if device.category == DeviceCategory.OUTLET:
            entities.append(LiproOutletPowerSensor(coordinator, device))
            entities.append(LiproOutletEnergySensor(coordinator, device))

        # Add battery sensor for devices with battery (e.g., Bedside Light)
        if device.has_battery:
            entities.append(LiproBatterySensor(coordinator, device))

        # Add WiFi signal strength sensor for devices with wifi_rssi
        if device.wifi_rssi is not None:
            entities.append(LiproWifiSignalSensor(coordinator, device))

    async_add_entities(entities)


class LiproSensor(LiproEntity, SensorEntity):
    """Base class for Lipro sensors."""

    def _get_power_info(self) -> dict[str, Any] | None:
        """Get power info from device extra_data.

        Power info is stored by coordinator during outlet power queries.
        """
        return self.device.extra_data.get("power_info")


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
        return power_info.get("nowPower")


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
        energy_list = power_info.get("energyList", [])
        if not energy_list:
            return None

        total_energy = 0.0
        for item in energy_list:
            # Skip non-dict items
            if not isinstance(item, dict):
                continue
            # API returns "v" for energy value (kWh), "t" for date (YYYYMMDD)
            energy_value = item.get("v")
            if energy_value is not None:
                try:
                    total_energy += float(energy_value)
                except (ValueError, TypeError):
                    continue

        return total_energy


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
        return self.device.battery_level

    @property
    def icon(self) -> str | None:
        """Return charging icon when device is charging."""
        if self.device.is_charging:
            return "mdi:battery-charging"
        return None  # Let HA handle battery level icons via device_class

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "charging": self.device.is_charging,
        }


class LiproWifiSignalSensor(LiproSensor):
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
        return self.device.wifi_rssi

    @property
    def icon(self) -> str:
        """Return the icon based on signal strength."""
        rssi = self.device.wifi_rssi
        if rssi is None:
            return "mdi:wifi-off"
        if rssi >= -50:
            return "mdi:wifi-strength-4"
        if rssi >= -60:
            return "mdi:wifi-strength-3"
        if rssi >= -70:
            return "mdi:wifi-strength-2"
        if rssi >= -80:
            return "mdi:wifi-strength-1"
        return "mdi:wifi-strength-alert-outline"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs: dict[str, Any] = {}
        if self.device.net_type:
            attrs["network_type"] = self.device.net_type
        return attrs
