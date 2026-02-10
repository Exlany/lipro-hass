"""Configuration constants for the Lipro integration."""

from typing import Final

# Configuration keys
CONF_PHONE: Final = "phone"
CONF_PASSWORD: Final = "password"
CONF_PHONE_ID: Final = "phone_id"

# Options
CONF_SCAN_INTERVAL: Final = "scan_interval"
DEFAULT_SCAN_INTERVAL: Final = 30
MIN_SCAN_INTERVAL: Final = 10
MAX_SCAN_INTERVAL: Final = 300

# Anonymous share options (device info sharing)
CONF_ANONYMOUS_SHARE_ENABLED: Final = "anonymous_share_enabled"
CONF_ANONYMOUS_SHARE_ERRORS: Final = "anonymous_share_errors"
DEFAULT_ANONYMOUS_SHARE_ENABLED: Final = False
DEFAULT_ANONYMOUS_SHARE_ERRORS: Final = True
