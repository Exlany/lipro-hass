"""Configuration constants for the Lipro integration."""

from typing import Final

# Configuration keys
CONF_PHONE: Final = "phone"
CONF_PHONE_ID: Final = "phone_id"

# Config entry data keys (stored in entry.data)
CONF_ACCESS_TOKEN: Final = "access_token"
CONF_REFRESH_TOKEN: Final = "refresh_token"
CONF_USER_ID: Final = "user_id"
CONF_BIZ_ID: Final = "biz_id"
CONF_EXPIRES_AT: Final = "expires_at"

# Options - Polling interval
CONF_SCAN_INTERVAL: Final = "scan_interval"
DEFAULT_SCAN_INTERVAL: Final = 30
MIN_SCAN_INTERVAL: Final = 10
MAX_SCAN_INTERVAL: Final = 300

# Options - MQTT real-time updates
CONF_MQTT_ENABLED: Final = "mqtt_enabled"
DEFAULT_MQTT_ENABLED: Final = True

# Options - Power monitoring for outlets
CONF_ENABLE_POWER_MONITORING: Final = "enable_power_monitoring"
DEFAULT_ENABLE_POWER_MONITORING: Final = True

# Options - Power query interval (independent of scan_interval)
CONF_POWER_QUERY_INTERVAL: Final = "power_query_interval"
DEFAULT_POWER_QUERY_INTERVAL: Final = 60
MIN_POWER_QUERY_INTERVAL: Final = 30
MAX_POWER_QUERY_INTERVAL: Final = 300

# Options - API request timeout
CONF_REQUEST_TIMEOUT: Final = "request_timeout"
DEFAULT_REQUEST_TIMEOUT: Final = 30
MIN_REQUEST_TIMEOUT: Final = 10
MAX_REQUEST_TIMEOUT: Final = 60

# Options - Debug mode
CONF_DEBUG_MODE: Final = "debug_mode"
DEFAULT_DEBUG_MODE: Final = False

# Anonymous share options (device info sharing)
CONF_ANONYMOUS_SHARE_ENABLED: Final = "anonymous_share_enabled"
CONF_ANONYMOUS_SHARE_ERRORS: Final = "anonymous_share_errors"
DEFAULT_ANONYMOUS_SHARE_ENABLED: Final = False
DEFAULT_ANONYMOUS_SHARE_ERRORS: Final = True
