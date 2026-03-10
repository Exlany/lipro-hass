"""Base constants for the Lipro integration."""

from __future__ import annotations

from typing import Final

# Domain
DOMAIN: Final = "lipro"

# Manufacturer name (used in device_info)
MANUFACTURER: Final = "Lipro"

# Lipro/Meizu manufacturer ID prefix for IoT device IDs (939 in decimal)
# IoT device ID format: IOT_DEVICE_ID_PREFIX + 12 hex chars (BLE MAC without colons)
IOT_DEVICE_ID_PREFIX: Final = "03ab"

# Integration version (should match manifest.json)
VERSION: Final = "1.0.0"

# API library version - increment when API changes are made
# This helps track compatibility with Lipro cloud API
API_VERSION: Final = "1.0.0"

# API version info (Lipro app version we're emulating)
APP_VERSION_NAME: Final = "2.24.3"
APP_VERSION_CODE: Final = 20240003
