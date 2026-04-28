"""Constants for the anonymous share worker integration."""

from __future__ import annotations

from typing import Final

# Anonymous share server endpoints
#
# NOTE: `X-API-Key` is a *public* client identifier used for coarse attribution
# and anti-abuse shaping on the Worker side (not a secret).
SHARE_BASE_URL: Final = "https://lipro-share.lany.me"
SHARE_REPORT_URL: Final = f"{SHARE_BASE_URL}/api/report"
SHARE_TOKEN_REFRESH_URL: Final = f"{SHARE_BASE_URL}/api/token/refresh"
SHARE_API_KEY: Final = "lipro-ha-share-2026"

# Maximum items to keep in memory before forcing upload
MAX_PENDING_ERRORS: Final = 50
MAX_PENDING_DEVICES: Final = 20

# Minimum interval between uploads (seconds)
MIN_UPLOAD_INTERVAL: Final = 3600  # 1 hour

# Auto-upload interval: force upload if no upload in 24 hours
AUTO_UPLOAD_INTERVAL: Final = MIN_UPLOAD_INTERVAL * 24  # 24 hours
