"""Anonymous share payload models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import time
from typing import Any


@dataclass
class SharedError:
    """Represents one collected error (Worker API compatible)."""

    error_type: str
    message: str = ""
    endpoint: str = ""
    iot_name: str = ""
    device_type: str = ""
    timestamp: float = field(default_factory=time.time)
    count: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        message = self.message
        if self.count > 1:
            message = f"{message} (x{self.count})"
        return {
            "type": self.error_type,
            "message": message,
            "endpoint": self.endpoint,
            "iot_name": self.iot_name,
            "device_type": self.device_type,
            "timestamp": datetime.fromtimestamp(self.timestamp, tz=UTC).isoformat(),
        }


@dataclass
class SharedDevice:
    """Represents one collected device record (sanitized)."""

    physical_model: str | None
    iot_name: str
    device_type: int
    product_id: int | None
    is_group: bool
    category: str
    firmware_version: str | None
    property_keys: list[str]
    properties: dict[str, Any]  # Sanitized property values (preserves structure)
    min_color_temp_kelvin: int = 0
    max_color_temp_kelvin: int = 0
    has_gear_presets: bool = False
    gear_count: int = 0
    capabilities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        return {
            "physical_model": self.physical_model,
            "iot_name": self.iot_name,
            "device_type": self.device_type,
            "product_id": self.product_id,
            "is_group": self.is_group,
            "category": self.category,
            "firmware_version": self.firmware_version,
            "property_keys": self.property_keys,
            "properties": self.properties,
            "min_color_temp_kelvin": self.min_color_temp_kelvin,
            "max_color_temp_kelvin": self.max_color_temp_kelvin,
            "has_gear_presets": self.has_gear_presets,
            "gear_count": self.gear_count,
            "capabilities": self.capabilities,
        }


__all__ = ["SharedDevice", "SharedError"]
