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
DEFAULT_POWER_QUERY_INTERVAL: Final = 300
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

# Options - light.turn_on semantic behavior when adjusting brightness/color temp
CONF_LIGHT_TURN_ON_ON_ADJUST: Final = "light_turn_on_on_adjust"
DEFAULT_LIGHT_TURN_ON_ON_ADJUST: Final = True

# Options - room/area synchronization policy
# False (default): preserve user-customized HA areas and use cloud room as fallback.
# True: always force HA area to match cloud room assignment.
CONF_ROOM_AREA_SYNC_FORCE: Final = "room_area_sync_force"
DEFAULT_ROOM_AREA_SYNC_FORCE: Final = False

# Options - command delivery verify via query_command_result
# True (default): after command send, verify delivery result by msgSn.
# False: keep existing optimistic pushSuccess behavior.
CONF_COMMAND_RESULT_VERIFY: Final = "command_result_verify"
DEFAULT_COMMAND_RESULT_VERIFY: Final = True

# Options - device filtering (home/model/ssid/did)
CONF_DEVICE_FILTER_HOME_MODE: Final = "device_filter_home_mode"
CONF_DEVICE_FILTER_HOME_LIST: Final = "device_filter_home_list"
CONF_DEVICE_FILTER_MODEL_MODE: Final = "device_filter_model_mode"
CONF_DEVICE_FILTER_MODEL_LIST: Final = "device_filter_model_list"
CONF_DEVICE_FILTER_SSID_MODE: Final = "device_filter_ssid_mode"
CONF_DEVICE_FILTER_SSID_LIST: Final = "device_filter_ssid_list"
CONF_DEVICE_FILTER_DID_MODE: Final = "device_filter_did_mode"
CONF_DEVICE_FILTER_DID_LIST: Final = "device_filter_did_list"
DEVICE_FILTER_MODE_OFF: Final = "off"
DEVICE_FILTER_MODE_INCLUDE: Final = "include"
DEVICE_FILTER_MODE_EXCLUDE: Final = "exclude"
DEFAULT_DEVICE_FILTER_MODE: Final = DEVICE_FILTER_MODE_OFF
MAX_DEVICE_FILTER_LIST_CHARS: Final = 4096
MAX_DEVICE_FILTER_LIST_ITEMS: Final = 200

# Anonymous share options (device info sharing)
CONF_ANONYMOUS_SHARE_ENABLED: Final = "anonymous_share_enabled"
CONF_ANONYMOUS_SHARE_ERRORS: Final = "anonymous_share_errors"
DEFAULT_ANONYMOUS_SHARE_ENABLED: Final = False
DEFAULT_ANONYMOUS_SHARE_ERRORS: Final = True

# Key for storing password MD5 hash instead of plain password
# This improves security as the API accepts MD5 hash directly
CONF_PASSWORD_HASH: Final = "password_hash"

# Whether to persist the password hash locally (config entry data).
# When disabled, the integration can still use access/refresh tokens, but may
# require manual re-authentication if refresh tokens expire.
CONF_REMEMBER_PASSWORD_HASH: Final = "remember_password_hash"
DEFAULT_REMEMBER_PASSWORD_HASH: Final = False
