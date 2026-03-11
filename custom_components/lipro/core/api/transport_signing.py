"""Request signing utilities for Lipro API."""

from __future__ import annotations

import hashlib
import time

from ...const.api import IOT_SIGN_KEY, MERCHANT_CODE, SMART_HOME_SIGN_KEY


class TransportSigning:
    """Handles request signing for Smart Home and IoT APIs."""

    def __init__(self, phone_id: str) -> None:
        """Initialize signing utilities.

        Args:
            phone_id: Device identifier for API signing.

        """
        self._phone_id = phone_id

    def smart_home_sign(self) -> str:
        """Generate Smart Home API signature.

        Returns:
            MD5 signature string.

        """
        sign_data = f"{self._phone_id}{SMART_HOME_SIGN_KEY}"
        return hashlib.md5(sign_data.encode("utf-8"), usedforsecurity=False).hexdigest()

    def iot_sign(self, access_token: str, nonce: int, body: str) -> str:
        """Generate IoT API signature.

        Args:
            access_token: Current access token.
            nonce: Timestamp in milliseconds.
            body: Request body JSON string.

        Returns:
            MD5 signature string.

        Note:
            Per API docs, body should be trimmed before signing.
            json.dumps() output has no leading/trailing whitespace,
            but we call strip() explicitly for safety.

        """
        trimmed_body = body.strip() if body else ""
        sign_data = (
            f"{access_token}{nonce}{MERCHANT_CODE}{trimmed_body}{IOT_SIGN_KEY}"
        )
        return hashlib.md5(sign_data.encode("utf-8"), usedforsecurity=False).hexdigest()

    @staticmethod
    def get_timestamp_ms() -> int:
        """Get current timestamp in milliseconds.

        Returns:
            Current timestamp in milliseconds.

        """
        return int(time.time() * 1000)
