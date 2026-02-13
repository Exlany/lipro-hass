"""Core constants for Lipro API."""

from typing import Final

# API endpoints
SMART_HOME_API_URL: Final = "https://api-hilbert.lipro.com"
IOT_API_URL: Final = "https://api-mlink.lipro.com"

# Signing keys
SMART_HOME_SIGN_KEY: Final = "*Hilbert$@q9g"
IOT_SIGN_KEY: Final = "19ff9eb20f818bc45ab216d0d67f"

# Merchant code
MERCHANT_CODE: Final = "LP0002"

# API paths - Smart Home
PATH_LOGIN: Final = "/v1/user/token/login-by-password.do"
PATH_REFRESH_TOKEN: Final = "/v1/user/token/refresh.do"
PATH_FETCH_DEVICES: Final = "/v1/user/index.do"
PATH_GET_PRODUCT_CONFIGS: Final = "/v1/iot/product/index/list.do"

# API paths - IoT
PATH_SEND_COMMAND: Final = "/app/oauth/api/v1/user/control/device/command.do"
PATH_SEND_GROUP_COMMAND: Final = (
    "/app/oauth/api/v2/user/control/device/group/command.do"
)
PATH_QUERY_DEVICE_STATUS: Final = "/app/oauth/api/v1/user/query/devices/state.do"
PATH_QUERY_MESH_GROUP_STATUS: Final = (
    "/app/oauth/api/v2/user/query/devices/group/state.do"
)
PATH_QUERY_CONNECT_STATUS: Final = (
    "/app/oauth/api/v1/user/query/devices/connect-state.do"
)
PATH_QUERY_OUTLET_POWER: Final = "/app/oauth/api/v1/user/query/device/power-info.do"

# API paths - Timing Tasks
PATH_SCHEDULE_ADD: Final = (
    "/app/oauth/api/v1/user/control/device/schedule/addOrUpdate.do"
)
PATH_SCHEDULE_DELETE: Final = "/app/oauth/api/v1/user/control/device/schedule/delete.do"
PATH_SCHEDULE_GET: Final = "/app/oauth/api/v1/user/control/device/schedule/get.do"

# HTTP headers
HEADER_CONTENT_TYPE: Final = "Content-Type"
HEADER_CACHE_CONTROL: Final = "Cache-Control"
HEADER_USER_AGENT: Final = "User-Agent"
HEADER_ACCESS_TOKEN: Final = "i-access-token"
HEADER_MERCHANT_CODE: Final = "merchant-code"
HEADER_NONCE: Final = "nonce"
HEADER_SIGN: Final = "sign"

# User-Agent (matches Android app's OkHttp client)
USER_AGENT: Final = "okhttp/4.12.0"

# Content types
CONTENT_TYPE_FORM: Final = "application/x-www-form-urlencoded"
CONTENT_TYPE_JSON: Final = "application/json"

# Response codes
RESPONSE_SUCCESS: Final = 200
RESPONSE_SUCCESS_STR: Final = "0000"
RESPONSE_SUCCESS_CODES: Final = (200, "0000", "200")  # All known success code variants

# Error codes - verified in real API responses
ERROR_DEVICE_OFFLINE: Final = 140003  # Device not found / offline
ERROR_DEVICE_OFFLINE_STR: Final = "140003"
ERROR_NO_PERMISSION: Final = 140101  # No permission to view device
ERROR_NO_PERMISSION_STR: Final = "140101"
ERROR_AUTH_CODES: Final = (401, "401", 2001, 2002)  # Authentication errors

# Error codes - from API docs, not yet verified in real responses
# Refresh token expired
ERROR_REFRESH_TOKEN_EXPIRED: Final = (20002, 1202, "20002", "1202")

# Token expiry settings
# Note: API does not return expires_in, so we use conservative estimates
# accessToken: estimated 2 hours (7200 seconds)
# refreshToken: estimated 30 days
ACCESS_TOKEN_EXPIRY_SECONDS: Final = 7200  # 2 hours (conservative estimate)
TOKEN_REFRESH_BUFFER: Final = 300  # Refresh accessToken 5 minutes before expiry

# Adaptive adjustment for accessToken
# If 401 errors occur frequently, reduce the estimated expiry time
TOKEN_EXPIRY_MIN: Final = 1800  # Minimum: 30 minutes
TOKEN_EXPIRY_REDUCTION_FACTOR: Final = 0.5  # Reduce by 50% on 401

# Minimum interval between token refreshes to prevent duplicate refresh storms
TOKEN_REFRESH_DEDUP_WINDOW: Final = 5  # seconds

# Request timeout (seconds)
REQUEST_TIMEOUT: Final = 30

# Maximum Retry-After value (seconds) to prevent hanging on malicious/abnormal headers
MAX_RETRY_AFTER: Final = 60

# Maximum MQTT dedup cache entries before forced cleanup
MAX_MQTT_CACHE_SIZE: Final = 500

# Max devices per status query
MAX_DEVICES_PER_QUERY: Final = 100

# MQTT configuration (Aliyun MQTT)
MQTT_BROKER_HOST: Final = "post-cn-li93yvd5304.mqtt.aliyuncs.com"
MQTT_BROKER_PORT: Final = 8883
MQTT_INSTANCE_ID: Final = "post-cn-li93yvd5304"
MQTT_KEEP_ALIVE: Final = 60
MQTT_QOS: Final = 2  # EXACTLY_ONCE
MQTT_RECONNECT_MIN_DELAY: Final = 1  # seconds
MQTT_RECONNECT_MAX_DELAY: Final = 300  # 5 minutes (was 32s)
MQTT_RECONNECT_JITTER: Final = 0.2  # ±20% random jitter
MQTT_DISCONNECT_NOTIFY_THRESHOLD: Final = 300  # 5 minutes before notifying user

# MQTT credential decryption key (from libmqtt.so)
MQTT_AES_KEY: Final = "fprd#huy1n!&d8d6"

# MQTT topic format
MQTT_TOPIC_PREFIX: Final = "Topic_Device_State"

# API path for MQTT config
PATH_GET_MQTT_CONFIG: Final = (
    "/app/oauth/api/v2/user/control/device/get_aliyun_mqtt_config.do"
)
